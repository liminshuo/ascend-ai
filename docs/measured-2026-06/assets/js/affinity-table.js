(function () {
  var table = document.querySelector(".data-table--affinity");
  if (!table) return;

  var tbody = table.querySelector("tbody");
  var filter = table.querySelector(".affinity-source-filter");
  if (!tbody || !filter) return;

  var originalHtml = tbody.innerHTML;

  function getRowSource(row) {
    if (row.querySelector(".affinity-source--problems")) return "problems";
    if (row.querySelector(".affinity-source--content")) return "content";
    return "";
  }

  function annotateDim(rows) {
    var currentDim = "";
    rows.forEach(function (row) {
      var dimCell = row.querySelector("td.col-dim");
      if (dimCell) currentDim = dimCell.textContent.trim();
      row.dataset.dim = currentDim;
    });
  }

  function rebuildRowspans(visible) {
    var i = 0;
    while (i < visible.length) {
      var dim = visible[i].dataset.dim;
      var j = i + 1;
      while (j < visible.length && visible[j].dataset.dim === dim) j++;
      var span = j - i;
      var first = visible[i];
      var dimTd = first.querySelector("td.col-dim");
      if (!dimTd) {
        dimTd = document.createElement("td");
        dimTd.className = "col-dim";
        first.insertBefore(dimTd, first.firstChild);
      }
      dimTd.textContent = dim;
      if (span > 1) dimTd.setAttribute("rowspan", String(span));
      else dimTd.removeAttribute("rowspan");
      for (var k = i + 1; k < j; k++) {
        var extra = visible[k].querySelector("td.col-dim");
        if (extra) extra.remove();
      }
      i = j;
    }
  }

  function applyFilter(value) {
    tbody.innerHTML = originalHtml;
    var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr[id]"));
    annotateDim(rows);
    rows.forEach(function (row) {
      var source = getRowSource(row);
      row.hidden = value !== "all" && source !== value;
    });
    rebuildRowspans(rows.filter(function (row) {
      return !row.hidden;
    }));
  }

  filter.addEventListener("change", function () {
    applyFilter(filter.value);
  });
})();
