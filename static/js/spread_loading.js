document.addEventListener('DOMContentLoaded', () => {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
    }

    const screen = document.querySelector('[data-page="spread-loading"]');
    const nextUrl = screen ? screen.dataset.nextUrl : '/spreads';

    setTimeout(() => {
        window.location.href = nextUrl || '/spreads';
    }, 2800);
});
