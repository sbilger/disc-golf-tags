/* Discinsanity — accounts layer, backed by REAL Supabase Auth (email/password + Google/
   Apple/Facebook OAuth once Sean registers each provider — see docs/TODO-SEAN.md).

   Same DI shape as the old local/demo version (current/isAdmin/initials/signUp/signIn/
   signOut/update/members) so NO CALLER in any other file needs to change — only this
   file's internals swapped from localStorage/hand-rolled hash to real Supabase Auth + a
   `members` table (row auto-created by a DB trigger on auth.users insert, see
   supabase-auth-schema.sql).

   IMPORTANT — async boot: DI.current()/isAdmin()/members() are SYNCHRONOUS reads of a
   cache populated by the async DI.init(). Every page's boot sequence must
   `await DI.init()` before any of those synchronous calls run (same pattern already used
   for `await load()` everywhere). Requires the supabase-js CDN script loaded BEFORE this
   file: <script src="https://unpkg.com/@supabase/supabase-js@2"></script>

   Admin code is NOT in this file (unlike the old ADMIN_CODE constant) — it lives
   server-side in Postgres (app_secrets table) and is only checked inside the claim_admin()
   RPC function. See supabase-auth-schema.sql. */
(function (g) {
  const SUPA_URL = 'https://ohvhhcpmohztmlossbjv.supabase.co';
  const SUPA_KEY = 'sb_publishable_Id_1aKGpo0ivVPKGN9bHPA_IFrPbCXX';

  let supa = null;
  let _current = null;       // cached members row for the signed-in user, or null
  let _membersCache = [];    // cached snapshot of all members (for name/email lookups elsewhere)
  let _listenersSetup = false;

  function client() {
    if (!supa) {
      if (!g.supabase) throw new Error('supabase-js not loaded — add the CDN <script> before account.js');
      supa = g.supabase.createClient(SUPA_URL, SUPA_KEY);
    }
    return supa;
  }

  async function accessToken() {
    const { data: { session } } = await client().auth.getSession();
    return session ? session.access_token : SUPA_KEY;
  }

  async function fetchMemberRow(userId) {
    const token = await accessToken();
    const r = await fetch(`${SUPA_URL}/rest/v1/members?id=eq.${userId}&select=*`, {
      headers: { apikey: SUPA_KEY, Authorization: `Bearer ${token}` },
    });
    if (!r.ok) return null;
    const rows = await r.json();
    return rows[0] || null;
  }

  async function fetchAllMembers() {
    try {
      const r = await fetch(`${SUPA_URL}/rest/v1/members?select=id,name,email,pdga,rating,division,league_name,has_card,role`, {
        headers: { apikey: SUPA_KEY, Authorization: `Bearer ${SUPA_KEY}` },
      });
      if (!r.ok) return [];
      const rows = await r.json();
      // normalize to the shape older callers expect (leagueName/hasCard, camelCase)
      return rows.map(m => ({ ...m, leagueName: m.league_name, hasCard: m.has_card }));
    } catch (e) { return []; }
  }

  async function refreshCurrent() {
    const { data: { session } } = await client().auth.getSession();
    if (!session) { _current = null; return; }
    const row = await fetchMemberRow(session.user.id);
    _current = row
      ? { ...row, leagueName: row.league_name, hasCard: row.has_card, created: (row.created_at || '').slice(0, 10) }
      : { id: session.user.id, email: session.user.email, name: session.user.email, role: 'member', created: '' };
  }

  const initials = (n) => (n || '?').split(/\s+/).map(x => x[0]).join('').slice(0, 2).toUpperCase();

  const DI = {
    /* Call once at the top of every page's boot, before any current()/isAdmin() read:
       await DI.init(); */
    async init() {
      await refreshCurrent();
      _membersCache = await fetchAllMembers();
      if (!_listenersSetup) {
        _listenersSetup = true;
        client().auth.onAuthStateChange(async () => {
          await refreshCurrent();
          _membersCache = await fetchAllMembers();
        });
      }
    },
    current() { return _current; },
    members() { return _membersCache; },
    isAdmin() { return !!(_current && (_current.role === 'admin' || _current.role === 'organizer')); },
    initials,

    /* Throws Error('CONFIRM_EMAIL') if Supabase requires email confirmation before sign-in
       (project setting, Authentication -> Providers -> Email). Caller should show a
       "check your email" message for that specific error, not a generic failure. */
    async signUp({ name, email, password }) {
      name = (name || '').trim();
      if (!name) throw new Error('Name required');
      if (!email || !email.includes('@')) throw new Error('Valid email required');
      if ((password || '').length < 6) throw new Error('Password must be 6+ characters (Supabase minimum)');
      const { data, error } = await client().auth.signUp({
        email, password, options: { data: { name } },
      });
      if (error) throw new Error(error.message);
      if (!data.session) throw new Error('CONFIRM_EMAIL');
      await refreshCurrent();
      _membersCache = await fetchAllMembers();
      return _current;
    },
    async signIn(email, password) {
      const { error } = await client().auth.signInWithPassword({ email, password });
      if (error) throw new Error(error.message);
      await refreshCurrent();
      _membersCache = await fetchAllMembers();
      return _current;
    },
    /* provider: 'google' | 'apple' | 'facebook'. Redirects the whole page to the provider
       and back — Supabase's client auto-detects the returned session on load (default
       detectSessionInUrl: true), no extra handling needed here. Each provider only works
       once Sean has registered it in Supabase's dashboard (Authentication -> Providers) —
       see docs/TODO-SEAN.md. Clicking before that just shows Supabase's own error page. */
    async signInWithProvider(provider) {
      await client().auth.signInWithOAuth({ provider, options: { redirectTo: g.location.href } });
    },
    async signOut() {
      await client().auth.signOut();
      _current = null;
    },
    /* patch may include `code` (admin claim code) alongside/instead of profile fields.
       Profile fields go straight to the members row (RLS: users can only update their own
       row). `code` goes through the claim_admin() RPC, which is the ONLY path that can set
       role='admin' — a direct PATCH attempting to change `role` is silently reverted by
       the protect_role_column trigger server-side. */
    async update(patch) {
      if (!_current) return null;
      const clean = {};
      const map = { name: 'name', pdga: 'pdga', rating: 'rating', division: 'division', leagueName: 'league_name', hasCard: 'has_card' };
      Object.keys(patch).forEach(k => { if (k !== 'code' && map[k]) clean[map[k]] = patch[k]; });

      const token = await accessToken();
      if (Object.keys(clean).length) {
        await fetch(`${SUPA_URL}/rest/v1/members?id=eq.${_current.id}`, {
          method: 'PATCH',
          headers: { apikey: SUPA_KEY, Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
          body: JSON.stringify(clean),
        });
      }
      if (patch.code !== undefined && patch.code.trim()) {
        await fetch(`${SUPA_URL}/rest/v1/rpc/claim_admin`, {
          method: 'POST',
          headers: { apikey: SUPA_KEY, Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ p_code: patch.code.trim() }),
        });
      }
      await refreshCurrent();
      _membersCache = await fetchAllMembers();
      return _current;
    },
  };

  g.DI = DI;
})(window);
