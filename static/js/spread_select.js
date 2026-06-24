document.addEventListener('DOMContentLoaded', () => {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
    }

    const screen = document.querySelector('[data-page="spread-select"]');
    const cards = Array.from(document.querySelectorAll('.select-card'));
    const slots = Array.from(document.querySelectorAll('.choice-item'));
    const nextUrl = screen ? screen.dataset.nextUrl : '/loading';
    const selected = [];
    let locked = false;

    const haptic = (type = 'light') => {
        const tg = window.Telegram && window.Telegram.WebApp;
        if (tg && tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred(type);
        }
    };

    const refreshSlots = () => {
        slots.forEach((slot, index) => {
            const state = slot.querySelector('.choice-state');
            if (selected[index]) {
                slot.classList.add('filled');
                state.textContent = `Карта ${index + 1} выбрана`;
            } else {
                slot.classList.remove('filled');
                state.textContent = 'Ожидаем выбора...';
            }
        });

        cards.forEach((card) => {
            const order = card.querySelector('.card-order');
            const selectedIndex = selected.indexOf(card);
            if (selectedIndex >= 0) {
                card.classList.add('selected');
                order.textContent = selectedIndex + 1;
            } else {
                card.classList.remove('selected');
                order.textContent = '';
            }
        });
    };

    cards.forEach((card) => {
        card.addEventListener('click', () => {
            if (locked) return;

            const currentIndex = selected.indexOf(card);
            if (currentIndex >= 0) {
                selected.splice(currentIndex, 1);
                haptic('soft');
                refreshSlots();
                return;
            }

            if (selected.length >= 3) {
                haptic('rigid');
                return;
            }

            selected.push(card);
            haptic('light');
            refreshSlots();

            if (selected.length === 3) {
                locked = true;
                try {
                    localStorage.setItem(`spread_${screen.dataset.slug}_cards`, JSON.stringify(selected.map((item) => item.dataset.card)));
                } catch (e) {}

                setTimeout(() => {
                    window.location.href = nextUrl || '/loading';
                }, 620);
            }
        });
    });
});
