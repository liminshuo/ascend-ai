/** 测试页面侧滑预览抽屉（挤压主内容区） */
(function () {
  var wrapper = document.querySelector('.page-wrapper');
  var drawer = document.getElementById('preview-drawer');
  if (!wrapper || !drawer) return;

  var frame = drawer.querySelector('.preview-drawer-frame');

  function openDrawer() {
    wrapper.classList.add('is-preview-open');
    drawer.setAttribute('aria-hidden', 'false');
    if (frame && !frame.getAttribute('src')) {
      frame.setAttribute('src', frame.getAttribute('data-preview-src') || '');
    }
    var closeBtn = drawer.querySelector('[data-preview-drawer-close]');
    if (closeBtn) closeBtn.focus();
  }

  function closeDrawer() {
    wrapper.classList.remove('is-preview-open');
    drawer.setAttribute('aria-hidden', 'true');
  }

  document.querySelectorAll('[data-preview-drawer-open]').forEach(function (trigger) {
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      openDrawer();
    });
  });

  document.querySelectorAll('[data-preview-drawer-close]').forEach(function (el) {
    el.addEventListener('click', closeDrawer);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && wrapper.classList.contains('is-preview-open')) {
      closeDrawer();
    }
  });
})();
