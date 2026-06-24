document.addEventListener('DOMContentLoaded', function () {
  const items = document.querySelectorAll('.spread-item');

  items.forEach(function (item) {
    item.addEventListener('click', function () {
      items.forEach(function (el) { el.classList.remove('is-active'); });
      item.classList.add('is-active');
    });
  });
});
