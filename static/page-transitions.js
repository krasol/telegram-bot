(function () {
  const DURATION = 230;

  function applyEnterAnimation() {
    const type = sessionStorage.getItem("pageTransition") || "forward";
    sessionStorage.removeItem("pageTransition");

    document.body.classList.remove(
      "page-enter-forward",
      "page-enter-back",
      "page-enter-menu"
    );

    requestAnimationFrame(() => {
      document.body.classList.add("page-enter-" + type);
      window.setTimeout(() => {
        document.body.classList.remove("page-enter-" + type);
      }, 120);
    });
  }

  function isSamePage(url) {
    return (
      url.pathname === window.location.pathname &&
      url.search === window.location.search &&
      url.hash
    );
  }

  function getTransitionType(link) {
    const manual = link.dataset.transition;
    if (manual) return manual;

    const href = link.getAttribute("href") || "";
    const text = (link.textContent || "").toLowerCase();
    const html = (link.innerHTML || "").toLowerCase();
    const aria = (link.getAttribute("aria-label") || "").toLowerCase();

    if (
      link.closest(".nav") ||
      link.closest("nav") ||
      link.classList.contains("nav-link") ||
      link.classList.contains("tab") ||
      link.classList.contains("menu-link")
    ) {
      return "menu";
    }

    if (
      link.classList.contains("back") ||
      link.classList.contains("back-btn") ||
      href === "javascript:history.back()" ||
      href.includes("history.back") ||
      href.includes("back") ||
      text.includes("назад") ||
      aria.includes("назад") ||
      html.includes("back.png")
    ) {
      return "back";
    }

    return "forward";
  }

  function shouldSkip(link, event) {
    if (!link) return true;
    if (event.defaultPrevented) return true;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return true;
    if (link.target && link.target !== "_self") return true;

    const href = link.getAttribute("href");
    if (!href || href === "#" || href.startsWith("javascript:")) return true;
    if (href.startsWith("mailto:") || href.startsWith("tel:")) return true;

    return false;
  }

  document.addEventListener("DOMContentLoaded", applyEnterAnimation);

  document.addEventListener("click", function (event) {
    const link = event.target.closest("a");
    if (shouldSkip(link, event)) return;

    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin) return;
    if (isSamePage(url)) return;

    event.preventDefault();

    const type = getTransitionType(link);
    sessionStorage.setItem("pageTransition", type);

    document.body.classList.remove(
      "page-exit-forward",
      "page-exit-back",
      "page-exit-menu"
    );
    document.body.classList.add("page-exit-" + type);

    window.setTimeout(function () {
      window.location.href = url.href;
    }, DURATION);
  });

  window.addEventListener("popstate", function () {
    sessionStorage.setItem("pageTransition", "back");
  });
})();