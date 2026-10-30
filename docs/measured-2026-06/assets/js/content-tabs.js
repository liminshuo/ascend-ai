(function () {
  function activateTab(root, target) {
    var tabs = root.querySelectorAll('[role="tab"]');
    var panels = root.querySelectorAll('[role="tabpanel"]');

    tabs.forEach(function (tab) {
      var active = tab.getAttribute('data-tab') === target;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    panels.forEach(function (panel) {
      var active = panel.getAttribute('data-tab-panel') === target;
      panel.classList.toggle('is-active', active);
      panel.hidden = !active;
    });
  }

  function initialTab() {
    var hash = (location.hash || '').replace('#', '');
    if (hash === 'solution' || hash === 'problem') return hash;
    var params = new URLSearchParams(location.search);
    var q = params.get('tab');
    if (q === 'solution' || q === 'problem') return q;
    return null;
  }

  document.querySelectorAll('[data-content-tabs]').forEach(function (root) {
    var tabs = root.querySelectorAll('[role="tab"]');
    var panels = root.querySelectorAll('[role="tabpanel"]');

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        activateTab(root, tab.getAttribute('data-tab'));
      });
    });

    var start = initialTab();
    if (start) {
      activateTab(root, start);
    }
  });
})();
