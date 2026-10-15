/* BRAIN documentation: theme switch, navigation drawer, page contents with
   the current section highlighted, and a quick search over Sphinx's own
   index (searchindex.js), opened with Ctrl+K or "/". */
(function () {
  "use strict";
  var root = document.documentElement;

  /* ---- colour theme: system -> light -> dark -> system ---------------- */
  var themeBtn = document.querySelector("[data-theme-toggle]");
  function setTheme(t) {
    try {
      if (t === "system") { root.removeAttribute("data-theme"); localStorage.removeItem("brain-theme"); }
      else { root.setAttribute("data-theme", t); localStorage.setItem("brain-theme", t); }
    } catch (e) { if (t !== "system") root.setAttribute("data-theme", t); }
    if (themeBtn) {
      var label = { system: "follows the system", light: "light", dark: "dark" }[t];
      themeBtn.setAttribute("aria-label", "Colour theme: " + label + " (click to change)");
      themeBtn.title = "Theme: " + label;
    }
  }
  if (themeBtn) {
    setTheme(root.getAttribute("data-theme") || "system");
    themeBtn.addEventListener("click", function () {
      var now = root.getAttribute("data-theme") || "system";
      setTheme(now === "system" ? "light" : now === "light" ? "dark" : "system");
    });
  }

  /* ---- navigation drawer on narrow screens ----------------------------- */
  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    document.querySelectorAll("[data-nav-toggle]").forEach(function (b) {
      b.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  document.querySelectorAll("[data-nav-toggle]").forEach(function (b) {
    b.addEventListener("click", function () { setNav(!document.body.classList.contains("nav-open")); });
  });
  document.querySelectorAll("[data-nav-close]").forEach(function (b) {
    b.addEventListener("click", function () { setNav(false); });
  });
  var activeNav = document.querySelector(".sidebar .nav-link.is-active");
  if (activeNav && activeNav.scrollIntoView) {
    var sb = document.querySelector("[data-sidebar]");
    if (sb && activeNav.offsetTop > sb.clientHeight - 80) sb.scrollTop = activeNav.offsetTop - sb.clientHeight / 3;
  }

  /* ---- on this page ---------------------------------------------------- */
  var list = document.querySelector("[data-onpage]");
  if (list) {
    var heads = Array.prototype.slice.call(document.querySelectorAll(".body section > h2, .body section > h3"))
      .filter(function (h) { return h.parentElement && h.parentElement.id; });
    if (heads.length < 2) { list.parentElement.classList.add("is-empty"); }
    var links = heads.map(function (h) {
      var li = document.createElement("li");
      li.className = h.tagName === "H3" ? "l3" : "l2";
      var a = document.createElement("a");
      a.href = "#" + h.parentElement.id;
      a.textContent = h.textContent.replace(/[#¶]\s*$/, "").trim();
      li.appendChild(a); list.appendChild(li);
      return a;
    });
    function spy() {
      var y = window.scrollY + 120, cur = -1;
      heads.forEach(function (h, i) { if (h.getBoundingClientRect().top + window.scrollY <= y) cur = i; });
      if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 4) cur = heads.length - 1;
      links.forEach(function (a, i) { a.classList.toggle("is-active", i === cur); });
    }
    if (heads.length) { window.addEventListener("scroll", spy, { passive: true }); spy(); }
  }

  /* ---- code panel tabs (home page) ------------------------------------- */
  document.querySelectorAll("[data-codepanel]").forEach(function (panel) {
    var tabs = panel.querySelectorAll("[data-tab]");
    tabs.forEach(function (t) {
      t.addEventListener("click", function () {
        tabs.forEach(function (o) { o.setAttribute("aria-selected", o === t ? "true" : "false"); });
        panel.querySelectorAll("[data-pane]").forEach(function (p) { p.hidden = p.getAttribute("data-pane") !== t.getAttribute("data-tab"); });
      });
    });
  });

  /* ---- quick search ----------------------------------------------------- */
  var modal = document.querySelector("[data-search-modal]");
  var input = document.querySelector("[data-search-input]");
  var out = document.querySelector("[data-search-results]");
  var hint = document.querySelector("[data-search-hint]");
  var index = null, loading = false, current = -1;

  function loadIndex(done) {
    if (index) return done();
    if (loading) return;
    loading = true;
    var own = window.Search;
    window.Search = { setIndex: function (i) { index = i; window.Search = own; done(); } };
    var s = document.createElement("script");
    s.src = window.BRAIN_SEARCH_INDEX;
    s.onerror = function () { hint.textContent = "The search index could not be loaded."; };
    document.head.appendChild(s);
  }
  function url(doc, anchor) {
    return window.BRAIN_ROOT + doc + ".html" + (anchor ? "#" + anchor : "");
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function search(q) {
    q = q.trim().toLowerCase();
    out.innerHTML = ""; current = -1;
    if (!q) { hint.innerHTML = "Type to search page titles, section headings, functions and words."; return; }
    var hits = [], seen = {};
    function add(score, doc, anchor, title) {
      var key = doc + "#" + (anchor || "");
      if (seen[key] !== undefined) { hits[seen[key]].score = Math.max(hits[seen[key]].score, score); return; }
      seen[key] = hits.length;
      hits.push({ score: score, doc: doc, anchor: anchor, title: title });
    }
    var titles = index.titles, docs = index.docnames;
    Object.keys(index.alltitles || {}).forEach(function (t) {
      var lt = t.toLowerCase(), pos = lt.indexOf(q);
      if (pos < 0) return;
      (index.alltitles[t] || []).forEach(function (e) {
        add((pos === 0 ? 30 : 20) + (e[1] ? 0 : 5) - lt.length / 40, e[0], e[1], t);
      });
    });
    var objs = index.objects || {};
    Object.keys(objs).forEach(function (prefix) {
      var arr = objs[prefix];
      if (!Array.isArray(arr)) return;
      arr.forEach(function (o) {
        if (!Array.isArray(o) || o.length < 5) return;
        var full = (prefix ? prefix + "." : "") + o[4];
        var lf = full.toLowerCase(), pos = lf.indexOf(q);
        if (pos < 0) return;
        add(25 - pos / 10, o[0], o[3] === "" ? full : o[3], full);
      });
    });
    var words = q.split(/\s+/).filter(function (w) { return w.length > 2; });
    if (words.length) {
      var count = {};
      words.forEach(function (w) {
        var got = {};
        Object.keys(index.terms).forEach(function (term) {
          if (term.indexOf(w.slice(0, Math.max(3, w.length - 2))) !== 0) return;
          var d = index.terms[term]; (Array.isArray(d) ? d : [d]).forEach(function (i) { got[i] = 1; });
        });
        Object.keys(got).forEach(function (i) { count[i] = (count[i] || 0) + 1; });
      });
      Object.keys(count).forEach(function (i) {
        if (count[i] === words.length) add(5 + count[i], +i, null, titles[i]);
      });
    }
    hits.sort(function (a, b) { return b.score - a.score; });
    hits.slice(0, 14).forEach(function (h) {
      var li = document.createElement("li");
      var page = titles[h.doc] || docs[h.doc];
      var tabs = window.BRAIN_TABS || {}, section = "";
      Object.keys(tabs).forEach(function (pre) { if (docs[h.doc].indexOf(pre) === 0) section = tabs[pre]; });
      var where = [section, h.title !== page ? page : ""].filter(Boolean).join(" · ");
      li.innerHTML = '<a href="' + url(docs[h.doc], h.anchor) + '"><span class="r-title">' + esc(h.title) +
        '</span>' + (where ? '<span class="r-page">' + esc(where) + "</span>" : "") + "</a>";
      out.appendChild(li);
    });
    hint.innerHTML = hits.length ? 'Enter opens the first; ↑ ↓ to move. <a href="' + window.BRAIN_SEARCH_PAGE + "?q=" +
      encodeURIComponent(q) + '">Every match, with context</a>' :
      'Nothing found. <a href="' + window.BRAIN_SEARCH_PAGE + "?q=" + encodeURIComponent(q) + '">Search the full text</a>';
  }
  function move(step) {
    var as = out.querySelectorAll("a");
    if (!as.length) return;
    current = (current + step + as.length) % as.length;
    as.forEach(function (a, i) { a.classList.toggle("is-current", i === current); });
    as[current].scrollIntoView({ block: "nearest" });
  }
  function open() {
    if (!modal) return;
    modal.hidden = false; document.body.style.overflow = "hidden";
    input.value = ""; out.innerHTML = ""; input.focus();
    loadIndex(function () { search(input.value); });
  }
  function close() { if (modal) { modal.hidden = true; document.body.style.overflow = ""; } }
  document.querySelectorAll("[data-search-open]").forEach(function (b) { b.addEventListener("click", open); });
  document.querySelectorAll("[data-search-close]").forEach(function (b) { b.addEventListener("click", close); });
  if (input) {
    input.addEventListener("input", function () { if (index) search(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") {
        var as = out.querySelectorAll("a");
        if (as.length) { window.location.href = as[Math.max(current, 0)].href; close(); }
      } else if (e.key === "Escape") { close(); }
    });
  }
  document.addEventListener("keydown", function (e) {
    var typing = /input|textarea|select/i.test((e.target && e.target.tagName) || "");
    if ((e.key === "k" || e.key === "K") && (e.ctrlKey || e.metaKey)) { e.preventDefault(); open(); }
    else if (e.key === "/" && !typing && modal && modal.hidden) { e.preventDefault(); open(); }
    else if (e.key === "Escape") { close(); setNav(false); }
  });
})();

/* Now and then a shooting star crosses the background: a thin streak with a
   fading tail, light on the dark theme and ink on the light one (--star and
   --star-alpha in brain.css). Behind the column of text it is drawn at half
   strength, so it never competes with a letter. None for anyone who prefers
   reduced motion; paused while the tab is hidden. */
(function () {
  "use strict";
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var canvas = document.createElement("canvas");
  canvas.className = "sky";
  canvas.setAttribute("aria-hidden", "true");
  document.body.insertBefore(canvas, document.body.firstChild);
  var ctx = canvas.getContext("2d");
  if (!ctx) return;
  var W = 0, H = 0, meteors = [], nextMeteor = 0, ink = "255,255,255", gain = 1, frame = 0;
  var colL = 0, colR = 0;

  function rand(a, b) { return a + Math.random() * (b - a); }
  function now() { return window.performance ? performance.now() : 0; }
  function readStyle() {
    var cs = getComputedStyle(document.documentElement);
    var c = cs.getPropertyValue("--star").trim();
    if (c) ink = c;
    var g = parseFloat(cs.getPropertyValue("--star-alpha"));
    gain = isFinite(g) ? g : 1;
  }
  function textColumn() {
    var el = document.querySelector(".article") || document.querySelector(".home .hero") || document.querySelector("main");
    if (!el) { colL = colR = 0; return; }
    var r = el.getBoundingClientRect();
    colL = r.left - 12; colR = r.right + 12;
  }
  function resize() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    textColumn();
  }
  function spawn(t) {
    var fromLeft = Math.random() < 0.5, ang = rand(0.35, 0.65) * (fromLeft ? 1 : -1);
    var speed = rand(0.55, 0.9) * Math.max(W, 600) / 1000;
    meteors.push({ x: fromLeft ? rand(0, W * 0.6) : rand(W * 0.4, W), y: rand(-20, H * 0.35),
                   vx: Math.sin(ang) * speed, vy: Math.cos(ang) * speed,
                   len: rand(90, 170), born: t, life: rand(900, 1400) });
    nextMeteor = t + rand(5000, 11000);
  }
  function draw(t) {
    if (frame++ % 60 === 0) readStyle();
    ctx.clearRect(0, 0, W, H);
    if (t > nextMeteor) spawn(t);
    for (var i = meteors.length - 1; i >= 0; i--) {
      var m = meteors[i], age = t - m.born;
      if (age > m.life) { meteors.splice(i, 1); continue; }
      var hx = m.x + m.vx * age, hy = m.y + m.vy * age;
      var sp = Math.hypot(m.vx, m.vy), tx = hx - m.vx / sp * m.len, ty = hy - m.vy / sp * m.len;
      var fade = gain * Math.sin(Math.PI * age / m.life) * (hx > colL && hx < colR ? 0.5 : 1);
      var g = ctx.createLinearGradient(hx, hy, tx, ty);
      g.addColorStop(0, "rgba(" + ink + "," + (0.9 * fade).toFixed(3) + ")");
      g.addColorStop(1, "rgba(" + ink + ",0)");
      ctx.strokeStyle = g; ctx.lineWidth = 1.4; ctx.lineCap = "round";
      ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(tx, ty); ctx.stroke();
      ctx.fillStyle = "rgba(" + ink + "," + fade.toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(hx, hy, 1.3, 0, 6.283); ctx.fill();
    }
  }
  var running = false;
  function loop(t) { if (!running) return; draw(t); requestAnimationFrame(loop); }
  function start() { if (running) return; running = true; requestAnimationFrame(loop); }
  function stop() { running = false; }

  readStyle(); resize();
  nextMeteor = now() + rand(1500, 4000);
  start();
  var resizeTimer;
  window.addEventListener("resize", function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(resize, 150); });
  document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });
  new MutationObserver(readStyle).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
})();
