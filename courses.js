/* Discinsanity — shared course database (Lehigh Valley), UDisc-style scoring support.
   Holes + par per course/layout so scores display relative to par (E / -3 / +2) like UDisc.
   NOTE: UDisc has no public API and blocks scraping (docs/RESEARCH-udisc-data.md), so this is
   OUR editable database: sensible defaults seeded below, organizer corrects holes/par in-app
   (✎ in the Doubles course picker). Overrides + custom courses persist locally
   (`discinsanity_courses_v1`) and ride along to Supabase later.
   Load AFTER account.js/suite.js. Used by Tags (index.html) + Doubles. */
(function (g) {
  const KEY = 'discinsanity_courses_v1';

  /* Defaults: par 54 / 18 holes is the standard assumption — EDIT in-app if a layout differs. */
  const DEFAULTS = [
    { course: 'South Mountain',          layout: 'White Tee', holes: 18, par: 54 },
    { course: 'South Mountain',          layout: 'Blue Tee',  holes: 18, par: 54 },
    { course: 'Jordan Creek',            layout: 'Short',     holes: 18, par: 54 },
    { course: 'Jordan Creek',            layout: 'Long',      holes: 18, par: 54 },
    { course: 'Little Gap',              layout: 'Main',      holes: 18, par: 54 },
    { course: 'Trexler Nature Preserve', layout: 'Main',      holes: 18, par: 54 }
  ];

  const readStore = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } };
  const writeStore = s => localStorage.setItem(KEY, JSON.stringify(s));
  const kf = (c, l) => ((c || '').trim() + '|' + (l || '').trim()).toLowerCase();

  const DIC = {
    /* merged view: defaults (+local overrides) + locally added custom courses */
    list() {
      const st = readStore(); const out = []; const seen = new Set();
      DEFAULTS.forEach(d => {
        const o = (st.overrides || {})[kf(d.course, d.layout)] || {};
        out.push({ ...d, ...o }); seen.add(kf(d.course, d.layout));
      });
      (st.custom || []).forEach(c => {
        if (!seen.has(kf(c.course, c.layout))) { out.push(c); seen.add(kf(c.course, c.layout)); }
      });
      return out;
    },
    get(course, layout) {
      return this.list().find(c => kf(c.course, c.layout) === kf(course, layout)) || null;
    },
    /* edit holes/par — overrides a default, or updates/creates a custom course */
    set(course, layout, patch) {
      const st = readStore(); const k = kf(course, layout);
      if (DEFAULTS.find(d => kf(d.course, d.layout) === k)) {
        st.overrides = st.overrides || {};
        st.overrides[k] = { ...(st.overrides[k] || {}), ...patch };
      } else {
        st.custom = st.custom || [];
        const i = st.custom.findIndex(c => kf(c.course, c.layout) === k);
        if (i >= 0) Object.assign(st.custom[i], patch);
        else st.custom.push({ course: (course || '').trim(), layout: (layout || '').trim(), holes: 18, par: 54, ...patch });
      }
      writeStore(st);
    },
    label(c) { return c.course + (c.layout ? ' — ' + c.layout : ''); },

    /* UDisc-style score-to-par: E, -3, +2 */
    toPar(score, par) {
      if (par == null || score == null || isNaN(score)) return '';
      const d = Number(score) - Number(par);
      return d === 0 ? 'E' : (d > 0 ? '+' + d : String(d));
    },
    fmtScore(score, par) {
      const t = this.toPar(score, par);
      return t ? `${score} (${t})` : String(score ?? '—');
    },

    /* shotgun-start helper: n groups spread evenly across the course's holes */
    spreadHoles(n, holes) {
      holes = holes || 18; n = Math.max(1, n);
      const step = Math.max(1, Math.floor(holes / n));
      const out = [];
      for (let i = 0; i < n; i++) out.push((i * step) % holes + 1);
      return out;
    }
  };
  g.DIC = DIC;
})(window);
