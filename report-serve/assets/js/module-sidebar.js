/** 内容载体侧栏（文档层原则 / 实测，自「大模型抓取」迁入） */
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
      { group: "读的懂", id: "c1", href: "principles-image.html", label: "图片内容转译", pageIds: ["image"] },
      { group: null, id: "c2", href: "principles-hotzone.html", label: "图片热区转译", pageIds: ["hotzone"] },
      { group: null, id: "c3", href: "principles-table.html", label: "表格语义化", pageIds: ["table"] },
      { group: null, id: "c4", href: "principles-code.html", label: "代码块语义化", pageIds: ["code"] },
      { group: null, id: "c6", href: "principles-note.html", label: "安全警示语义化", pageIds: ["note"] },
      { group: null, id: "c7", href: "principles-collapse.html", label: "隐藏语义：折叠全量展开", pageIds: ["collapse", "tab"] }
    ]
  };

  var module = document.body.getAttribute("data-module");
  var page = document.body.getAttribute("data-page");
  var items = NAV[module];
  var aside = document.getElementById("module-sidebar");
  if (!aside) return;
  if (!items || items.length <= 1) {
    aside.remove();
    return;
  }

  var html = "";
  if (module === "principles") {
    html += "<ul class=\"sidebar-nav sidebar-phase-nav sidebar-module-title\">";
    html += "<li class=\"nav-group-label\">文档内容载体</li>";
    html += "<li><a href=\"community-ui.html\">← 返回组件清单</a></li>";
    html += "</ul>";
  } else if (module === "problems") {
    html += "<ul class=\"sidebar-nav sidebar-phase-nav sidebar-module-title\">";
    html += "<li class=\"nav-group-label\">内容载体实测</li>";
    html += "<li><a href=\"community-ui.html\">← 返回组件清单</a></li>";
    html += "</ul>";
  }

  function navItemActive(item) {
    if (page === item.id) return true;
    if (item.pageIds && item.pageIds.indexOf(page) >= 0) return true;
    return false;
  }

  html += "<ul class=\"sidebar-nav sidebar-phase-nav\">";
  items.forEach(function (item) {
    if (item.group) {
      html += "<li class=\"nav-group-label\">" + item.group + "</li>";
    }
    var active = navItemActive(item) ? " class=\"active\"" : "";
    html += "<li><a href=\"" + item.href + "\"" + active + ">" + item.label + "</a></li>";
  });
  html += "</ul>";
  aside.innerHTML = html;
})();
