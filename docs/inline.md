# PackIt Inline Search

**[RU](#ru) | [EN](#en)**

Инлайн-поиск позволяет искать и отправлять карточки плагинов прямо из поля ввода.  
Inline search lets you find and share plugin cards directly from the message input.

---

<a name="ru"></a>
# 🇷🇺 Русский

## Содержание

- [Основы](#ru-основы)
- [Фильтры](#ru-фильтры)
- [Формат вывода](#ru-вывод)

---

<a name="ru-основы"></a>
## Основы

### Запуск поиска
```
.packit <запрос>
```
Введи `.packit ` (с пробелом) — появится попап с результатами. Начни вводить название плагина для фильтрации.

Пример:
```
.packit DevSettings
```

> Команду `.packit` можно изменить в настройках → **Inline command**.

### Выбор плагина
- **Тап** — отправить карточку плагина в чат.
- **Долгий тап** — открыть профиль плагина.

### Двойной пробел
Если включено в настройках, двойное нажатие пробела автоматически вставляет `.packit `.

### Очистка поля после отправки
Если включено в настройках, поле ввода очищается после выбора плагина.

---

<a name="ru-фильтры"></a>
## Фильтры

Фильтры добавляются через `filter:` после запроса (или вместо него). Несколько фильтров разделяются `;`, несколько значений внутри фильтра — `,`.

```
.packit <запрос> filter:<ключ>="<значение>";<ключ>="<значение1>","<значение2>"
```

Порядок `filter:` и запроса — произвольный.

---

### filter:tags

Показывает только плагины, у которых есть **хотя бы один** из указанных тегов (без учёта регистра).

```
.packit filter:tags="elyx"
.packit filter:tags="elyx","devtools"
.packit DevSettings filter:tags="System"
```

---

### filter:author

Показывает только плагины указанного автора (без учёта регистра и `@`).

```
.packit filter:author="@shareui"
.packit filter:author="shareui","anotherdev"
```

---

### filter:app_version

Показывает только плагины, совместимые с указанной версией приложения.

Поддерживаемые операторы: `>=`, `<=`, `==`.

```
.packit filter:app_version=">=12.5.1"
.packit filter:app_version="==11.0.0"
```

---

### Комбинирование

Все фильтры можно комбинировать в любом порядке:

```
.packit filter:tags="elyx";author="@shareui"
.packit DevSettings filter:tags="System";app_version=">=12.5.1"
.packit filter:author="@shareui";tags="elyx","devtools";app_version=">=12.0.0"
```

---

<a name="ru-вывод"></a>
## Формат вывода

По умолчанию карточка выглядит так:

```
DevSettingIcons (v1.4.3)
by @shareui
<описание>
Install via PackIt
```

Изменить формат первой строки можно через `output:type=`.

---

### output:type="update"

Используй при анонсе обновления плагина.

```
.packit DevSettingIcons output:type="update"
```

Первая строка:
```
DevSettingIcons updated to 1.4.3
```
(`updated to` — жирный, название — ссылка)

---

### output:type="release"

Используй при анонсе нового релиза.

```
.packit DevSettingIcons output:type="release"
```

Первая строка:
```
DevSettingIcons has been released!
```
(без версии, название — ссылка)

---

### Комбинирование с фильтрами

`output:type=` работает вместе с `filter:`:

```
.packit DevSettingIcons filter:tags="System" output:type="update"
.packit filter:author="@shareui" output:type="release"
```

---

Настроить состав карточки (версия, автор, описание, ссылка установки) можно в настройках → **Sending a message**.

---

<a name="en"></a>
# 🇬🇧 English

## Table of Contents

- [Basics](#en-basics)
- [Filters](#en-filters)
- [Output format](#en-output)

---

<a name="en-basics"></a>
## Basics

### Starting a search
```
.packit <query>
```
Type `.packit ` (with a space) — a popup will appear with results. Start typing a plugin name to filter.

Example:
```
.packit DevSettings
```

> The `.packit` command can be changed in settings → **Inline command**.

### Selecting a plugin
- **Tap** — send a plugin card to the chat.
- **Long tap** — open the plugin profile.

### Double space
When enabled in settings, pressing space twice automatically inserts `.packit `.

### Clear field after sending
When enabled in settings, the input field is cleared after selecting a plugin.

---

<a name="en-filters"></a>
## Filters

Filters are added via `filter:` after the query (or instead of it). Multiple filters are separated by `;`, multiple values within a filter by `,`.

```
.packit <query> filter:<key>="<value>";<key>="<value1>","<value2>"
```

The order of `filter:` and the query is arbitrary.

---

### filter:tags

Shows only plugins that have **at least one** of the specified tags (case-insensitive).

```
.packit filter:tags="elyx"
.packit filter:tags="elyx","devtools"
.packit DevSettings filter:tags="System"
```

---

### filter:author

Shows only plugins from the specified author (case-insensitive, `@` is optional).

```
.packit filter:author="@shareui"
.packit filter:author="shareui","anotherdev"
```

---

### filter:app_version

Shows only plugins compatible with the specified app version.

Supported operators: `>=`, `<=`, `==`.

```
.packit filter:app_version=">=12.5.1"
.packit filter:app_version="==11.0.0"
```

---

### Combining filters

All filters can be combined in any order:

```
.packit filter:tags="elyx";author="@shareui"
.packit DevSettings filter:tags="System";app_version=">=12.5.1"
.packit filter:author="@shareui";tags="elyx","devtools";app_version=">=12.0.0"
```

---

<a name="en-output"></a>
## Output format

By default a card looks like this:

```
DevSettingIcons (v1.4.3)
by @shareui
<description>
Install via PackIt
```

You can change the format of the first line using `output:type=`.

---

### output:type="update"

Use when announcing a plugin update.

```
.packit DevSettingIcons output:type="update"
```

First line:
```
DevSettingIcons updated to 1.4.3
```
(`updated to` — bold, name — link)

---

### output:type="release"

Use when announcing a new release.

```
.packit DevSettingIcons output:type="release"
```

First line:
```
DevSettingIcons has been released!
```
(no version, name — link)

---

### Combining with filters

`output:type=` works together with `filter:`:

```
.packit DevSettingIcons filter:tags="System" output:type="update"
.packit filter:author="@shareui" output:type="release"
```

---

The card contents (version, author, description, install link) can be configured in settings → **Sending a message**.
