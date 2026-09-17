(function () {
  var STAGE_W = 1920;
  var STAGE_H = 1080;

  function isFs(frame) {
    return !!(frame && frame.classList.contains("is-fs"));
  }

  function scaleStage() {
    document.querySelectorAll("#practices .reach-stage-frame").forEach(function (frame) {
      var stage = frame.querySelector(".reach-stage");
      if (!stage) return;
      var fw = frame.clientWidth;
      var fh = frame.clientHeight || (fw * STAGE_H) / STAGE_W;
      var s = isFs(frame)
        ? Math.min(fw / STAGE_W, fh / STAGE_H)
        : fw / STAGE_W;
      s = s || 1;
      stage.style.transform = "scale(" + s + ")";
      if (isFs(frame)) {
        stage.style.marginLeft = Math.max(0, (fw - STAGE_W * s) / 2) + "px";
        stage.style.marginTop = Math.max(0, (fh - STAGE_H * s) / 2) + "px";
      } else {
        stage.style.marginLeft = "";
        stage.style.marginTop = "";
      }
    });
  }

  function localBox(el, root) {
    var er = el.getBoundingClientRect();
    var rr = root.getBoundingClientRect();
    var scale = rr.width / (root.offsetWidth || STAGE_W) || 1;
    return {
      x: (er.left - rr.left) / scale,
      y: (er.top - rr.top) / scale,
      w: er.width / scale,
      h: er.height / scale
    };
  }

  function roundPoly(pts, r) {
    if (pts.length < 2) return "";
    var d = "M" + pts[0][0] + " " + pts[0][1];
    if (pts.length === 2) {
      return d + " L" + pts[1][0] + " " + pts[1][1];
    }
    for (var i = 1; i < pts.length - 1; i++) {
      var ax = pts[i - 1][0];
      var ay = pts[i - 1][1];
      var bx = pts[i][0];
      var by = pts[i][1];
      var cx = pts[i + 1][0];
      var cy = pts[i + 1][1];
      var d1 = Math.hypot(bx - ax, by - ay) || 1;
      var d2 = Math.hypot(cx - bx, cy - by) || 1;
      var rr = Math.min(r, d1 / 2, d2 / 2);
      var ix = bx - ((bx - ax) / d1) * rr;
      var iy = by - ((by - ay) / d1) * rr;
      var ox = bx + ((cx - bx) / d2) * rr;
      var oy = by + ((cy - by) / d2) * rr;
      d += " L" + ix + " " + iy + " Q" + bx + " " + by + " " + ox + " " + oy;
    }
    var last = pts[pts.length - 1];
    d += " L" + last[0] + " " + last[1];
    return d;
  }

  function arm(d, arrow, dashed, markerId) {
    return (
      '<path d="' +
      d +
      '" stroke="#191919" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"' +
      (dashed ? ' stroke-dasharray="6 5"' : "") +
      (arrow ? ' marker-end="url(#' + markerId + ')"' : "") +
      "/>"
    );
  }

  function placeChip(chip, x, y) {
    if (!chip) return;
    chip.style.left = x + "px";
    chip.style.top = y + "px";
    chip.style.transform = "translate(0, -50%)";
  }

  function layoutChart(chart, markerId) {
    var svg = chart.querySelector(".rc-wires");
    var gate = chart.querySelector('[data-rc="gate"]');
    var llms = chart.querySelector('[data-rc="llms"]');
    var sitemap = chart.querySelector('[data-rc="sitemap"]');
    var leaf = chart.querySelector('[data-rc="leaf"]');
    if (!svg || !gate || !llms || !sitemap || !leaf) return;

    var w = Math.max(1, chart.offsetWidth);
    var h = Math.max(1, chart.offsetHeight);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);

    var g = localBox(gate, chart);
    var a = localBox(llms, chart);
    var b = localBox(sitemap, chart);
    var c = localBox(leaf, chart);

    var sx = 18;
    var sy = g.y + g.h;
    var cx = a.x + a.w / 2;
    var xRail = Math.min(w - 10, Math.max(a.x + a.w, b.x + b.w, c.x + c.w) + 36);
    var y3 = c.y + c.h / 2;
    var rad = 28;
    var yesY = a.y - 28;

    var dGuess = roundPoly(
      [
        [sx, sy],
        [sx, y3],
        [c.x - 2, y3]
      ],
      rad
    );
    var dYes = roundPoly(
      [
        [sx, Math.max(sy + 8, yesY - 24)],
        [sx, yesY],
        [cx, yesY],
        [cx, a.y - 4]
      ],
      rad
    );
    var dNo = "M" + cx + " " + (a.y + a.h + 2) + " L" + cx + " " + (b.y - 4);
    var dNo2 = "M" + cx + " " + (b.y + b.h + 2) + " L" + cx + " " + (c.y - 4);
    var dHit = roundPoly(
      [
        [a.x + a.w, a.y + a.h / 2],
        [xRail, a.y + a.h / 2],
        [xRail, y3],
        [c.x + c.w + 2, y3]
      ],
      rad
    );

    svg.innerHTML =
      "<defs>" +
      '<marker id="' +
      markerId +
      '" viewBox="0 0 8 8" markerWidth="8" markerHeight="8" refX="6.2" refY="4" orient="auto" markerUnits="userSpaceOnUse">' +
      '<path d="M0 0.6 L8 4 L0 7.4 Z" fill="#191919"/>' +
      "</marker>" +
      "</defs>" +
      '<circle cx="' + sx + '" cy="' + sy + '" r="2.2" fill="#fff" stroke="#191919" stroke-width="1.5"/>' +
      arm(dGuess, true, false, markerId) +
      arm(dYes, true, false, markerId) +
      arm(dNo, true, true, markerId) +
      arm(dNo2, true, true, markerId) +
      arm(dHit, true, false, markerId);

    placeChip(chart.querySelector(".rc-chip-yes"), cx + 8, yesY);
    placeChip(chart.querySelector(".rc-chip-no"), cx + 10, (a.y + a.h + b.y) / 2);
    placeChip(chart.querySelector(".rc-chip-guess"), 4, (b.y + b.h + y3) / 2);
  }

  function layout() {
    scaleStage();
    document.querySelectorAll("#practices .reach-chart").forEach(function (chart, i) {
      layoutChart(chart, "rc-arr-" + i);
    });
  }

  var t;
  function onResize() {
    clearTimeout(t);
    t = setTimeout(layout, 40);
  }

  window.addEventListener("resize", onResize);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", layout);
  else layout();
  window.addEventListener("load", layout);
  if (typeof ResizeObserver !== "undefined") {
    document.querySelectorAll("#practices .reach-stage-frame").forEach(function (frame) {
      new ResizeObserver(layout).observe(frame);
    });
  }

  (function bindFs() {
    var frames = document.querySelectorAll("#practices .reach-stage-frame");
    if (!frames.length) return;
    var openLabel = "点击放大到全屏";
    var closeLabel = "全屏，按 Esc 或点关闭退出";

    function openFs(frame) {
      frames.forEach(function (other) {
        if (other !== frame) closeFs(other);
      });
      frame.classList.add("is-fs");
      document.body.classList.add("reach-fs-open");
      var closeBtn = frame.querySelector(".reach-fs-close");
      if (closeBtn) closeBtn.hidden = false;
      frame.setAttribute("aria-label", closeLabel);
      layout();
    }
    function closeFs(frame) {
      if (!frame) return;
      frame.classList.remove("is-fs");
      var closeBtn = frame.querySelector(".reach-fs-close");
      if (closeBtn) closeBtn.hidden = true;
      frame.setAttribute("aria-label", frame.dataset.fsIdle || openLabel);
      if (!document.querySelector("#practices .reach-stage-frame.is-fs")) {
        document.body.classList.remove("reach-fs-open");
      }
      layout();
    }

    frames.forEach(function (frame) {
      frame.dataset.fsIdle = frame.getAttribute("aria-label") || openLabel;
      var closeBtn = frame.querySelector(".reach-fs-close");
      frame.addEventListener("click", function (e) {
        if (e.target.closest(".reach-fs-close")) return;
        if (isFs(frame)) {
          if (e.target.closest(".reach-stage")) return;
          closeFs(frame);
          return;
        }
        openFs(frame);
      });
      if (closeBtn) {
        closeBtn.addEventListener("click", function (e) {
          e.stopPropagation();
          closeFs(frame);
        });
      }
      frame.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (isFs(frame)) closeFs(frame);
          else openFs(frame);
        }
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      document.querySelectorAll("#practices .reach-stage-frame.is-fs").forEach(closeFs);
    });
  })();

  (function cloneNvSeq() {
    var src = document.getElementById("nv-seq-src");
    var host = document.querySelector("#practices .ppt-nv-seq");
    if (!src || !host || host.firstChild) return;
    var clone = src.cloneNode(true);
    clone.removeAttribute("id");
    clone.querySelectorAll("[id]").forEach(function (el) {
      el.id = "ppt-" + el.id;
    });
    clone.querySelectorAll("*").forEach(function (n) {
      if (!n.attributes) return;
      Array.prototype.forEach.call(n.attributes, function (a) {
        if (a.name === "id" || !a.value) return;
        if (a.value.indexOf("#") === -1 && a.value.indexOf("mat-") === -1) return;
        n.setAttribute(
          a.name,
          a.value
            .replace(/url\(#(?!ppt-)([^)]+)\)/g, "url(#ppt-$1)")
            .replace(/(^|\s)(?!ppt-)(mat-title|mat-desc)\b/g, "$1ppt-$2")
        );
      });
    });
    host.appendChild(clone);
    var legend = clone.querySelector(".seq-legend");
    var nv = host.closest(".ppt-nv");
    if (legend && nv) nv.appendChild(legend);
  })();
})();
