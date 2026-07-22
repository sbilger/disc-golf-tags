/* Discinsanity — shared accounts layer.
   DEMO auth: members + sessions live in localStorage. NOT real security.
   Swap these functions for Supabase Auth in Phase 1 (signUp/signIn/signOut/current
   keep the same shape, so callers don't change). See HUB-PLAN.md / TODO.md. */
(function (g) {
  const MK = 'discinsanity_members', SK = 'discinsanity_session';
  const ADMIN_CODE = 'nhNuGvSoCzbU';           // entering this on sign-up/in grants admin (Jeff). CHANGE.
  const read = () => { try { return JSON.parse(localStorage.getItem(MK) || '[]'); } catch (e) { return []; } };
  const write = (m) => localStorage.setItem(MK, JSON.stringify(m));
  const hash = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return 'h' + (h >>> 0); };
  const norm = (e) => (e || '').trim().toLowerCase();
  const initials = (n) => (n || '?').split(/\s+/).map(x => x[0]).join('').slice(0, 2).toUpperCase();

  const DI = {
    ADMIN_CODE,
    members: read,
    current() { const id = localStorage.getItem(SK); return id ? read().find(m => m.id === id) || null : null; },
    isAdmin() { const c = this.current(); return !!c && (c.role === 'admin' || c.role === 'organizer'); },
    initials,
    signUp({ name, email, password, pdga, division, code }) {
      name = (name || '').trim(); email = norm(email);
      if (!name) throw new Error('Name required');
      if (!email || !email.includes('@')) throw new Error('Valid email required');
      if ((password || '').length < 4) throw new Error('Password must be 4+ characters');
      const m = read();
      if (m.find(x => norm(x.email) === email)) throw new Error('That email already has an account');
      const role = (code && code.trim() === ADMIN_CODE) ? 'admin' : 'member';
      const member = { id: 'm' + Date.now().toString(36) + Math.floor(Math.random() * 999),
        name, email, pwh: hash(password), pdga: (pdga || '').replace(/\D/g, ''), division: division || '', role,
        created: new Date().toISOString().slice(0, 10) };
      m.push(member); write(m); localStorage.setItem(SK, member.id); return member;
    },
    signIn(email, password) {
      email = norm(email); const member = read().find(x => norm(x.email) === email);
      if (!member || member.pwh !== hash(password || '')) throw new Error('Wrong email or password');
      localStorage.setItem(SK, member.id); return member;
    },
    signOut() { localStorage.removeItem(SK); },
    update(patch) {
      const m = read(); const i = m.findIndex(x => x.id === localStorage.getItem(SK));
      if (i < 0) return null;
      if (patch.code !== undefined) { if (patch.code.trim() === ADMIN_CODE) m[i].role = 'admin'; delete patch.code; }
      if (patch.pdga !== undefined) patch.pdga = (patch.pdga || '').replace(/\D/g, '');
      Object.assign(m[i], patch); write(m); return m[i];
    },
    /* tiny seeded demo member so the login screen has something to show */
    seedDemo() {
      const m = read();
      if (!m.find(x => norm(x.email) === 'jeff@discinsanity.com')) {
        m.push({ id: 'm_jeff', name: 'Jeff Cope', email: 'jeff@discinsanity.com', pwh: hash('discinsanity'),
          pdga: '114217', division: 'MA1', role: 'admin', created: '2026-06-01' });
        write(m);
      }
    }
  };
  DI.seedDemo();
  g.DI = DI;
})(window);
