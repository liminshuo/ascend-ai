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

  function layoutReadChart(chart, markerId) {
    var svg = chart.querySelector(".rc-wires");
    var htmlN = chart.querySelector('[data-rc="html"]');
    var mdN = chart.querySelector('[data-rc="md"]');
    var secN = chart.querySelector('[data-rc="sec"]');
    if (!svg || !htmlN || !mdN || !secN) return;

    var w = Math.max(1, chart.offsetWidth);
    var h = Math.max(1, chart.offsetHeight);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);

    var htmlB = localBox(htmlN, chart);
    var mdB = localBox(mdN, chart);
    var secB = localBox(secN, chart);

    var sx = 18;
    var sy = 16;
    var hx = htmlB.x + htmlB.w / 2;
    var mx = mdB.x + mdB.w / 2;
    var xRail = Math.min(w - 10, Math.max(htmlB.x + htmlB.w, mdB.x + mdB.w, secB.x + secB.w) + 36);
    var y3 = secB.y + secB.h / 2;
    var rad = 28;
    var guessY = htmlB.y + htmlB.h / 2;
    var llmsY = mdB.y + mdB.h / 2;

    var dGuess = roundPoly(
      [
        [sx, sy],
        [sx, guessY],
        [htmlB.x - 2, guessY]
      ],
      rad
    );
    var dLlms = roundPoly(
      [
        [sx, sy],
        [sx, llmsY],
        [mdB.x - 2, llmsY]
      ],
      rad
    );
    var dMirror = "M" + hx + " " + (htmlB.y + htmlB.h + 2) + " L" + mx + " " + (mdB.y - 4);
    if (Math.abs(hx - mx) < 2) {
      dMirror = "M" + mx + " " + (htmlB.y + htmlB.h + 2) + " L" + mx + " " + (mdB.y - 4);
    }
    var dMdSec = "M" + mx + " " + (mdB.y + mdB.h + 2) + " L" + mx + " " + (secB.y - 4);
    var dNoMirror = roundPoly(
      [
        [htmlB.x + htmlB.w, htmlB.y + htmlB.h / 2],
        [xRail, htmlB.y + htmlB.h / 2],
        [xRail, y3],
        [secB.x + secB.w + 2, y3]
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
      arm(dLlms, true, false, markerId) +
      arm(dMirror, true, false, markerId) +
      arm(dMdSec, true, true, markerId) +
      arm(dNoMirror, true, true, markerId);

    placeChip(chart.querySelector(".rc-chip-guess"), sx + 6, (sy + htmlB.y) / 2);
    placeChip(chart.querySelector(".rc-chip-yes"), sx + 6, (htmlB.y + htmlB.h + mdB.y) / 2);
    placeChip(chart.querySelector(".rc-chip-mirror"), hx + 10, (htmlB.y + htmlB.h + mdB.y) / 2);
    placeChip(chart.querySelector(".rc-chip-no"), mx + 10, (mdB.y + mdB.h + secB.y) / 2);
  }

  function dualPath(x1, y1, x2, y2) {
    var mx = x2 - 36;
    if (mx < x1 + 16) mx = (x1 + x2) / 2;
    if (Math.abs(y2 - y1) < 6) {
      return "M" + x1 + " " + y1 + " L" + x2 + " " + y2;
    }
    return roundPoly(
      [
        [x1, y1],
        [mx, y1],
        [mx, y2],
        [x2, y2]
      ],
      14
    );
  }

  function dropPath(x1, y1, x2, y2) {
    if (Math.abs(x2 - x1) < 6) {
      return "M" + x1 + " " + y1 + " L" + x2 + " " + y2;
    }
    return roundPoly(
      [
        [x1, y1],
        [x1, y2],
        [x2, y2]
      ],
      14
    );
  }

  function layoutLlmsJump(root) {
    var svg = root.querySelector(".llms-dual-wires");
    if (!svg) return;

    var w = Math.max(1, root.offsetWidth);
    var h = Math.max(1, root.offsetHeight);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);

    var defs = "";
    var paths = "";
    var markers = {};
    var uid = "w" + Math.round(root.getBoundingClientRect().left) + "-" + Math.round(root.getBoundingClientRect().top);

    function addMarker(id, color) {
      id = uid + "-" + id;
      if (markers[id]) return id;
      markers[id] = true;
      defs +=
        '<marker id="' +
        id +
        '" viewBox="0 0 8 8" markerWidth="8" markerHeight="8" refX="6.2" refY="4" orient="auto" markerUnits="userSpaceOnUse">' +
        '<path d="M0 0.6 L8 4 L0 7.4 Z" fill="' +
        color +
        '"/>' +
        "</marker>";
      return id;
    }

    function wire(from, to, color, markerId, y2mode) {
      if (!from || !to) return;
      var mid = addMarker(markerId, color);
      var a = localBox(from, root);
      var b = localBox(to, root);
      var x1 = a.x + a.w + 4;
      var y1 = a.y + a.h / 2;
      var x2 = b.x - 8;
      var y2 = y2mode === "top" ? b.y + 16 : b.y + b.h / 2;
      var d = dualPath(x1, y1, x2, y2);
      paths +=
        '<path d="' +
        d +
        '" stroke="' +
        color +
        '" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#' +
        mid +
        ')"/>' +
        '<circle cx="' +
        x1 +
        '" cy="' +
        y1 +
        '" r="3.5" fill="' +
        color +
        '"/>';
    }

    var cannFrom = root.querySelector(".llms-line.is-jump");
    var cannTo = root.querySelector(".llms-jump-to");
    if (cannFrom && cannTo) {
      wire(cannFrom, cannTo.querySelector("pre") || cannTo, "#047857", "jump", "top");
    }
    wire(
      root.querySelector(".llms-sec--ops"),
      root.querySelector(".llms-sec--ops-after"),
      "#0369a1",
      "ops",
      "mid"
    );
    wire(
      root.querySelector(".llms-sec--doc"),
      root.querySelector(".llms-sec--doc-after"),
      "#047857",
      "doc",
      "mid"
    );
    svg.innerHTML = paths ? "<defs>" + defs + "</defs>" + paths : "";
  }

  function layoutDual(root) {
    var svg = root.querySelector(".ppt-dual-wires");
    var heroMask = root.querySelector(".ppt-dual-mask--hero");
    var bodyMask = root.querySelector(".ppt-dual-mask--body");
    var moreMask = root.querySelector(".ppt-dual-mask--more");
    var mapMask = root.querySelector(".ppt-dual-mask--map");
    var heroMd = root.querySelector(".ppt-dual-block--hero");
    var bodyMd = root.querySelector(".ppt-dual-block--body");
    var moreMd = root.querySelector(".ppt-dual-block--more");
    var mapMd = root.querySelector(".ppt-dual-block--map");
    var heroLab = root.querySelector(".ppt-dual-link--hero");
    var bodyLab = root.querySelector(".ppt-dual-link--body");
    var moreLab = root.querySelector(".ppt-dual-link--more");
    if (!svg) return;
    if (root.classList.contains("ppt-dual--ascend-heading")) return;

    var w = Math.max(1, root.offsetWidth);
    var h = Math.max(1, root.offsetHeight);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);

    function wire(mask, block, color, label) {
      if (!mask || !block) return "";
      var a = localBox(mask, root);
      var b = localBox(block, root);
      var x1 = a.x + a.w;
      var y1 = a.y + a.h / 2;
      var x2 = b.x;
      var y2 = b.y + b.h / 2;
      var mx = x2 - 36;
      if (mx < x1 + 16) mx = (x1 + x2) / 2;
      var d = dualPath(x1, y1, x2, y2);
      if (label) {
        label.style.left = mx + "px";
        label.style.top = (y1 + y2) / 2 + "px";
      }
      return (
        '<path d="' +
        d +
        '" stroke="' +
        color +
        '" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
        '<circle cx="' +
        x2 +
        '" cy="' +
        y2 +
        '" r="3.5" fill="' +
        color +
        '"/>'
      );
    }

    var pane = root.querySelector(".ppt-dual-md");
    var pbox = pane ? localBox(pane, root) : null;
    function wireVis(mask, block, color, yFrac) {
      if (!mask || !block) return "";
      var a = localBox(mask, root);
      var b = localBox(block, root);
      var x1 = a.x + a.w;
      var y1 = a.y + a.h * (yFrac == null ? 0.5 : yFrac);
      var x2 = b.x;
      var y2 = b.y + b.h / 2;
      if (pbox) {
        var iy0 = Math.max(b.y, pbox.y);
        var iy1 = Math.min(b.y + b.h, pbox.y + pbox.h);
        if (iy1 > iy0) y2 = (iy0 + iy1) / 2;
      }
      var d = dualPath(x1, y1, x2, y2);
      return (
        '<path d="' +
        d +
        '" stroke="' +
        color +
        '" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
        '<circle cx="' +
        x2 +
        '" cy="' +
        y2 +
        '" r="3.5" fill="' +
        color +
        '"/>'
      );
    }

    if (root.classList.contains("ppt-dual--ascend-link")) {
      svg.innerHTML = wireVis(mapMask, mapMd, "#0369a1", 0.5);
      return;
    }
    if (!heroMask || !moreMask || !heroMd || !moreMd) return;

    if (root.classList.contains("ppt-dual--ascend") && mapMask && mapMd) {
      svg.innerHTML =
        wireVis(heroMask, heroMd, "#0369a1", 0.18) +
        wireVis(moreMask, moreMd, "#7c3aed", 0.5) +
        wireVis(mapMask, mapMd, "#7c3aed", 0.12);
      return;
    }
    if (!bodyMask || !bodyMd) return;
    svg.innerHTML =
      wire(heroMask, heroMd, "#3b6fd8", heroLab) +
      wire(bodyMask, bodyMd, "#c43d6e", bodyLab) +
      wire(moreMask, moreMd, "#1a9b8e", moreLab);
  }

  function layoutSsrLoss(root) {
    var svg = root.querySelector(".ssr-loss-wires");
    var shot = root.querySelector(".ssr-loss-frame");
    var mapLab = root.querySelector(".ssr-loss-note--map h3");
    var linkLab = root.querySelector(".ssr-loss-note--link h3");
    var hideLab = root.querySelector(".ssr-loss-note--hide h3");
    if (!svg || !shot || !mapLab || !linkLab || !hideLab) return;

    var w = Math.max(1, root.offsetWidth);
    var h = Math.max(1, root.offsetHeight);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);

    function wire(yFrac, target, color) {
      var a = localBox(shot, root);
      var b = localBox(target, root);
      var x1 = a.x + a.w;
      var y1 = a.y + a.h * yFrac;
      var x2 = b.x - 16 - 3.5;
      var y2 = b.y + b.h / 2;
      var d = dualPath(x1, y1, x2, y2);
      return (
        '<path d="' +
        d +
        '" stroke="' +
        color +
        '" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
        '<circle cx="' + x2 + '" cy="' + y2 + '" r="3.5" fill="' + color + '"/>'
      );
    }

    svg.innerHTML =
      wire(0.271, mapLab, "#ec4899") +
      wire(0.393, linkLab, "#f97316") +
      wire(0.951, hideLab, "#e11d48");
  }

  function alignSsrDeckRows() {
    var deck = document.querySelector("#practices .ssr-deck");
    if (!deck) return;
    var left = deck.querySelector(".ssr-deck-card:not(.ssr-deck-card--hits)");
    var right = deck.querySelector(".ssr-deck-card--hits");
    if (!left || !right) return;
    var link = left.querySelector(".ssr-loss-note--link");
    var hide = left.querySelector(".ssr-loss-note--hide");
    var color = right.querySelector(".ssr-deck-point--color");
    var icon = right.querySelector(".ssr-deck-point--icon");
    if (!link || !hide || !color || !icon) return;

    color.style.marginTop = "0px";
    icon.style.marginTop = "16px";

    var scale = right.getBoundingClientRect().width / (right.offsetWidth || 1) || 1;
    function gap(fromEl, toEl) {
      return (toEl.getBoundingClientRect().top - fromEl.getBoundingClientRect().top) / scale;
    }
    color.style.marginTop = gap(color, link) + "px";
    icon.style.marginTop = 16 + gap(icon, hide) + "px";
  }

  function layoutSsrDeck(root) {
    var svg = root.querySelector(".ssr-deck-wires");
    var warn = root.querySelector(".ssr-deck-hit--warn");
    var mark = root.querySelector(".ssr-deck-hit--mark");
    var colorLab = root.querySelector(".ssr-deck-point--color h3");
    var iconLab = root.querySelector(".ssr-deck-point--icon h3");
    if (!svg || !warn || !mark || !colorLab || !iconLab) return;

    var w = Math.max(1, root.offsetWidth);
    var h = Math.max(1, root.offsetHeight);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);

    function wire(hit, target, color) {
      var a = localBox(hit, root);
      var b = localBox(target, root);
      var x1 = a.x + a.w;
      var y1 = a.y + a.h / 2;
      var x2 = b.x + b.w + 16 + 3.5;
      var y2 = b.y + b.h / 2;
      var d = dropPath(x1, y1, x2, y2);
      return (
        '<path d="' +
        d +
        '" stroke="' +
        color +
        '" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
        '<circle cx="' + x2 + '" cy="' + y2 + '" r="3.5" fill="' + color + '"/>'
      );
    }

    svg.innerHTML =
      wire(warn, colorLab, "#f97316") +
      wire(mark, iconLab, "#6366f1");
  }

  function layoutImgdocCallout(hier) {
    var svg = hier.querySelector(".ppt-imgdoc-wire");
    var from = hier.querySelector(".ppt-shot-dash");
    var cols = hier.querySelectorAll(".ppt-hier-col");
    var to = cols.length > 1 ? cols[1].querySelector(".ppt-sem-fig") : null;
    if (!svg || !from || !to) return;

    var w = Math.max(1, hier.offsetWidth);
    var h = Math.max(1, hier.offsetHeight);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);

    var a = localBox(from, hier);
    var b = localBox(to, hier);
    var x1 = a.x + a.w;
    var y1 = a.y + a.h / 2;
    var x2 = b.x - 16 - 3.5;
    var y2 = b.y + b.h / 2;
    var d = dualPath(x1, y1, x2, y2);
    svg.innerHTML =
      '<path d="' +
      d +
      '" stroke="#191919" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
      '<circle cx="' +
      x2 +
      '" cy="' +
      y2 +
      '" r="3.5" fill="#191919"/>';
  }

  function layout() {
    scaleStage();
    document.querySelectorAll("#practices .reach-chart").forEach(function (chart, i) {
      if (chart.querySelector('[data-rc="html"]')) layoutReadChart(chart, "rc-arr-r-" + i);
      else layoutChart(chart, "rc-arr-" + i);
    });
    document.querySelectorAll("#practices .ppt-dual").forEach(layoutDual);
    document.querySelectorAll("#practices .ppt-hier:has(.ppt-dual-shot--vecprog)").forEach(layoutImgdocCallout);
    document.querySelectorAll("#practices .llms-dual").forEach(layoutLlmsJump);
    document.querySelectorAll("#practices .ssr-loss").forEach(layoutSsrLoss);
    alignSsrDeckRows();
    document.querySelectorAll("#practices .ssr-deck-card--hits").forEach(layoutSsrDeck);
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

    function frameIndex(frame) {
      return Array.prototype.indexOf.call(frames, frame);
    }
    function syncNav(frame) {
      var i = frameIndex(frame);
      var prevBtn = frame.querySelector(".reach-fs-prev");
      var nextBtn = frame.querySelector(".reach-fs-next");
      if (prevBtn) prevBtn.disabled = i <= 0;
      if (nextBtn) nextBtn.disabled = i < 0 || i >= frames.length - 1;
    }
    function openFs(frame) {
      frames.forEach(function (other) {
        if (other !== frame) closeFs(other);
      });
      frame.classList.add("is-fs");
      document.body.classList.add("reach-fs-open");
      var bar = frame.querySelector(".reach-fs-bar");
      if (bar) bar.hidden = false;
      syncNav(frame);
      frame.setAttribute("aria-label", closeLabel);
      layout();
    }
    function closeFs(frame) {
      if (!frame) return;
      frame.classList.remove("is-fs");
      var bar = frame.querySelector(".reach-fs-bar");
      if (bar) bar.hidden = true;
      frame.setAttribute("aria-label", frame.dataset.fsIdle || openLabel);
      if (!document.querySelector("#practices .reach-stage-frame.is-fs")) {
        document.body.classList.remove("reach-fs-open");
      }
      layout();
    }
    function stepFs(delta) {
      var current = document.querySelector("#practices .reach-stage-frame.is-fs");
      if (!current) return;
      var n = frameIndex(current) + delta;
      if (n < 0 || n >= frames.length) return;
      openFs(frames[n]);
    }

    frames.forEach(function (frame) {
      frame.dataset.fsIdle = frame.getAttribute("aria-label") || openLabel;
      var bar = frame.querySelector(".reach-fs-bar");
      var closeBtn = frame.querySelector(".reach-fs-close");
      var prevBtn = frame.querySelector(".reach-fs-prev");
      var nextBtn = frame.querySelector(".reach-fs-next");
      frame.addEventListener("click", function (e) {
        if (e.target.closest(".reach-fs-bar")) return;
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
      if (prevBtn) {
        prevBtn.addEventListener("click", function (e) {
          e.stopPropagation();
          stepFs(-1);
        });
      }
      if (nextBtn) {
        nextBtn.addEventListener("click", function (e) {
          e.stopPropagation();
          stepFs(1);
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
      if (e.key === "Escape") {
        document.querySelectorAll("#practices .reach-stage-frame.is-fs").forEach(closeFs);
        return;
      }
      if (e.key === "ArrowLeft") stepFs(-1);
      if (e.key === "ArrowRight") stepFs(1);
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
