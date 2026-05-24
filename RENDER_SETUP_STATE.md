# Render state setup

Чтобы Telegram-пользователь, кристаллы и пройденный онбординг не сбрасывались после деплоя, на Render нужен постоянный диск.

## Environment Variables

```text
SECRET_KEY=любая_длинная_случайная_строка
BOT_TOKEN=токен_бота_из_BotFather
DATABASE_PATH=/var/data/app.db
```

## Persistent Disk

В Render добавь Persistent Disk и смонтируй его в:

```text
/var/data
```

Если диск не подключить, SQLite-файл может сбрасываться при новом деплое/перезапуске.

## Что сохраняется

- Telegram ID пользователя
- имя, username, avatar
- кристаллы
- streak дней
- факт прохождения первых 3 onboarding-экранов
- карта дня

Клиент также держит резервную копию в localStorage, чтобы не показывать плейсхолдеры, если Telegram WebApp не сразу отдал аккаунт.
