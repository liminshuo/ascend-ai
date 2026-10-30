(function () {
  var title = window.SITE_CONFIG && window.SITE_CONFIG.title;
  if (title) {
    var logo = document.querySelector(".site-logo");
    if (logo) logo.textContent = title;
  }

  var STORAGE_KEY = "geo-surface-view";
  var ICONS = {
    "design-ui":
      '<svg class="surface-tab-icon" width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">' +
      '<rect x="3.5" y="4.5" width="21" height="19" rx="3" stroke="currentColor" stroke-width="1.75"/>' +
      '<path d="M3.5 10.5h21M11.5 10.5v13" stroke="currentColor" stroke-width="1.75"/>' +
      "</svg>",
    "content-adjust":
      '<svg class="surface-tab-icon" width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">' +
      '<path d="M8 4.5h9.5L22.5 9.5V23a1.5 1.5 0 0 1-1.5 1.5H8A1.5 1.5 0 0 1 6.5 23V6A1.5 1.5 0 0 1 8 4.5Z" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>' +
      '<path d="M17 4.5V9h5.5M10 14h8M10 18.5h6" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>' +
      "</svg>",
    "frontend-adjust":
      '<svg class="surface-tab-icon" width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">' +
      '<path d="M9 8.5 4.5 14 9 19.5M19 8.5 23.5 14 19 19.5M15.5 6.5 12.5 21.5" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>' +
      "</svg>"
  };
  var SURFACES = [
    { id: "design-ui", label: "设计实践", desc: "视觉呈现与交互结构" },
    { id: "content-adjust", label: "Markdown 书写", desc: "文案、层级与适用表述" },
    { id: "frontend-adjust", label: "前端实现", desc: "源码结构与抓取管道" }
  ];

  function preferredSurface() {
    try {
      var v = localStorage.getItem(STORAGE_KEY);
      if (v && SURFACES.some(function (s) { return s.id === v; })) return v;
    } catch (e) {}
    return "design-ui";
  }

  function availableSurfaces() {
    return SURFACES.filter(function (s) {
      return document.getElementById(s.id);
    });
  }

  function applySurface(id) {
    SURFACES.forEach(function (s) {
      var el = document.getElementById(s.id);
      if (!el) return;
      el.hidden = s.id !== id;
      el.style.display = s.id === id ? "" : "none";
    });
    try { localStorage.setItem(STORAGE_KEY, id); } catch (e) {}

    var tabs = document.querySelectorAll(".surface-tabs [role='tab']");
    tabs.forEach(function (btn) {
      var on = btn.getAttribute("data-surface") === id;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
      btn.tabIndex = on ? 0 : -1;
    });
  }

  function injectPeerFoldStyles() {
    if (document.getElementById("geo-peer-fold-style")) return;
    var style = document.createElement("style");
    style.id = "geo-peer-fold-style";
    style.textContent = [
      ".peer-nav li.peer-sub.has-children{list-style:none;}",
      ".peer-nav .peer-row{display:flex;align-items:stretch;min-height:36px;border-left:2px solid transparent;box-sizing:border-box;}",
      ".peer-nav .peer-row:hover{background:var(--color-primary-light,#F5F5F5);}",
      ".peer-nav .peer-link{flex:1;min-width:0;display:flex;align-items:center;padding:8px 4px 8px 20px;font-size:13px;line-height:1.5;color:var(--muted,#595959);font-weight:400;cursor:pointer;user-select:none;box-sizing:border-box;}",
      ".peer-nav .peer-row:hover .peer-link{color:var(--text,#191919);}",
      ".peer-nav .peer-fold{appearance:none;-webkit-appearance:none;border:0 !important;box-shadow:none !important;background:transparent !important;cursor:pointer;flex:0 0 36px;width:36px;min-height:36px;display:inline-flex;align-items:center;justify-content:center;color:var(--muted,#595959);padding:0 !important;margin:0;border-radius:0 !important;font-size:0;line-height:0;}",
      ".peer-nav .peer-row:hover .peer-fold{color:var(--text,#191919);background:transparent !important;}",
      ".peer-nav .peer-fold svg{display:none !important;}",
      ".peer-nav .peer-fold::before{content:'';box-sizing:border-box;width:6px;height:6px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(-45deg);margin-top:1px;transition:transform .15s;}",
      ".peer-nav li.peer-sub.is-open>.peer-row .peer-fold::before{transform:rotate(45deg);margin-top:-2px;}",
      ".peer-nav li.peer-sub>.peer-sub-list{list-style:none;margin:0;padding:0 0 4px;}",
      ".peer-nav li.peer-sub:not(.is-open)>.peer-sub-list{display:none;}",
      ".peer-nav li.peer-sub>.peer-sub-list a{display:block;padding:8px 20px 8px 32px;font-size:13px;line-height:1.5;color:var(--muted,#595959);font-weight:400;border-left:2px solid transparent;text-decoration:none;min-height:36px;box-sizing:border-box;}",
      ".peer-nav li.peer-sub>.peer-sub-list a:hover{color:var(--text,#191919);background:var(--color-primary-light,#F5F5F5);text-decoration:none;}",
      ".peer-nav li.peer-sub>.peer-sub-list a.active{color:var(--accent,#2457d6);border-left-color:var(--accent,#2457d6);background:#EEF5FF;font-weight:600;}"
    ].join("");
    document.head.appendChild(style);
  }

  function injectStyles() {
    if (document.getElementById("geo-surface-tabs-style")) return;
    var style = document.createElement("style");
    style.id = "geo-surface-tabs-style";
    style.textContent = [
      ".surface-tabs{",
      "  margin:16px 0 8px;width:100%;box-sizing:border-box;",
      "}",
      ".surface-tabs-label{",
      "  margin:0 0 16px;padding:0 0 16px;",
      "  font-size:var(--text-h2,24px);font-weight:700;",
      "  line-height:var(--text-h2-lh,36px);letter-spacing:-0.01em;",
      "  color:var(--color-text,#191919);",
      "  border-bottom:2px solid #f0f0f0;",
      "}",
      ".surface-tabs-nav{",
      "  display:grid;",
      "  grid-template-columns:repeat(3,minmax(0,1fr));",
      "  gap:16px;",
      "  width:100%;",
      "}",
      ".surface-tabs-nav [role='tab']{",
      "  appearance:none;-webkit-appearance:none;",
      "  display:flex;flex-direction:column;align-items:flex-start;gap:8px;",
      "  margin:0;padding:14px 16px;min-height:0;box-sizing:border-box;",
      "  border:1px solid #e2e8f0;border-radius:12px;",
      "  background:#fff;color:#191919;text-align:left;",
      "  font:inherit;cursor:pointer;",
      "  transition:border-color .15s,box-shadow .15s,background .15s,color .15s;",
      "}",
      ".surface-tabs-nav [role='tab']:hover{",
      "  border-color:#c5d4eb;background:#fafbfc;",
      "}",
      ".surface-tabs-nav [role='tab'].is-active{",
      "  border-color:#1476FF;background:#F0F6FF;",
      "  box-shadow:0 0 0 1px #1476FF;",
      "}",
      ".surface-tabs-nav [role='tab']:focus-visible{",
      "  outline:2px solid #1476FF;outline-offset:2px;",
      "}",
      ".surface-tab-icon{",
      "  display:block;flex-shrink:0;color:#595959;",
      "}",
      ".surface-tabs-nav [role='tab'].is-active .surface-tab-icon{",
      "  color:#1476FF;",
      "}",
      ".surface-tab-title{",
      "  display:block;margin:0;",
      "  font-size:16px;font-weight:700;line-height:24px;color:inherit;",
      "}",
      ".surface-tab-desc{",
      "  display:block;margin:0;",
      "  font-size:13px;font-weight:400;line-height:20px;color:#595959;",
      "}",
      ".surface-tabs-nav [role='tab'].is-active .surface-tab-desc{",
      "  color:#3d6db5;",
      "}",
      /* 卡片已承担页签语义，隐藏下方重复 H2 */
      "body.surface-filter-on #design-ui > h2,",
      "body.surface-filter-on #content-adjust > h2,",
      "body.surface-filter-on #frontend-adjust > h2{display:none;}",
      "body.surface-filter-on #design-ui:not([hidden]),",
      "body.surface-filter-on #content-adjust:not([hidden]),",
      "body.surface-filter-on #frontend-adjust:not([hidden]){margin-top:16px;}",
      "body.surface-filter-on .section#design-ui[hidden],",
      "body.surface-filter-on .section#content-adjust[hidden],",
      "body.surface-filter-on .section#frontend-adjust[hidden]{display:none!important;}",
      "@media (max-width:720px){",
      "  .surface-tabs-nav{grid-template-columns:1fr;}",
      "  .surface-tabs-nav [role='tab']{padding:14px 16px;}",
      "}"
    ].join("");
    document.head.appendChild(style);
  }

  function injectSelector() {
    if (document.body.hasAttribute("data-no-surface-tabs")) return;
    if (document.getElementById("surface-tabs")) return;

    var surfaces = availableSurfaces();
    if (!surfaces.length) return;

    var first = document.getElementById(surfaces[0].id);
    if (!first || !first.parentNode) return;

    var old = document.querySelector(".surface-select-wrap");
    if (old) old.remove();

    var wrap = document.createElement("div");
    wrap.className = "surface-tabs";
    wrap.id = "surface-tabs";
    wrap.innerHTML =
      '<h2 class="surface-tabs-label" id="surface-tabs-label">典型做法</h2>' +
      '<div class="surface-tabs-nav" role="tablist" aria-labelledby="surface-tabs-label">' +
      surfaces.map(function (s) {
        return (
          '<button type="button" role="tab" class="surface-tab-card" data-surface="' + s.id + '"' +
          ' aria-controls="' + s.id + '" id="surface-tab-' + s.id + '">' +
          (ICONS[s.id] || "") +
          '<span class="surface-tab-title">' + s.label + "</span>" +
          '<span class="surface-tab-desc">' + s.desc + "</span>" +
          "</button>"
        );
      }).join("") +
      "</div>";

    first.parentNode.insertBefore(wrap, first);

    var initial = preferredSurface();
    if (!surfaces.some(function (s) { return s.id === initial; })) {
      initial = surfaces[0].id;
    }

    wrap.querySelectorAll("[role='tab']").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-surface");
        document.body.classList.add("surface-filter-on");
        applySurface(id);
        if (history.replaceState) {
          history.replaceState(null, "", "#" + id);
        } else {
          location.hash = id;
        }
      });
    });

    document.body.classList.add("surface-filter-on");
    applySurface(initial);
  }

  function syncFromHash() {
    var hash = (location.hash || "").replace(/^#/, "");
    if (!hash) return;
    if (SURFACES.some(function (s) { return s.id === hash; })) {
      document.body.classList.add("surface-filter-on");
      applySurface(hash);
    }
  }

  function injectExtraNav() {
    var path = (location.pathname || "").split("/").pop() || "";
    var extras = [
      { href: "skills.html", label: "Skill 目录" }
    ];
    document.querySelectorAll("nav.site-nav").forEach(function (nav) {
      nav.querySelectorAll('a[href="design-guide-image-text.html"]').forEach(function (a) {
        a.remove();
      });
      nav.querySelectorAll("a").forEach(function (a) {
        var href = a.getAttribute("href") || "";
        if (href.indexOf("data-analysis.html") !== -1 || a.textContent.trim() === "数据分析") {
          a.remove();
        }
      });
      extras.forEach(function (item) {
        var existing = nav.querySelector('a[href="' + item.href + '"]');
        if (!existing) {
          existing = document.createElement("a");
          existing.href = item.href;
          existing.textContent = item.label;
          nav.appendChild(existing);
        }
        if (path === item.href) {
          nav.querySelectorAll("a").forEach(function (x) {
            x.classList.remove("active");
          });
          existing.classList.add("active");
        }
      });
    });
  }

  function initPeerFolds() {
    var STORE_KEY = "geo-peer-fold";
    var openMap = {};
    try {
      openMap = JSON.parse(sessionStorage.getItem(STORE_KEY) || "{}") || {};
    } catch (err) {
      openMap = {};
    }

    function setOpen(li, openNow) {
      if (!li) return;
      li.classList.toggle("is-open", openNow);
      var fold = li.querySelector(".peer-fold");
      if (fold) fold.setAttribute("aria-expanded", openNow ? "true" : "false");
      var id = li.getAttribute("data-peer-fold");
      if (id) {
        openMap[id] = openNow;
        try {
          sessionStorage.setItem(STORE_KEY, JSON.stringify(openMap));
        } catch (e) {}
      }
    }

    document.querySelectorAll(".peer-nav li.peer-sub.has-children").forEach(function (li) {
      var id = li.getAttribute("data-peer-fold") || "";
      var childActive = !!li.querySelector(".peer-sub-list a.active");
      var openNow = childActive;
      if (!childActive && Object.prototype.hasOwnProperty.call(openMap, id)) {
        openNow = !!openMap[id];
      } else if (childActive) {
        openNow = true;
      }
      setOpen(li, openNow);
    });

    document.querySelectorAll(".peer-nav").forEach(function (nav) {
      nav.addEventListener("click", function (e) {
        var fold = e.target.closest(".peer-fold");
        var label = e.target.closest(".peer-link");
        var hit = fold || label;
        if (!hit || !nav.contains(hit)) return;
        e.preventDefault();
        e.stopPropagation();
        var li = hit.closest("li.peer-sub.has-children");
        setOpen(li, !li.classList.contains("is-open"));
      });
    });
  }

  injectPeerFoldStyles();
  injectStyles();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      injectExtraNav();
      injectSelector();
      syncFromHash();
      initPeerFolds();
    });
  } else {
    injectExtraNav();
    injectSelector();
    syncFromHash();
    initPeerFolds();
  }
  window.addEventListener("hashchange", syncFromHash);
})();
