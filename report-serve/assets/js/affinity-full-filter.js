/** 全量亲和原则页：按调整项类型筛选，支持五层目标多表格布局 */
(function () {
  if (document.body.getAttribute("data-page") !== "affinity-full") return;

  var adjustFilter = document.getElementById("affinity-full-filter");
  var countEl = document.getElementById("affinity-filter-count");
  var catalog = document.getElementById("affinity-catalog");
  if (!adjustFilter || !catalog) return;

  var rows = Array.prototype.slice.call(
    catalog.querySelectorAll("tr[id]")
  );

  function adjustMatches(row, value) {
    if (value === "all") return true;
    if (value === "content") return row.dataset.adjustContent === "1";
    if (value === "design") return row.dataset.adjustDesign === "1";
    if (value === "dev") return row.dataset.adjustDev === "1";
    return true;
  }

  function applyFilter() {
    var aVal = adjustFilter.value;
    var count = 0;

    rows.forEach(function (row) {
      var show = adjustMatches(row, aVal);
      row.hidden = !show;
      if (show) count++;
    });

    // 节点分组下所有行都被隐藏时，同时隐藏该组标题和表格
    var groupTitles = Array.prototype.slice.call(
      catalog.querySelectorAll(".affinity-group-title")
    );
    groupTitles.forEach(function (title) {
      var wrap = title.nextElementSibling;
      if (!wrap) return;
      var hasVisible = Array.prototype.slice.call(
        wrap.querySelectorAll("tr[id]")
      ).some(function (r) { return !r.hidden; });
      title.hidden = !hasVisible;
      wrap.hidden = !hasVisible;
    });

    if (countEl) countEl.textContent = count + " 项";
  }

  adjustFilter.addEventListener("change", applyFilter);

  function revealPrincipleRow(id) {
    if (!id || id.indexOf("principle-full-") !== 0) return null;
    var row = document.getElementById(id);
    if (!row) return null;

    adjustFilter.value = "all";
    applyFilter();

    return row;
  }

  function scrollToPrincipleHash() {
    var id = (location.hash || "").replace(/^#/, "");
    var row = revealPrincipleRow(id);
    if (!row) return;

    window.requestAnimationFrame(function () {
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      row.classList.add("principle-row--target");
      window.setTimeout(function () {
        row.classList.remove("principle-row--target");
      }, 2200);
    });
  }

  applyFilter();
  scrollToPrincipleHash();
  window.addEventListener("hashchange", scrollToPrincipleHash);
})();
