/* Discinsanity — shared suite session.
   ONE unlock + ONE organizer state for every module (tags/doubles/events/leaderboards),
   layered on account.js (DI): a signed-in member opens the whole suite, an admin
   (Jeff) is organizer everywhere. Tokens roll daily, so access auto-expires.
   ⚠ Client-side gate only — real security arrives with Supabase RLS (see BACKEND.md).
   Load AFTER account.js. */
(function (g) {
  const ACCESS_KEY = 'discinsanity_access_v1';  // suite-wide date unlock
  const ORG_KEY    = 'discinsanity_org_v1';     // suite-wide organizer unlock
  const LEGACY_KEYS = ['di_access', 'di_dbl_access', 'di_evt_access', 'di_lb_access'];

  const token = () => {
    const t = new Date();
    return `${t.getFullYear()}${String(t.getMonth() + 1).padStart(2, '0')}${String(t.getDate()).padStart(2, '0')}`;
  };
  const digits = s => (s || '').replace(/\D/g, '');

  const DIS = {
    token,
    /* does this string match today's date (yyyymmdd or mmddyyyy)? */
    checkDate(v) {
      const d = digits(v); const t = new Date();
      const y = t.getFullYear(), m = String(t.getMonth() + 1).padStart(2, '0'), da = String(t.getDate()).padStart(2, '0');
      return d === `${y}${m}${da}` || d === `${m}${da}${y}`;
    },
    /* suite unlocked? signed-in member ⇒ yes; else today's token (migrates old per-module keys) */
    hasAccess() {
      if (g.DI && g.DI.current()) return true;
      if (localStorage.getItem(ACCESS_KEY) === token()) return true;
      for (const k of LEGACY_KEYS) {
        if (localStorage.getItem(k) === token()) { this.grantAccess(); return true; }
      }
      return false;
    },
    grantAccess() { localStorage.setItem(ACCESS_KEY, token()); },
    /* organizer everywhere? admin account ⇒ yes; else today's organizer token */
    isOrg() { return !!(g.DI && g.DI.isAdmin()) || localStorage.getItem(ORG_KEY) === token(); },
    grantOrg() { localStorage.setItem(ORG_KEY, token()); },
    dropOrg() { localStorage.removeItem(ORG_KEY); }
  };
  g.DIS = DIS;
})(window);
