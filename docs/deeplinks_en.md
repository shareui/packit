# [Deeplink RU](https://github.com/shareui/packit/blob/main/docs/deeplinks_ru.md) | Deeplink EN

Deeplink URLs with the prefix `tg://packit` allow you to quickly perform actions within the Packit ecosystem: open menus, manage repositories, install and update plugins. Here is all the information about them.

## Link format

`tg://packit?<command>&<parameter1>=<value1>&<parameter2>=<value2>...`

- **command** — main action.
- **parameters** — additional details.

---

## Available commands

### Menu and navigation
| Deeplink | Description |
|----------|-------------|
| `tg://packit?settings` | Open settings |
| `tg://packit?deeplink` | Deeplink info |
| `tg://packit?other` | Other functions |
| `tg://packit?contributors` | Contributors list |
| `tg://packit?docs` | Documentation |
| `tg://packit?repo` | Repositories menu |
| `tg://packit?install` | Plugin installation / repository selection menu |
| `tg://packit?update` | Update / repository selection menu |

### Repositories
| Deeplink | Description | Variables |
|----------|-------------|-----------|
| `tg://packit?repo` | Show repositories list | --- |
| `tg://packit?repo=all` | Show all available repositories | --- |
| `tg://packit?repo=add&name=NAME&link=URL&icon=URL` | Add a new repository (requires `name`, `link`, `icon` parameters) | `NAME`, `LINK`, `ICON` |

### Plugin installation
| Deeplink | Description | Variables |
|----------|-------------|-----------|
| `tg://packit?install` | Open installation menu | --- |
| `tg://packit?install&repo=REPO` | Install plugins from specified repository | `REPO` |
| `tg://packit?install&repo=REPO&plugin=PLUGIN` | Install a specific plugin | `REPO`, `PLUGIN` |
| `tg://packit?install&repo=REPO&plugin=PLUGIN&mode=MODE` | Install plugin in specified mode. <br> `mode=share` — share plugin link; `mode=private` — private installation. | `REPO`, `PLUGIN`, `MODE` |

### Update
| Deeplink | Description | Variables |
|----------|-------------|-----------|
| `tg://packit?update` | Update plugin information in ALL repositories | --- |
| `tg://packit?update&repo=REPO` | Update plugin information in REPO repository | `REPO` |

### Other
| Deeplink | Description |
|----------|-------------|
| `tg://packit?forum` | Community forum |
| `tg://packit?problems` | Report a problem |
| `tg://packit?pkill` | Close the app |

---

## Parameters

Example parameter values used in links.

| Parameter | Description |
|-----------|-------------|
| `REPO`    | Repository name |
| `PLUGIN`  | Plugin ID |
| `MODE`    | Installation mode (`share`) |
| `NAME`    | Repository name |
| `LINK`    | Repository link (URL) |
| `ICON`    | Repository icon (pack/id) |

---

Hope this helps you understand Deeplinks for Packit :)
