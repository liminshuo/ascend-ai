/** 全站模块侧栏：一项一页，无锚点导航 */
(function () {
  var NAV = {
  "background": [],
  "problems": [
    {
      "group": "抓不到",
      "id": "structure-llms",
      "href": "problems-structure-llms.html",
      "label": "机器发现层"
    },
    {
      "group": "找不准",
      "id": "timeliness",
      "href": "problems-timeliness.html",
      "label": "版本滞后 & 多版本并存"
    },
    {
      "group": null,
      "id": "structure-metadata",
      "href": "problems-structure-metadata.html",
      "label": "页级元数据未结构化"
    },
    {
      "group": null,
      "id": "structure-cross",
      "href": "problems-structure-cross.html",
      "label": "跨页关系未显性化"
    },
    {
      "group": "读不懂",
      "id": "content-image",
      "href": "problems-content-image.html",
      "label": "图片语义缺失"
    },
    {
      "group": null,
      "id": "content-hotzone",
      "href": "problems-content-hotzone.html",
      "label": "热区信息缺失"
    },
    {
      "group": null,
      "id": "content-table",
      "href": "problems-content-table.html",
      "label": "表格语义缺失"
    },
    {
      "group": null,
      "id": "content-code",
      "href": "problems-content-code.html",
      "label": "代码块语义缺失"
    },
    {
      "group": null,
      "id": "content-link",
      "href": "problems-content-link.html",
      "label": "链接锚文本无效"
    },
    {
      "group": null,
      "id": "content-note",
      "href": "problems-content-note.html",
      "label": "警示级别缺失"
    },
    {
      "group": null,
      "id": "content-tab",
      "href": "problems-content-tab.html",
      "label": "隐藏语义缺失",
      "pageIds": ["content-tab", "content-collapse"]
    },
    {
      "group": null,
      "id": "content-carousel",
      "href": "problems-content-carousel.html",
      "label": "轮播帧语义噪声"
    },
    {
      "group": "读不顺",
      "id": "format",
      "href": "problems-format.html",
      "label": "HTML 适配不足"
    }
  ],
  "principles": [
    { "group": "找的到", "id": "a1", "href": "principles-structure-llms.html", "label": "llms.txt / sitemap 部署", "pageIds": ["structure-llms"] },
    { "group": null, "id": "content-retrievable", "href": "principles-content-retrievable.html", "label": "内容可检索", "pageIds": ["content-retrievable"] },
    { "group": "找的准", "id": "b1", "href": "principles-timeliness.html", "label": "版本号外显", "pageIds": ["timeliness"] },
    { "group": null, "id": "b2", "href": "principles-a2.html", "label": "失效/弃用状态显化", "pageIds": ["a2"] },
    { "group": null, "id": "b3", "href": "principles-structure-metadata.html", "label": "元数据丰富化", "pageIds": ["structure-metadata"] },
    { "group": "读的懂", "id": "c1", "href": "principles-image.html", "label": "图片内容转译", "pageIds": ["image"] },
    { "group": null, "id": "c2", "href": "principles-hotzone.html", "label": "图片热区转译", "pageIds": ["hotzone"] },
    { "group": null, "id": "c3", "href": "principles-table.html", "label": "表格语义化", "pageIds": ["table"] },
    { "group": null, "id": "c4", "href": "principles-code.html", "label": "代码块语义化", "pageIds": ["code"] },
    { "group": null, "id": "c5", "href": "principles-link.html", "label": "链接语义化", "pageIds": ["link"] },
    { "group": null, "id": "c6", "href": "principles-note.html", "label": "安全警示语义化", "pageIds": ["note"] },
    { "group": null, "id": "c7", "href": "principles-tab.html", "label": "隐藏语义：Tab/折叠全量展开", "pageIds": ["tab", "collapse"] },
    { "group": "读的顺", "id": "d1", "href": "principles-format.html", "label": "双轨交付", "pageIds": ["format"] }
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
    html += "<li class=\"nav-group-label\">亲和原则</li>";
    html += "<li><a href=\"principles-affinity-full.html\"" + (page === "affinity-full" ? " class=\"active\"" : "") + ">全量亲和原则</a></li>";
    html += "</ul>";
  }
  function navItemActive(item) {
    if (item.pageIds && item.pageIds.indexOf(page) !== -1) return true;
    return item.id === page;
  }

  html += "<ul class=\"sidebar-nav\">";
  if (module === "problems") {
    html += "<li class=\"nav-group-label\">本批记录</li>";
    html += "<li><a href=\"index.html\"" + (page === "index" ? " class=\"active\"" : "") + ">2026年6月目录</a></li>";
  }
  var lastGroup = null;
  items.forEach(function (item) {
    if (item.group && item.group !== lastGroup) {
      html += "<li class=\"nav-group-label\">" + item.group + "</li>";
      if (module === "problems" && item.group === "抓不到") {
        html += "<li><a href=\"problems-answer-search.html\"" + (page === "answer-search" ? " class=\"active\"" : "") + ">检索阶段</a></li>";
        html += "<li><a href=\"problems-answer-generate.html\"" + (page === "answer-generate" ? " class=\"active\"" : "") + ">生成阶段</a></li>";
      }
      lastGroup = item.group;
    }
    var active = navItemActive(item) ? " class=\"active\"" : "";
    html += "<li><a href=\"" + item.href + "\"" + active + ">" + item.label + "</a></li>";
  });
  html += "</ul>";

  aside.className = "sidebar";
  aside.innerHTML = html;
  initPageToc();
})();

/** 文档页右侧锚点目录（h2 / h3） */
function initPageToc() {
  var module = document.body.getAttribute("data-module");
  var page = document.body.getAttribute("data-page");
  if (module !== "problems" && module !== "principles") return;
  if (page === "affinity" || page === "affinity-full") return;
  if (!document.getElementById("module-sidebar")) return;

  var main = document.querySelector(".main-content");
  if (!main) return;

  var headings = main.querySelectorAll("h2, h3");
  if (!headings.length) return;

  var used = {};
  function slugify(text) {
    var base = (text || "")
      .trim()
      .toLowerCase()
      .replace(/[^\w\u4e00-\u9fff]+/g, "-")
      .replace(/^-+|-+$/g, "");
    if (!base) base = "section";
    var slug = base;
    var n = 2;
    while (used[slug]) {
      slug = base + "-" + n++;
    }
    used[slug] = true;
    return slug;
  }

  var items = [];
  headings.forEach(function (el) {
    if (el.closest(".preview-drawer")) return;
    var text = el.textContent.replace(/\s+/g, " ").trim();
    if (!text) return;
    if (!el.id) el.id = slugify(text);
    items.push({ el: el, id: el.id, text: text, level: el.tagName === "H3" ? 3 : 2 });
  });
  if (!items.length) return;

  var aside = document.createElement("aside");
  aside.id = "page-toc";
  aside.className = "page-toc";
  aside.setAttribute("aria-label", "本篇目录");

  var html = "<div class=\"page-toc-title\">本篇目录</div><nav class=\"page-toc-nav\"><ul>";
  items.forEach(function (item) {
    var cls = item.level === 3 ? " class=\"toc-h3\"" : "";
    html += "<li><a href=\"#" + item.id + "\"" + cls + " data-toc-link>" + item.text + "</a></li>";
  });
  html += "</ul></nav>";
  aside.innerHTML = html;

  var wrapper = document.querySelector(".page-wrapper");
  var drawer = wrapper && wrapper.querySelector(".preview-drawer");
  if (drawer) wrapper.insertBefore(aside, drawer);
  else if (wrapper) wrapper.appendChild(aside);

  var links = aside.querySelectorAll("[data-toc-link]");
  function setActive(id) {
    links.forEach(function (a) {
      a.classList.toggle("active", a.getAttribute("href") === "#" + id);
    });
  }

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        var visible = entries
          .filter(function (e) { return e.isIntersecting; })
          .sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
        if (visible.length) setActive(visible[0].target.id);
      },
      { rootMargin: "-80px 0px -60% 0px", threshold: 0 }
    );
    items.forEach(function (item) { observer.observe(item.el); });
  } else if (items[0]) {
    setActive(items[0].id);
  }
}
