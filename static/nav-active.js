document.addEventListener('DOMContentLoaded', function () {
  var path = window.location.pathname.replace(/\/$/, '') || '/';

  document.querySelectorAll('.nav a').forEach(function (link) {
    var href = (link.getAttribute('href') || '').replace(/\/$/, '') || '/';
    var active =
      (path === '/' && href === '/') ||
      (href !== '/' && path === href) ||
      (href === '/birthdate' && path.indexOf('/birthdate') === 0);

    link.classList.toggle('active', active);

    var img = link.querySelector('img');
    if (img) {
      var activeSrc = img.getAttribute('data-active-src');
      var inactiveSrc = img.getAttribute('data-inactive-src');
      if (active && activeSrc) img.src = activeSrc;
      if (!active && inactiveSrc) img.src = inactiveSrc;
    }
  });
});
