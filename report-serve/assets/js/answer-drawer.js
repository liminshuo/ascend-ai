/** 模型回答侧滑抽屉 */
(function () {
  var drawer = document.getElementById('answer-drawer');
  if (!drawer) return;

  var panel = drawer.querySelector('.answer-drawer-panel');
  var titleEl = drawer.querySelector('#answer-drawer-title');
  var bodyEl = drawer.querySelector('.answer-drawer-body');
  var templates = document.querySelectorAll('[data-drawer-template]');
  var templateMap = {};

  templates.forEach(function (tpl) {
    templateMap[tpl.getAttribute('data-drawer-template')] = tpl;
  });

  function openDrawer(id) {
    var tpl = templateMap[id];
    if (!tpl || !bodyEl) return;

    titleEl.textContent = tpl.getAttribute('data-drawer-title') || '对话详情';
    bodyEl.innerHTML = '';
    if (tpl.content) {
      bodyEl.appendChild(tpl.content.cloneNode(true));
    } else {
      bodyEl.innerHTML = tpl.innerHTML;
    }
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    document.body.classList.add('drawer-open');
    drawer.querySelector('.answer-drawer-close').focus();
  }

  function closeDrawer() {
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('drawer-open');
  }

  document.querySelectorAll('[data-drawer-open]').forEach(function (trigger) {
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      openDrawer(trigger.getAttribute('data-drawer-open'));
    });
  });

  drawer.querySelectorAll('[data-drawer-close]').forEach(function (el) {
    el.addEventListener('click', closeDrawer);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
      closeDrawer();
    }
  });

  if (panel) {
    panel.addEventListener('click', function (e) {
      e.stopPropagation();
    });
  }

  var drawerParam = new URLSearchParams(window.location.search).get('drawer');
  if (drawerParam && templateMap[drawerParam]) {
    openDrawer(drawerParam);
  }
})();
