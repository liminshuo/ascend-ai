(function () {
  var title = window.SITE_CONFIG && window.SITE_CONFIG.title;
  if (!title) return;
  var logo = document.querySelector('.site-logo');
  if (logo) logo.textContent = title;
})();
