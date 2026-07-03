/* Discinsanity — shared course database (Lehigh Valley), UDisc-style scoring support.
   Course/layout carries holes + total par, and optionally PER-HOLE pars + distances (ft)
   so the Scorecard can show "Hole 7 · Par 3 · 285 ft" like UDisc.
   NOTE: UDisc has no public API and blocks scraping (docs/RESEARCH-udisc-data.md), so this is
   OUR editable database: defaults below (par 3 per hole), and anyone can tap the par chip on
   the Scorecard (or ✎ in the Doubles course picker) to set the real par/distance — entered
   once, saved for everyone on that device (cloud later via Supabase).
   Storage: `discinsanity_courses_v1`. Load AFTER account.js/suite.js. */
(function (g) {
  const KEY = 'discinsanity_courses_v1';

  /* Defaults: par 54 / 18 holes standard assumption — EDIT in-app if a layout differs. */
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
  /* per-hole pars win: total par = sum(pars), holes = pars.length */
  const normalize = c => {
    if (Array.isArray(c.pars) && c.pars.length) {
      c.holes = c.pars.length;
      c.par = c.pars.reduce((a, b) => a + (Number(b) || 3), 0);
    }
    return c;
  };

  const DIC = {
    /* merged view: defaults (+local overrides) + locally added custom courses */
    list() {
      const st = readStore(); const out = []; const seen = new Set();
      DEFAULTS.forEach(d => {
        const o = (st.overrides || {})[kf(d.course, d.layout)] || {};
        out.push(normalize({ ...d, ...o })); seen.add(kf(d.course, d.layout));
      });
      (st.custom || []).forEach(c => {
        if (!seen.has(kf(c.course, c.layout))) { out.push(normalize({ ...c })); seen.add(kf(c.course, c.layout)); }
      });
      return out;
    },
    get(course, layout) {
      return this.list().find(c => kf(c.course, c.layout) === kf(course, layout)) || null;
    },
    /* edit holes/par/pars/dists — overrides a default, or updates/creates a custom course */
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
    /* per-hole info (1-based). Par defaults to 3, distance unknown until entered. */
    holePar(course, layout, hole) {
      const c = this.get(course, layout);
      return (c && Array.isArray(c.pars) && c.pars[hole - 1]) ? Number(c.pars[hole - 1]) : 3;
    },
    holeDist(course, layout, hole) {
      const c = this.get(course, layout);
      const d = c && Array.isArray(c.dists) ? c.dists[hole - 1] : null;
      return d ? Number(d) : null;
    },
    /* set one hole's par and/or distance; keeps total par in sync */
    setHole(course, layout, hole, patch) {
      const c = this.get(course, layout); if (!c) return;
      const H = c.holes || 18;
      const pars = Array.isArray(c.pars) && c.pars.length === H ? [...c.pars] : Array.from({ length: H }, (_, i) => (c.pars && c.pars[i]) || 3);
      const dists = Array.isArray(c.dists) && c.dists.length === H ? [...c.dists] : Array.from({ length: H }, (_, i) => (c.dists && c.dists[i]) || null);
      if (patch.par != null && !isNaN(patch.par)) pars[hole - 1] = Number(patch.par);
      if (patch.dist !== undefined) dists[hole - 1] = patch.dist ? Number(patch.dist) : null;
      this.set(course, layout, { pars, dists, holes: H, par: pars.reduce((a, b) => a + (Number(b) || 3), 0) });
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
