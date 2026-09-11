(function () {
  function reset(link) {
    link.style.marginTop = "";
    link.style.height = "";
    link.style.width = "";
    link.style.flex = "";
    link.style.flexBasis = "";
    link.style.alignSelf = "";
    link.removeAttribute("preserveAspectRatio");
  }

  function goCenterY(go, trackRect) {
    var r = go.getBoundingClientRect();
    return r.top + r.height / 2 - trackRect.top;
  }

  function pinWidth(el, w) {
    el.style.width = w + "px";
    el.style.flex = "0 0 " + w + "px";
    el.style.flexBasis = w + "px";
    el.style.alignSelf = "flex-start";
  }

  function defs(suffix) {
    var fwd = "wf-arr-fwd-" + suffix;
    var back = "wf-arr-back-" + suffix;
    return {
      fwd: fwd,
      back: back,
      html:
        "<defs>" +
        '<marker id="' +
        fwd +
        '" viewBox="0 0 6 6" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto" markerUnits="userSpaceOnUse">' +
        '<path d="M0 0.5 L6 3 L0 5.5 Z" fill="#191919"/>' +
        "</marker>" +
        '<marker id="' +
        back +
        '" viewBox="0 0 6 6" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto" markerUnits="userSpaceOnUse">' +
        '<path d="M0 0.5 L6 3 L0 5.5 Z" fill="#737373"/>' +
        "</marker>" +
        "</defs>"
    };
  }

  function layout() {
    var track = document.querySelector(".wf-track");
    if (!track) return;
    var kids = Array.prototype.slice.call(track.children);
    if (window.matchMedia("(max-width: 900px)").matches) {
      kids.forEach(function (el) {
        if (el.classList.contains("wf-link")) reset(el);
      });
      return;
    }
    var trackRect = track.getBoundingClientRect();
    kids.forEach(function (el, i) {
      if (!el.classList.contains("wf-link")) return;
      var prev = kids[i - 1];
      var next = kids[i + 1];
      if (!prev) return;
      var gos = prev.querySelectorAll(".wf-row--go");
      if (!gos.length) return;
      var mk = defs(i);

      if (next && next.classList.contains("wf-split") && gos.length > 1) {
        var ends = next.querySelectorAll(".wf-node");
        var n = Math.min(gos.length, ends.length);
        var pts = [];
        var minY = Infinity;
        var maxY = -Infinity;
        for (var k = 0; k < n; k++) {
          var y0 = goCenterY(gos[k], trackRect);
          var er = ends[k].getBoundingClientRect();
          var y1 = er.top + er.height / 2 - trackRect.top;
          pts.push({ y0: y0, y1: y1 });
          minY = Math.min(minY, y0, y1);
          maxY = Math.max(maxY, y0, y1);
        }
        var pad = 20;
        var h = Math.max(16, maxY - minY + pad * 2);
        var w = 56;
        pinWidth(el, w);
        el.style.marginTop = minY - pad + "px";
        el.style.height = h + "px";
        el.setAttribute("viewBox", "0 0 " + w + " " + h);
        el.removeAttribute("preserveAspectRatio");
        var o = minY - pad;
        var a0 = pts[0].y0 - o;
        var b0 = pts[0].y1 - o;
        var a1 = pts[1].y0 - o;
        var b1 = pts[1].y1 - o;
        var backY = (a0 + a1) / 2;
        var backStart = b0 + 10;
        el.innerHTML =
          mk.html +
          '<path d="M4 ' + a0 + " C 20 " + (a0 - 4) + ", 32 " + (b0 - 10) + ", 46 " + b0 +
          '" stroke="#191919" stroke-width="2.5" fill="none" stroke-linecap="round" marker-end="url(#' + mk.fwd + ')"/>' +
          '<circle cx="4" cy="' + a0 + '" r="3.2" fill="#fff" stroke="#191919" stroke-width="2"/>' +
          '<text x="22" y="' + (a0 - 8) + '" text-anchor="middle" font-size="10" font-weight="700" fill="#191919">1</text>' +
          '<path d="M46 ' + backStart + " C 30 " + backStart + ", 22 " + backY + ", 10 " + backY +
          '" stroke="#737373" stroke-width="2" fill="none" stroke-linecap="round" stroke-dasharray="5 3.5" marker-end="url(#' + mk.back + ')"/>' +
          '<text x="30" y="' + (backY + 4) + '" text-anchor="middle" font-size="9" font-weight="700" fill="#737373">回</text>' +
          '<path d="M4 ' + a1 + " C 20 " + (a1 + 4) + ", 32 " + (b1 + 10) + ", 46 " + b1 +
          '" stroke="#191919" stroke-width="2.5" fill="none" stroke-linecap="round" marker-end="url(#' + mk.fwd + ')"/>' +
          '<circle cx="4" cy="' + a1 + '" r="3.2" fill="#fff" stroke="#191919" stroke-width="2"/>' +
          '<text x="22" y="' + (a1 + 14) + '" text-anchor="middle" font-size="10" font-weight="700" fill="#191919">2</text>';
        return;
      }

      pinWidth(el, 40);
      var y = goCenterY(gos[0], trackRect);
      el.style.height = "16px";
      el.style.marginTop = y - 8 + "px";
      el.setAttribute("viewBox", "0 0 40 16");
      el.setAttribute("preserveAspectRatio", "xMidYMid meet");
      el.innerHTML =
        mk.html +
        '<path d="M4 8 H30" stroke="#191919" stroke-width="2.5" fill="none" stroke-linecap="round" marker-end="url(#' +
        mk.fwd +
        ')"/>' +
        '<circle cx="4" cy="8" r="3.2" fill="#fff" stroke="#191919" stroke-width="2"/>';
    });
  }

  window.addEventListener("resize", layout);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", layout);
  else layout();
})();
