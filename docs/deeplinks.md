# PackIt Deeplinks

**[RU](#ru) | [EN](#en)**

Все диплинки начинаются с `tg://packit`.  
All deeplinks start with `tg://packit`.

---

<a name="ru"></a>
# 🇷🇺 Русский

## Содержание

- [Основные](#ru-основные)
- [Установка](#ru-установка)
- [Репозитории](#ru-репозитории)
- [Утилиты](#ru-утилиты)

---

<a name="ru-основные"></a>
## Основные

### Проверка работы
```
tg://packit
```
Показывает уведомление что PackIt работает.

### Настройки PackIt
```
tg://packit?settings
```
Открывает страницу настроек PackIt.

---

<a name="ru-установка"></a>
## Установка

### Открыть менеджер плагинов
```
tg://packit?install
```

### Открыть плагины репозитория
```
tg://packit?install&repo=<rm_id>
```
| Параметр | Описание |
|----------|----------|
| `rm_id` | ID репозитория (должен быть добавлен в PackIt) |

### Установить конкретный плагин
```
tg://packit?install&repo=<rm_id>&plugin=<plugin_id>
```
| Параметр | Описание |
|----------|----------|
| `rm_id` | ID репозитория |
| `plugin_id` | ID плагина внутри репозитория |

Скачивает плагин и открывает нативный диалог установки.

### Установить иконку
```
tg://packit?install&repo=<rm_id>&icon=<icon_id>
```
| Параметр | Описание |
|----------|----------|
| `rm_id` | ID репозитория |
| `icon_id` | ID иконки внутри репозитория |

Скачивает иконку и открывает нативный диалог установки.

---

<a name="ru-репозитории"></a>
## Репозитории

### Добавить репозиторий
```
tg://packit?repo=add&name=<n>&link=<url>&icon=<icon>
```
| Параметр | Обязательный | Описание |
|----------|:---:|----------|
| `name` | ✅ | Название репозитория |
| `link` | ✅ | URL до `repomap.json` репозитория |
| `icon` | ❌ | Иконка (например `msg_folders`) |

Показывает диалог подтверждения с информацией о репозитории перед добавлением. Максимум 10 репозиториев.

### Обновить кэш репозиториев
```
tg://packit?update
```
Обновляет кэш всех добавленных репозиториев и синхронизирует их метаданные.

### Обновить кэш конкретного репозитория
```
tg://packit?update&repo=<rm_id>
```
| Параметр | Описание |
|----------|----------|
| `rm_id` | ID репозитория (должен быть добавлен в PackIt) |

Обновляет кэш только одного указанного репозитория. Показывает уведомление об успехе или ошибке.

---

<a name="ru-утилиты"></a>
## Утилиты

### Форум PackIt
```
tg://packit?forum
```
Открывает Telegram-канал [PackItGround](https://t.me/packitGround).

### Известные проблемы
```
tg://packit?problems
```
Открывает тему с известными проблемами в форуме.

### Перезапустить приложение
```
tg://packit?pkill
```
Принудительно завершает процесс приложения (перезапуск).

---

Надеюсь, это поможет вам разобраться с внутренними ссылками Packit :)

<a name="en"></a>
# 🇬🇧 English

## Table of Contents

- [General](#en-general)
- [Installation](#en-installation)
- [Repositories](#en-repositories)
- [Utilities](#en-utilities)

---

<a name="en-general"></a>
## General

### Check status
```
tg://packit
```
Shows a notification confirming PackIt is working.

### PackIt settings
```
tg://packit?settings
```
Opens the PackIt settings page.

---

<a name="en-installation"></a>
## Installation

### Open plugin manager
```
tg://packit?install
```

### Open repository plugins
```
tg://packit?install&repo=<rm_id>
```
| Parameter | Description |
|-----------|-------------|
| `rm_id` | Repository ID (must be added to PackIt) |

### Install a specific plugin
```
tg://packit?install&repo=<rm_id>&plugin=<plugin_id>
```
| Parameter | Description |
|-----------|-------------|
| `rm_id` | Repository ID |
| `plugin_id` | Plugin ID within the repository |

Downloads the plugin and opens the native install dialog.

### Install an icon
```
tg://packit?install&repo=<rm_id>&icon=<icon_id>
```
| Parameter | Description |
|-----------|-------------|
| `rm_id` | Repository ID |
| `icon_id` | Icon ID within the repository |

Downloads the icon and opens the native install dialog.

---

<a name="en-repositories"></a>
## Repositories

### Add a repository
```
tg://packit?repo=add&name=<n>&link=<url>&icon=<icon>
```
| Parameter | Required | Description |
|-----------|:---:|-------------|
| `name` | ✅ | Repository name |
| `link` | ✅ | URL to the repository `repomap.json` |
| `icon` | ❌ | Icon name (e.g. `msg_folders`) |

Shows a confirmation dialog with repository info before adding. Max 10 repositories.

### Update repository cache
```
tg://packit?update
```
Updates the cache of all added repositories and syncs their metadata.

### Update a specific repository cache
```
tg://packit?update&repo=<rm_id>
```
| Parameter | Description |
|-----------|-------------|
| `rm_id` | Repository ID (must be added to PackIt) |

Updates the cache of only the specified repository. Shows a success or error notification.

---

<a name="en-utilities"></a>
## Utilities

### PackIt forum
```
tg://packit?forum
```
Opens the [PackItGround](https://t.me/packitGround) Telegram channel.

### Known issues
```
tg://packit?problems
```
Opens the known issues thread in the forum.

### Restart the app
```
tg://packit?pkill
```
Force-kills the app process (restart).

---

Hope this helps you understand Deeplinks for Packit :)


