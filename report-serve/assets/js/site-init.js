(function () {
  var title = window.SITE_CONFIG && window.SITE_CONFIG.title;
  if (title) {
    var logo = document.querySelector(".site-logo");
    if (logo) logo.textContent = title;
  }

  var STORAGE_KEY = "geo-surface-view";
  var SURFACES = [
    { id: "design-ui", label: "设计UI调整" },
    { id: "content-adjust", label: "文档内容调整" },
    { id: "frontend-adjust", label: "前端调整" }
  ];

  function preferredSurface() {
    try {
      var v = localStorage.getItem(STORAGE_KEY);
      if (v && SURFACES.some(function (s) { return s.id === v; })) return v;
    } catch (e) {}
    return "design-ui";
  }

  function applySurface(id) {
    SURFACES.forEach(function (s) {
      var el = document.getElementById(s.id);
      if (!el) return;
      el.hidden = s.id !== id;
      el.style.display = s.id === id ? "" : "none";
    });
    try { localStorage.setItem(STORAGE_KEY, id); } catch (e) {}
    var sel = document.getElementById("surface-select");
    if (sel && sel.value !== id) sel.value = id;
  }

  function injectStyles() {
    if (document.getElementById("geo-topbar-surface-style")) return;
    var style = document.createElement("style");
    style.id = "geo-topbar-surface-style";
    style.textContent = [
      ".topbar-inner{display:flex;align-items:center;justify-content:flex-start;gap:0;}",
      ".topbar .site-nav,.topbar-inner > .site-nav{",
      "  display:flex;align-items:center;gap:4px;flex:0 0 auto;flex-wrap:wrap;",
      "  margin-left:0;",
      "}",
      ".topbar .surface-select-wrap{",
      "  display:inline-flex;align-items:center;margin-left:auto;flex-shrink:0;",
      "}",
      ".topbar .surface-select{",
      "  appearance:none;-webkit-appearance:none;",
      "  height:34px;padding:0 32px 0 12px;",
      "  border:1px solid #e2e8f0;border-radius:6px;",
      "  background:#fff url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23595959' d='M1.2 1.5 6 6.3l4.8-4.8'/%3E%3C/svg%3E\") no-repeat right 10px center;",
      "  color:#191919;font:inherit;font-size:13px;font-weight:500;line-height:34px;",
      "  cursor:pointer;min-width:148px;",
      "}",
      ".topbar .surface-select:hover,.topbar .surface-select:focus{",
      "  border-color:#1476FF;outline:none;",
      "}",
      "body.surface-filter-on .section#design-ui[hidden],",
      "body.surface-filter-on .section#content-adjust[hidden],",
      "body.surface-filter-on .section#frontend-adjust[hidden]{display:none!important;}"
    ].join("");
    document.head.appendChild(style);
  }

  function injectSelector() {
    var nav = document.querySelector(".topbar .site-nav, .topbar-inner > .site-nav");
    if (!nav || document.getElementById("surface-select")) return;

    var wrap = document.createElement("div");
    wrap.className = "surface-select-wrap";
    wrap.innerHTML =
      '<label class="visually-hidden" for="surface-select">交付面</label>' +
      '<select id="surface-select" class="surface-select" aria-label="交付面">' +
      SURFACES.map(function (s) {
        return '<option value="' + s.id + '">' + s.label + "</option>";
      }).join("") +
      "</select>";

    nav.insertAdjacentElement("afterend", wrap);

    if (!document.getElementById("geo-visually-hidden-style")) {
      var vs = document.createElement("style");
      vs.id = "geo-visually-hidden-style";
      vs.textContent =
        ".visually-hidden{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}";
      document.head.appendChild(vs);
    }

    var sel = wrap.querySelector("select");
    var initial = preferredSurface();
    sel.value = initial;
    sel.addEventListener("change", function () {
      applySurface(sel.value);
      var target = document.getElementById(sel.value);
      if (target) {
        document.body.classList.add("surface-filter-on");
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });

    var hasAny = SURFACES.some(function (s) {
      return document.getElementById(s.id);
    });
    if (hasAny) {
      document.body.classList.add("surface-filter-on");
      applySurface(initial);
    }
  }

  function syncFromHash() {
    var hash = (location.hash || "").replace(/^#/, "");
    if (!hash) return;
    if (SURFACES.some(function (s) { return s.id === hash; })) {
      document.body.classList.add("surface-filter-on");
      applySurface(hash);
    }
  }

  injectStyles();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      injectSelector();
      syncFromHash();
    });
  } else {
    injectSelector();
    syncFromHash();
  }
  window.addEventListener("hashchange", syncFromHash);
})();
