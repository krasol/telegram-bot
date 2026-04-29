document.addEventListener('DOMContentLoaded', function () {
  var path = window.location.pathname.replace(/\/$/, '') || '/';
  var links = document.querySelectorAll('.nav a, .bottom-nav a');

  links.forEach(function (link) {
    var href = (link.getAttribute('href') || '').replace(/\/$/, '') || '/';
    var isActive =
      (path === '/' && href === '/') ||
      (href !== '/' && path === href) ||
      (href === '/birthdate' && path.indexOf('/birthdate') === 0);

    link.classList.toggle('active', isActive);

    var img = link.querySelector('img');
    if (img) {
      var activeSrc = img.getAttribute('data-active-src');
      var inactiveSrc = img.getAttribute('data-inactive-src');

      if (isActive && activeSrc) {
        img.setAttribute('src', activeSrc);
      }

      if (!isActive && inactiveSrc) {
        img.setAttribute('src', inactiveSrc);
      }
    }
  });
});
