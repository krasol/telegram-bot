(function () {
  'use strict';

  const USER_KEY = 'astro_tg_user';
  const STATE_KEY = 'astro_app_state';
  const OLD_ONBOARDING_KEYS = ['onboarding_seen', 'onboardingSeen', 'astro_onboarding_seen'];
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;

  function safeJsonParse(value, fallback) {
    try {
      return value ? JSON.parse(value) : fallback;
    } catch (_) {
      return fallback;
    }
  }

  function readLocalUser() {
    return safeJsonParse(localStorage.getItem(USER_KEY), null);
  }

  function saveLocalUser(user) {
    if (!user || !user.id) return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function readLocalState() {
    const state = safeJsonParse(localStorage.getItem(STATE_KEY), {}) || {};

    if (state.coins == null) {
      const oldCoins = localStorage.getItem('coins') || localStorage.getItem('crystals') || localStorage.getItem('astro_coins');
      if (oldCoins !== null && oldCoins !== '') {
        const parsed = Number.parseInt(oldCoins, 10);
        if (Number.isFinite(parsed)) state.coins = parsed;
      }
    }

    for (const key of OLD_ONBOARDING_KEYS) {
      const value = localStorage.getItem(key);
      if (value === '1' || value === 'true') {
        state.onboarding_seen = true;
        break;
      }
    }

    if (state.coins == null) state.coins = 150;
    if (state.streak_days == null) state.streak_days = 7;
    if (state.onboarding_seen == null) state.onboarding_seen = false;

    return state;
  }

  function saveLocalState(patch) {
    const current = readLocalState();
    const next = Object.assign({}, current, patch || {}, { updated_at: new Date().toISOString() });
    localStorage.setItem(STATE_KEY, JSON.stringify(next));

    if (next.coins != null) {
      localStorage.setItem('coins', String(next.coins));
      localStorage.setItem('crystals', String(next.coins));
    }

    if (next.onboarding_seen) {
      localStorage.setItem('onboarding_seen', 'true');
      localStorage.setItem('onboardingSeen', 'true');
      localStorage.setItem('astro_onboarding_seen', 'true');
    }

    return next;
  }

  function getTelegramUser() {
    const user = tg && tg.initDataUnsafe ? tg.initDataUnsafe.user : null;
    if (user && user.id) return user;
    return null;
  }

  function fullName(user) {
    if (!user) return '';
    return [user.first_name || '', user.last_name || ''].join(' ').trim();
  }

  function renderUser(user) {
    if (!user) return;
    const name = fullName(user) || 'Пользователь';
    const username = user.username ? '@' + user.username : 'Искатель пути';

    document.querySelectorAll('[data-tg-name], #tgName').forEach((el) => {
      el.textContent = name;
    });

    document.querySelectorAll('[data-tg-username], #tgUsername').forEach((el) => {
      el.textContent = username;
    });

    document.querySelectorAll('[data-tg-avatar], #tgAvatar').forEach((el) => {
      if (user.photo_url) {
        el.src = user.photo_url;
        el.style.display = 'block';
      }
    });
  }

  function renderState(state) {
    if (!state) return;
    const coins = Number.isFinite(Number(state.coins)) ? Number(state.coins) : 150;
    const streak = Number.isFinite(Number(state.streak_days)) ? Number(state.streak_days) : 7;

    document.querySelectorAll('[data-coins-count], #coinCount').forEach((el) => {
      el.textContent = String(coins);
    });

    document.querySelectorAll('[data-coins-label], #walletCoins').forEach((el) => {
      el.textContent = `${coins} Кристаллов`;
    });

    document.querySelectorAll('[data-streak-days]').forEach((el) => {
      el.textContent = `${streak} дней в потоке`;
    });
  }

  async function postJson(url, body, keepalive) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        keepalive: Boolean(keepalive),
        body: JSON.stringify(body || {})
      });
      return await response.json().catch(() => null);
    } catch (_) {
      return null;
    }
  }

  async function syncUserAndState() {
    if (tg) {
      try {
        tg.ready();
        tg.expand();
      } catch (_) {}
    }

    const localUser = readLocalUser();
    const localState = readLocalState();
    renderUser(localUser);
    renderState(localState);

    const tgUser = getTelegramUser();
    if (tgUser) {
      renderUser(tgUser);
      saveLocalUser(tgUser);

      const saved = await postJson('/save-user', {
        user: tgUser,
        initData: tg ? (tg.initData || '') : '',
        state: localState
      });

      if (saved && saved.success) {
        if (saved.user) {
          saveLocalUser(saved.user);
          renderUser(saved.user);
        }
        if (saved.state) {
          saveLocalState(saved.state);
          renderState(saved.state);
        }
      }
    } else {
      // Если Telegram не отдал пользователя, не теряем локальное состояние.
      // Особенно важно для онбординга: после потери cookie Render должен восстановиться из localStorage.
      if (localState.onboarding_seen) {
        await postJson('/api/state', Object.assign({}, localState, { onboarding_seen: true, state: localState }));
      }

      const stateResponse = await fetch('/api/state', { credentials: 'same-origin' })
        .then((r) => r.json())
        .catch(() => null);

      if (stateResponse && stateResponse.success) {
        if (stateResponse.user && stateResponse.user.id) {
          saveLocalUser(stateResponse.user);
          renderUser(stateResponse.user);
        }
        if (stateResponse.state) {
          const merged = Object.assign({}, stateResponse.state, localState);
          if (localState.onboarding_seen) merged.onboarding_seen = true;
          saveLocalState(merged);
          renderState(merged);
        }
      }
    }

    const isOnboardingPage = /^\/onboarding(?:\/|$)/.test(window.location.pathname);
    const freshState = readLocalState();
    if (isOnboardingPage && freshState.onboarding_seen) {
      await postJson('/api/state', { onboarding_seen: true, state: freshState }, true);
      window.location.replace('/today');
    }
  }

  function bindOnboardingFinish() {
    document.querySelectorAll('a[href="/onboarding/finish"], [data-finish-onboarding]').forEach((el) => {
      el.addEventListener('click', () => {
        const state = saveLocalState({ onboarding_seen: true });
        const tgUser = getTelegramUser() || readLocalUser();
        postJson('/api/state', Object.assign({}, state, {
          user: tgUser || undefined,
          initData: tg ? (tg.initData || '') : '',
          onboarding_seen: true,
          state
        }), true);
      });
    });
  }

  window.AstroTelegramState = {
    readLocalUser,
    saveLocalUser,
    readLocalState,
    saveLocalState,
    syncUserAndState,
    renderUser,
    renderState
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      bindOnboardingFinish();
      syncUserAndState();
    });
  } else {
    bindOnboardingFinish();
    syncUserAndState();
  }
})();
