/* Discinsanity — shared suite session.
   ONE organizer state for every module (tags/doubles/events/leaderboards), layered on
   account.js (DI): an admin account (Jeff) is organizer everywhere. The organizer token
   rolls daily, so it auto-expires.
   Date-verification gate REMOVED 2026-07-03 (Sean's call) — modules are open, read-only
   by default; the 🔑 organizer code gates editing.
   ⚠ Client-side gate only — real security arrives with Supabase RLS (see BACKEND.md).
   Load AFTER account.js. */
(function (g) {
  const ORG_KEY = 'discinsanity_org_v1';     // suite-wide organizer unlock

  const token = () => {
    const t = new Date();
    return `${t.getFullYear()}${String(t.getMonth() + 1).padStart(2, '0')}${String(t.getDate()).padStart(2, '0')}`;
  };

  // housekeeping: clear tokens left behind by the retired date-gate
  ['di_access', 'di_dbl_access', 'di_evt_access', 'di_lb_access', 'discinsanity_access_v1']
    .forEach(k => { try { localStorage.removeItem(k); } catch (e) {} });

  const DIS = {
    token,
    /* organizer everywhere? admin account ⇒ yes; else today's organizer token */
    isOrg() { return !!(g.DI && g.DI.isAdmin()) || localStorage.getItem(ORG_KEY) === token(); },
    grantOrg() { localStorage.setItem(ORG_KEY, token()); },
    dropOrg() { localStorage.removeItem(ORG_KEY); }
  };
  g.DIS = DIS;
})(window);
