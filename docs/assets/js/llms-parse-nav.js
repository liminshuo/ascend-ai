(function () {
  var VENDORS = {
    mintlify: {
      label: "Mintlify",
      href: "principles-llms-parse-mintlify.html",
      layers: [
        {
          id: "root",
          idx: "第 1 层 · 根",
          title: "mintlify.com/llms.txt",
          href: "principles-llms-parse-mintlify.html"
        },
        {
          id: "docs",
          idx: "第 2 层 · 分册",
          title: "mintlify.com/docs/llms.txt",
          href: "principles-llms-parse-mintlify-docs.html"
        },
        {
          id: "path",
          idx: "读取路径",
          title: "编辑器快捷键",
          href: "principles-llms-parse-mintlify-path.html"
        },
        {
          id: "path-cross",
          idx: "读取路径",
          title: "CI 部署排障",
          href: "principles-llms-parse-mintlify-path-cross.html"
        },
        {
          id: "path-insight",
          idx: "读取路径",
          title: "洞察",
          href: "principles-llms-parse-mintlify-path-insight.html"
        }
      ]
    },
    nvidia: {
      label: "NVIDIA",
      href: "principles-llms-parse-nvidia.html",
      layers: [
        {
          id: "root",
          idx: "第 1 层 · 集团根",
          title: "nvidia.com/llms.txt",
          href: "principles-llms-parse-nvidia.html"
        },
        {
          id: "docs",
          idx: "第 2 层 · 站点",
          title: "docs.nvidia.com/llms.txt",
          href: "principles-llms-parse-nvidia-docs.html"
        },
        {
          id: "cuda",
          idx: "第 3 层 · 产品线",
          title: "docs.nvidia.com/cuda/llms.txt",
          href: "principles-llms-parse-nvidia-cuda.html"
        },
        {
          id: "path",
          idx: "路径分析",
          title: "编程模型",
          href: "principles-llms-parse-nvidia-path.html"
        },
        {
          id: "path-cross",
          idx: "路径分析",
          title: "安装与编程模型",
          href: "principles-llms-parse-nvidia-path-cross.html"
        },
        {
          id: "path-insight",
          idx: "路径分析",
          title: "洞察",
          href: "principles-llms-parse-nvidia-path-insight.html"
        },
        {
          id: "hiascend",
          idx: "对照",
          title: "hiascend.com/llms.txt",
          href: "principles-llms-parse-hiascend.html"
        },
        {
          id: "root-compare",
          idx: "对照",
          title: "根清单体量",
          href: "principles-llms-parse-root-compare.html"
        }
      ]
    }
  };

  var aside = document.getElementById("llms-parse-nav");
  if (!aside) return;

  var vendorId = aside.getAttribute("data-vendor");
  var layerId = aside.getAttribute("data-layer");
  var vendor = VENDORS[vendorId];
  if (!vendor) return;

  var html = '<div class="model-nav-label">厂商</div>';
  Object.keys(VENDORS).forEach(function (id) {
    var v = VENDORS[id];
    html +=
      '<a class="nav-vendor' +
      (id === vendorId ? " is-active" : "") +
      '" href="' +
      v.href +
      '">' +
      v.label +
      "</a>";
  });
  html += '<div class="model-nav-label is-sub">解析对象</div>';
  vendor.layers.forEach(function (layer) {
    html +=
      '<a class="nav-model-card' +
      (layer.id === layerId ? " is-active" : "") +
      '" href="' +
      layer.href +
      '"><span class="idx">' +
      layer.idx +
      '</span><span class="card-title">' +
      layer.title +
      "</span></a>";
  });
  aside.innerHTML = html;
})();
