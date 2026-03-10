// Инициализация Telegram Web App
let tg = window.Telegram.WebApp;

// Раскрываем на весь экран
tg.expand();

// Получаем информацию о пользователе
const user = tg.initDataUnsafe?.user;
const userDataDiv = document.getElementById('userData');

if (user) {
    userDataDiv.innerHTML = `
        <p><strong>ID:</strong> ${user.id}</p>
        <p><strong>Имя:</strong> ${user.first_name} ${user.last_name || ''}</p>
        <p><strong>Username:</strong> ${user.username || 'не указан'}</p>
        <p><strong>Язык:</strong> ${user.language_code || 'ru'}</p>
    `;
} else {
    userDataDiv.innerHTML = '<p>Информация о пользователе недоступна</p>';
}

// Счетчик
let count = 0;
const counterElement = document.getElementById('counter');
const incrementBtn = document.getElementById('incrementBtn');
const resetBtn = document.getElementById('resetBtn');
const sendDataBtn = document.getElementById('sendDataBtn');
const closeBtn = document.getElementById('closeBtn');
const checkThemeBtn = document.getElementById('checkTheme');
const themeNameSpan = document.getElementById('themeName');

// Увеличиваем счетчик
incrementBtn.addEventListener('click', () => {
    count++;
    counterElement.textContent = count;
    
    // Вибрация (если поддерживается)
    if (tg.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('light');
    }
});

// Сбрасываем счетчик
resetBtn.addEventListener('click', () => {
    count = 0;
    counterElement.textContent = count;
});

// Отправляем данные
sendDataBtn.addEventListener('click', () => {
    const data = {
        count: count,
        user_id: user?.id,
        username: user?.username,
        timestamp: new Date().toISOString()
    };
    
    tg.sendData(JSON.stringify(data));
    
    // Показываем уведомление
    if (tg.showPopup) {
        tg.showPopup({
            title: 'Успешно!',
            message: 'Данные отправлены боту',
            buttons: [{type: 'ok'}]
        });
    }
});

// Закрываем приложение
closeBtn.addEventListener('click', () => {
    tg.close();
});

// Проверяем тему
checkThemeBtn.addEventListener('click', () => {
    const theme = tg.colorScheme || 'light';
    themeNameSpan.textContent = theme;
    
    if (tg.HapticFeedback) {
        tg.HapticFeedback.selectionChanged();
    }
});

// Обновляем информацию о теме при загрузке
themeNameSpan.textContent = tg.colorScheme || 'light';

// Настраиваем главную кнопку (опционально)
tg.MainButton.setText('Отправить');
tg.MainButton.onClick(() => {
    sendDataBtn.click();
});

// Сообщаем Telegram, что приложение готово
tg.ready();

// Логируем информацию для отладки
console.log('Telegram Mini App инициализирован');
console.log('User:', user);
console.log('Theme:', tg.colorScheme);