/** 亲和原则 · 原则导航（主题 + 细项折叠；线性 Arrow） */
(function () {
  var NAV = {
    problems: [
      { group: "读不懂", id: "content-image", href: "problems-content-image.html", label: "图片语义缺失" },
      { group: null, id: "content-hotzone", href: "problems-content-hotzone.html", label: "热区信息缺失" },
      { group: null, id: "content-table", href: "problems-content-table.html", label: "表格语义缺失" },
      { group: null, id: "content-code", href: "problems-content-code.html", label: "代码块语义缺失" },
      { group: null, id: "content-note", href: "problems-content-note.html", label: "警示级别缺失" },
      { group: null, id: "content-collapse", href: "problems-content-collapse.html", label: "折叠隐藏语义", pageIds: ["content-collapse", "content-tab"] }
    ],
    principles: [
      {
        group: "可达", id: "page-discover", href: "principles-structure-llms.html", label: "页面可发现",
        pageIds: ["page-discover", "structure-llms"]
      },
      {
        group: null, id: "page-context", href: "principles-breadcrumb.html", label: "页面可访问",
        pageIds: ["page-context", "breadcrumb", "neighbor"],
        children: [
          { id: "breadcrumb", href: "principles-breadcrumb.html", label: "面包屑" },
          { id: "neighbor", href: "principles-neighbor.html", label: "邻篇导航" }
        ]
      },
      {
        group: null, id: "section-anchor", href: "principles-section-anchor.html", label: "章节可访问",
        pageIds: ["section-locate", "section-anchor"]
      },
      {
        group: null, id: "format", href: "principles-format.html", label: "双轨交付",
        pageIds: ["format"]
      },
      {
        group: "可读", id: "content-retrievable", href: "principles-content-retrievable.html", label: "页面 HTML 可读",
        pageIds: ["page-readable", "content-retrievable"]
      },
      {
        group: null, id: "nontext", href: "principles-image.html", label: "非文本信息等价表达",
        pageIds: ["nontext", "image", "icon-text", "style-semantic", "media"],
        children: [
          { id: "image", href: "principles-image.html", label: "图片内容转译" },
          { id: "icon-text", href: "principles-icon-text.html", label: "图标语义锚定" },
          { id: "style-semantic", href: "principles-style-semantic.html", label: "颜色语义转写" },
          { id: "media", href: "principles-media.html", label: "音视频要点伴随" }
        ]
      },
      {
        group: null, id: "structured", href: "principles-table.html", label: "结构化可读",
        pageIds: ["structured", "table", "code"],
        children: [
          { id: "table", href: "principles-table.html", label: "表格语义化" },
          { id: "code", href: "principles-code.html", label: "代码块语义化" }
        ]
      },
      {
        group: null, id: "hidden", href: "principles-tab.html", label: "隐藏信息持续可获取",
        pageIds: ["hidden", "tab", "collapse", "default-visible", "mask-clear"],
        children: [
          { id: "tab", href: "principles-tab.html", label: "Tab 面板可全量抓取" },
          { id: "collapse", href: "principles-collapse.html", label: "折叠默认展开" },
          { id: "default-visible", href: "principles-default-visible.html", label: "悬停不承载关键内容" },
          { id: "mask-clear", href: "principles-mask-clear.html", label: "蒙版不遮挡关键步骤" }
        ]
      },
      {
        group: null, id: "page-elements", href: "principles-control-label.html", label: "页面元素与状态可获取",
        pageIds: ["page-elements", "controls", "control-label", "gui-map"],
        children: [
          { id: "control-label", href: "principles-control-label.html", label: "控件须配独立标签" },
          { id: "gui-map", href: "principles-gui-map.html", label: "控件数值转写" }
        ]
      },
      {
        group: "可理解", id: "doc-structure", href: "principles-hierarchy.html", label: "信息结构明确",
        pageIds: ["doc-structure", "hierarchy", "noise"],
        children: [
          { id: "hierarchy", href: "principles-hierarchy.html", label: "标题按层级标注" },
          { id: "noise", href: "principles-noise.html", label: "推荐内容置后" }
        ]
      },
      {
        group: null, id: "lifecycle", href: "principles-timeliness.html", label: "必要信息完整",
        pageIds: ["lifecycle", "timeliness", "date-modified", "a2", "structure-metadata"],
        children: [
          { id: "timeliness", href: "principles-timeliness.html", label: "版本号外显" },
          { id: "date-modified", href: "principles-date-modified.html", label: "明确更新日期" },
          { id: "a2", href: "principles-a2.html", label: "失效/弃用状态显化" },
          { id: "structure-metadata", href: "principles-structure-metadata.html", label: "元数据丰富化" }
        ]
      },
      {
        group: null, id: "meaning", href: "principles-status-word.html", label: "内容含义明确",
        pageIds: ["meaning", "status-word", "note", "link"],
        children: [
          { id: "status-word", href: "principles-status-word.html", label: "状态完整标注" },
          { id: "note", href: "principles-note.html", label: "安全警示语义化" },
          { id: "link", href: "principles-link.html", label: "链接语义化" }
        ]
      },
      {
        group: "可操作", id: "executable", href: "principles-steps.html", label: "操作可执行",
        pageIds: ["executable", "example", "playground", "steps"],
        children: [
          { id: "steps", href: "principles-steps.html", label: "步骤列表化" },
          { id: "example", href: "principles-example.html", label: "示例路径可参照" },
          { id: "playground", href: "principles-playground.html", label: "可交互示例" }
        ]
      },
      {
        group: "可验证", id: "outcome", href: "principles-expected.html", label: "任务结果可确认",
        pageIds: ["outcome", "verify", "expected"],
        children: [
          { id: "expected", href: "principles-expected.html", label: "写明预期结果" },
          { id: "verify", href: "principles-verify.html", label: "验证区块" }
        ]
      },
      {
        group: null, id: "failure-handle", href: "principles-default-empty.html", label: "失败状态可处理",
        pageIds: ["failure-handle", "default-empty", "exception"],
        children: [
          { id: "default-empty", href: "principles-default-empty.html", label: "缺省空态文案化" },
          { id: "exception", href: "principles-exception.html", label: "常见异常说明" }
        ]
      }
    ]
  };

  var module = document.body.getAttribute("data-module");
  var page = document.body.getAttribute("data-page");
  var items = NAV[module];
  var aside = document.getElementById("module-sidebar");
  if (!aside) return;
  if (!items || !items.length) {
    aside.remove();
    return;
  }

  // 一级菜单无独立页：链接一律指向首个二级
  items.forEach(function (item) {
    if (item.children && item.children.length) {
      item.href = item.children[0].href;
    }
  });

  var STORE_KEY = "aff-nav-open";
  var openMap = {};
  try {
    openMap = JSON.parse(sessionStorage.getItem(STORE_KEY) || "{}") || {};
  } catch (e) {
    openMap = {};
  }

  function navItemActive(item) {
    if (item.pageIds && item.pageIds.indexOf(page) !== -1) return true;
    return item.id === page;
  }

  function childActive(child) {
    if (child.id === page) return true;
    var href = child.href || "";
    var hashIdx = href.indexOf("#");
    if (hashIdx === -1) return false;
    var file = href.slice(0, hashIdx);
    var hash = href.slice(hashIdx);
    var path = location.pathname || "";
    var onFile = !file || path === file || path.endsWith("/" + file) || path.endsWith(file);
    return onFile && location.hash === hash;
  }

  function isOpen(item) {
    // 用户显式收起/展开优先；否则当前主题默认展开
    if (Object.prototype.hasOwnProperty.call(openMap, item.id)) return !!openMap[item.id];
    if (navItemActive(item) && item.children && item.children.length) return true;
    return false;
  }

  function setOpen(li, openNow) {
    if (!li) return;
    li.classList.toggle("is-open", openNow);
    var fold = li.querySelector(".nav-fold");
    if (fold) fold.setAttribute("aria-expanded", openNow ? "true" : "false");
    var sub = li.querySelector(".nav-sub");
    if (sub) sub.hidden = !openNow;
    var id = li.getAttribute("data-nav-id");
    if (id) {
      openMap[id] = openNow;
      try {
        sessionStorage.setItem(STORE_KEY, JSON.stringify(openMap));
      } catch (err) {}
    }
    syncExpandAllBtn();
  }

  function allParentsOpen() {
    var nodes = aside.querySelectorAll(".sidebar-phase-nav:not(.sidebar-module-title) .nav-item.has-children");
    if (!nodes.length) return false;
    for (var i = 0; i < nodes.length; i++) {
      if (!nodes[i].classList.contains("is-open")) return false;
    }
    return true;
  }

  function setAllParentsOpen(openNow) {
    aside.querySelectorAll(".sidebar-phase-nav:not(.sidebar-module-title) .nav-item.has-children").forEach(function (li) {
      li.classList.toggle("is-open", openNow);
      var fold = li.querySelector(".nav-fold");
      if (fold) fold.setAttribute("aria-expanded", openNow ? "true" : "false");
      var sub = li.querySelector(".nav-sub");
      if (sub) sub.hidden = !openNow;
      var id = li.getAttribute("data-nav-id");
      if (id) openMap[id] = openNow;
    });
    try {
      sessionStorage.setItem(STORE_KEY, JSON.stringify(openMap));
    } catch (err) {}
    syncExpandAllBtn();
  }

  function syncExpandAllBtn() {
    var btn = aside.querySelector(".nav-expand-all");
    if (!btn) return;
    var allOpen = allParentsOpen();
    btn.classList.toggle("is-all-open", allOpen);
    btn.setAttribute("aria-expanded", allOpen ? "true" : "false");
    btn.setAttribute("aria-label", allOpen ? "收起全部一级菜单" : "展开全部一级菜单");
    btn.title = allOpen ? "收起全部" : "展开全部";
  }

  var html = "";
  if (module === "principles") {
    html += "<ul class=\"sidebar-nav sidebar-phase-nav sidebar-module-title\">";
    html += "<li class=\"nav-group-label nav-group-label--toggle\">";
    html += "<span class=\"nav-group-label-text\">亲和原则</span>";
    html += "<button type=\"button\" class=\"nav-expand-all\" aria-expanded=\"false\" aria-label=\"展开全部一级菜单\" title=\"展开/收起全部\">";
    html += "<img class=\"nav-expand-all-icon nav-expand-all-icon--expand\" src=\"assets/icons/nav-expand-all.png\" width=\"14\" height=\"14\" alt=\"\" aria-hidden=\"true\">";
    html += "<img class=\"nav-expand-all-icon nav-expand-all-icon--collapse\" src=\"assets/icons/nav-collapse-all.png\" width=\"14\" height=\"14\" alt=\"\" aria-hidden=\"true\">";
    html += "</button>";
    html += "</li>";
    html += "<li><a href=\"principles-overview.html\"" + (page === "overview" ? " class=\"active\"" : "") + ">AI 亲和原则</a></li>";
    html += "<li><a href=\"principles-affinity-full.html\"" + (page === "affinity-full" ? " class=\"active\"" : "") + ">全量亲和原则</a></li>";
    html += "</ul>";
  } else if (module === "problems") {
    html += "<ul class=\"sidebar-nav sidebar-phase-nav sidebar-module-title\">";
    html += "<li class=\"nav-group-label\">内容载体实测</li>";
    html += "<li><a href=\"community-ui.html\">← 返回组件清单</a></li>";
    html += "</ul>";
  }

  html += "<ul class=\"sidebar-nav sidebar-phase-nav\">";
  var lastGroup = null;
  items.forEach(function (item) {
    if (item.group && item.group !== lastGroup) {
      html += "<li class=\"nav-group-label\">" + item.group + "</li>";
      lastGroup = item.group;
    }

    var hasKids = item.children && item.children.length;
    var active = navItemActive(item);
    var open = hasKids && isOpen(item);
    var liClass = "nav-item" + (hasKids ? " has-children" : "") + (open ? " is-open" : "");
    html += "<li class=\"" + liClass + "\" data-nav-id=\"" + item.id + "\">";

    if (hasKids) {
      html += "<div class=\"nav-row\">";
      html += "<a class=\"nav-link" + (active && !item.children.some(childActive) ? " active" : "") + (active ? " is-current" : "") + "\" href=\"" + item.href + "\">" + item.label + "</a>";
      html += "<button type=\"button\" class=\"nav-fold\" aria-expanded=\"" + (open ? "true" : "false") + "\" aria-label=\"展开或收起「" + item.label + "」\"></button>";
      html += "</div>";
      html += "<ul class=\"nav-sub\"" + (open ? "" : " hidden") + ">";
      item.children.forEach(function (child) {
        var ca = childActive(child) ? " class=\"active\"" : "";
        html += "<li><a href=\"" + child.href + "\"" + ca + ">" + child.label + "</a></li>";
      });
      html += "</ul>";
    } else {
      html += "<a href=\"" + item.href + "\"" + (active ? " class=\"active\"" : "") + ">" + item.label + "</a>";
    }
    html += "</li>";
  });
  html += "</ul>";

  aside.className = "sidebar";
  aside.innerHTML = html;

  aside.querySelectorAll(".nav-item.has-children").forEach(function (li) {
    var subActive = li.querySelector(".nav-sub a.active");
    var link = li.querySelector(".nav-link");
    if (subActive && link) link.classList.add("is-current");
  });

  window.addEventListener("hashchange", function () {
    aside.querySelectorAll(".nav-sub a").forEach(function (a) {
      var href = a.getAttribute("href") || "";
      var hashIdx = href.indexOf("#");
      if (hashIdx === -1) return;
      var file = href.slice(0, hashIdx);
      var hash = href.slice(hashIdx);
      var path = location.pathname || "";
      var onFile = !file || path === file || path.endsWith("/" + file) || path.endsWith(file);
      a.classList.toggle("active", onFile && location.hash === hash);
    });
    aside.querySelectorAll(".nav-item.has-children").forEach(function (li) {
      var link = li.querySelector(".nav-link");
      if (!link) return;
      var subActive = li.querySelector(".nav-sub a.active");
      link.classList.toggle("is-current", !!subActive || link.classList.contains("active"));
    });
  });

  function pathEndsWith(href) {
    if (!href) return false;
    var path = location.pathname || "";
    return path === href || path.endsWith("/" + href) || path.endsWith(href);
  }

  aside.addEventListener("click", function (e) {
    var expandAll = e.target.closest(".nav-expand-all");
    if (expandAll) {
      e.preventDefault();
      e.stopPropagation();
      setAllParentsOpen(!allParentsOpen());
      return;
    }

    var fold = e.target.closest(".nav-fold");
    if (fold) {
      e.preventDefault();
      e.stopPropagation();
      var liFold = fold.closest(".nav-item");
      setOpen(liFold, !liFold.classList.contains("is-open"));
      return;
    }

    var parentLink = e.target.closest("a.nav-link");
    if (parentLink) {
      var li = parentLink.closest(".nav-item.has-children");
      if (li) {
        // 一级点击：展开并进入首个二级（href 已指向 children[0]）
        var id = li.getAttribute("data-nav-id");
        if (id) {
          openMap[id] = true;
          try {
            sessionStorage.setItem(STORE_KEY, JSON.stringify(openMap));
          } catch (err3) {}
        }
        setOpen(li, true);
        var href = parentLink.getAttribute("href") || "";
        var file = href.split("#")[0];
        var hashIdx = href.indexOf("#");
        var hash = hashIdx >= 0 ? href.slice(hashIdx) : "";
        if (pathEndsWith(file) && (!hash || location.hash === hash)) {
          e.preventDefault();
          try {
            sessionStorage.setItem("aff-sidebar-scroll", String(aside.scrollTop));
          } catch (err0) {}
          return;
        }
      }
    }

    var a = e.target.closest("a[href]");
    if (!a || a.getAttribute("href").charAt(0) === "#") return;
    try {
      sessionStorage.setItem("aff-sidebar-scroll", String(aside.scrollTop));
    } catch (err2) {}
  });

  if (module === "principles") {
    document.documentElement.style.scrollBehavior = "auto";
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
    window.scrollTo(0, 0);
    try {
      var saved = sessionStorage.getItem("aff-sidebar-scroll");
      if (saved != null) aside.scrollTop = Number(saved) || 0;
    } catch (err) {}
    syncExpandAllBtn();
  }
})();
