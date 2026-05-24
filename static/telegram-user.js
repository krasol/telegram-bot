const tg = window.Telegram?.WebApp;

tg?.ready();
tg?.expand();

const tgUser = tg?.initDataUnsafe?.user;

if (tgUser) {
    const firstName = tgUser.first_name || '';
    const lastName = tgUser.last_name || '';
    const fullName = `${firstName} ${lastName}`.trim();
    const username = tgUser.username ? '@' + tgUser.username : '';

    document.querySelectorAll('[data-tg-name]').forEach(el => {
        el.textContent = fullName || 'Пользователь';
    });

    document.querySelectorAll('[data-tg-username]').forEach(el => {
        el.textContent = username;
    });

    document.querySelectorAll('[data-tg-avatar]').forEach(el => {
        if (tgUser.photo_url) {
            el.src = tgUser.photo_url;
            el.style.display = 'block';
        }
    });

    fetch('/save-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user: tgUser,
            initData: tg?.initData || ''
        })
    }).catch(() => {});
}
