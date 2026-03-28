# PackIt Dev Docs

**[RU](#ru) | [EN](#en)**

Документация для разработчиков плагинов — возможности, добавленные PackIt.  
Developer documentation — features and APIs added by PackIt.

---

<a name="ru"></a>
# 🇷🇺 Русский

## Содержание

- [Метаинфо](#ru-metainfo)
  - [Ссылки в метаинфо](#ru-links)

---

<a name="ru-metainfo"></a>
## Метаинфо

Дополнительные поля метаинфо, поддерживаемые PackIt.

<a name="ru-links"></a>
### Ссылки в метаинфо

Позволяет указать список иконок-ссылок, которые отображаются в боттомшите установки плагина. По нажатию на иконку открывается указанный URL.

### Объявление

```python
__links__ = [
    {"icon": "msg_channel", "url": "https://t.me/shareui"},
]
```

### Поля элемента

| Поле | Тип | Обязательный | Описание |
|------|-----|:---:|---------|
| `url` | `str` | ✅ | URL, который откроется по нажатию |
| `icon` | `str` | ❌ | Имя иконки из `R.drawable`. По умолчанию `msg_link` |
| `gravity` | `str \| int` | ❌ | Расположение кнопки. По умолчанию `LEFT_TOP` |
| `x` | `int \| float` | ❌ | Горизонтальный отступ в dp. По умолчанию `16` |
| `y` | `int \| float` | ❌ | Вертикальный отступ от края в dp. По умолчанию автоматический (стакаются вниз) |

### Значения `gravity`

| Значение | Описание |
|----------|----------|
| `LEFT_TOP` | Левый верхний угол *(по умолчанию)* |
| `RIGHT_TOP` | Правый верхний угол |
| `LEFT_BOTTOM` | Левый нижний угол |
| `RIGHT_BOTTOM` | Правый нижний угол |
| `CENTER_TOP` | Центр сверху |
| `CENTER_BOTTOM` | Центр снизу |
| `LEFT` | Левый край |
| `RIGHT` | Правый край |
| `CENTER` | По центру |

Также можно комбинировать через `|`: `"LEFT|TOP"`, `"RIGHT|BOTTOM"`.  
Принимает числовой android Gravity int напрямую.

### Поведение

• Если `gravity` не указан — кнопки автоматически стакаются вниз от левого верхнего угла  
• Если `y` не указан — следующая кнопка размещается на `44dp` ниже предыдущей  
• Для `RIGHT*` gravity значение `x` становится `rightMargin`, а не `leftMargin`  
• По нажатию боттомшит установки закрывается, затем открывается ссылка  
• Кнопку можно отключить глобально в настройках PackIt → *Installation BottomSheet → Show author links*

### Примеры

**Один элемент (минимум):**
```python
__links__ = [
    {"icon": "msg_channel", "url": "https://t.me/shareui"},
]
```

**Несколько с явными координатами:**
```python
__links__ = [
    {"icon": "msg_channel",  "url": "https://t.me/shareui"},
    {"icon": "msg_link",     "url": "https://github.com/shareui",  "y": 60},
    {"icon": "msg_contacts", "url": "https://t.me/doctashare",     "y": 104},
]
```

**Разные углы:**
```python
__links__ = [
    {"icon": "msg_channel",  "url": "https://t.me/shareui",       "gravity": "LEFT_TOP"},
    {"icon": "msg_info",     "url": "https://t.me/shareui",        "gravity": "RIGHT_BOTTOM", "x": 16, "y": 16},
]
```

---

Надеюсь, это поможет вам в разработке плагинов :)

<a name="en"></a>
# 🇬🇧 English

## Table of Contents

- [Metainfo](#en-metainfo)
  - [Plugin Metainfo Links](#en-links)

---

<a name="en-metainfo"></a>
## Metainfo

Additional metainfo fields supported by PackIt.

<a name="en-links"></a>
### Plugin Metainfo Links

Allows you to define a list of icon buttons shown in the plugin install bottomsheet. Tapping an icon opens the specified URL.

### Declaration

```python
__links__ = [
    {"icon": "msg_channel", "url": "https://t.me/shareui"},
]
```

### Item fields

| Field | Type | Required | Description |
|-------|------|:---:|-------------|
| `url` | `str` | ✅ | URL to open on tap |
| `icon` | `str` | ❌ | Icon name from `R.drawable`. Defaults to `msg_link` |
| `gravity` | `str \| int` | ❌ | Button placement. Defaults to `LEFT_TOP` |
| `x` | `int \| float` | ❌ | Horizontal margin in dp. Defaults to `16` |
| `y` | `int \| float` | ❌ | Vertical margin from edge in dp. Defaults to auto (stacks downward) |

### `gravity` values

| Value | Description |
|-------|-------------|
| `LEFT_TOP` | Top-left corner *(default)* |
| `RIGHT_TOP` | Top-right corner |
| `LEFT_BOTTOM` | Bottom-left corner |
| `RIGHT_BOTTOM` | Bottom-right corner |
| `CENTER_TOP` | Top center |
| `CENTER_BOTTOM` | Bottom center |
| `LEFT` | Left edge |
| `RIGHT` | Right edge |
| `CENTER` | Center |

You can also combine with `|`: `"LEFT|TOP"`, `"RIGHT|BOTTOM"`.  
A raw android Gravity int is also accepted.

### Behavior

• If `gravity` is omitted — buttons auto-stack downward from the top-left corner  
• If `y` is omitted — each next button is placed `44dp` below the previous one  
• For `RIGHT*` gravity, `x` becomes `rightMargin` instead of `leftMargin`  
• Tapping a button dismisses the install bottomsheet, then opens the URL  
• Can be disabled globally in PackIt settings → *Installation BottomSheet → Show author links*

### Examples

**Single item (minimum):**
```python
__links__ = [
    {"icon": "msg_channel", "url": "https://t.me/shareui"},
]
```

**Multiple with explicit coordinates:**
```python
__links__ = [
    {"icon": "msg_channel",  "url": "https://t.me/shareui"},
    {"icon": "msg_link",     "url": "https://github.com/shareui",  "y": 60},
    {"icon": "msg_contacts", "url": "https://t.me/doctashare",     "y": 104},
]
```

**Different corners:**
```python
__links__ = [
    {"icon": "msg_channel",  "url": "https://t.me/shareui",        "gravity": "LEFT_TOP"},
    {"icon": "msg_info",     "url": "https://t.me/shareui",        "gravity": "RIGHT_BOTTOM", "x": 16, "y": 16},
]
```

---

Hope this helps you build better plugins :)
