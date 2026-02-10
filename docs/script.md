# adding script

<p align="center">
  <a href="#english-documentation">Documentation</a> • <a href="#русская-документация">Документация</a>
</p>

---

## English documentation

Script for managing plugin repository configuration files.

Download: https://github.com/shareui/packit/blob/main/add.py

> IMPORTANT TO KNOW: This script was created for personal use but I decided to publish It

### Overview

This script automates the process of adding, updating, and managing plugins in a repository configuration file. It extracts metadata from plugin files, manages versions, creates backups, and maintains a JSON configuration.

### Configuration

On first run, the script creates a configuration file (cfg.yml) with the following settings:

- addAbout: Include "about" field in plugin entries
- addDescription: Include "description" field in plugin entries
- addHash: Include SHA256 hash for each plugin
- writeLastLog: Generate a log file after updates
- createForPost: Generate a file for Telegram posts after updates
- createBackups: Create backup copies of config.json before modifications
- allowDowngrade: Allow version downgrade without confirmation (default: false)
- manualInputDescriptions: Manually input descriptions during plugin addition
- manualInputAbout: Manually input about text in English and Russian
- configPath: Path to repository config file (default: config.json)
- workingDir: Directory containing plugin files (default: workingdir)
- backupDir: Directory for backups (default: backups)
- stateKeywords: Keywords for version states (default: alpha,beta,dev,rc,release,rel,stable)
- rawDirUrl: Base URL for plugin downloads (default: https://raw.githubusercontent.com/user/repo/refs/heads/main/plugins)

### Plugin Metadata

The script extracts the following metadata from plugin files:

- __id__: Unique plugin identifier
- __name__: Plugin name
- __author__: Author name
- __description__: Plugin description
- __version__: Version string
- __icon__: Icon identifier
- __dependencies__: List of plugin dependencies

### Features

#### 1. Add Files

Scans the working directory for plugin files and adds or updates them in the repository configuration. The script:

- Calculates SHA256 hash for each file
- Skips files with existing hashes
- Updates existing plugins if ID matches
- Performs version comparison before updating
- Warns about version downgrades and asks for confirmation (unless allowDowngrade is enabled)
- Adds new plugins if ID is not found
- Generates a log file if enabled
- Generates a post file for Telegram if enabled

#### 2. Change File

Updates a specific plugin entry by providing a file name. The script automatically reads the plugin ID from the file and replaces the existing entry with metadata from the new file.

Usage: filename

#### 3. Delete Files

Removes a plugin from the configuration by providing a file name. The script automatically reads the plugin ID from the file and removes it from the configuration. The physical file is also deleted from the working directory.

Usage: filename

#### 4. Clear Missing Plugins

Removes plugin entries from the configuration if their corresponding files are missing from the working directory. Logs all deletions if writeLastLog is enabled.

#### 5. Dir Status

Shows a preview of what will happen if you start adding files now:
- Will be added: Count of new plugins
- Will be updated: Count of existing plugins that will be updated
- Will be removed: Count of plugins that will be removed (files missing from directory)

#### 6. Edit Plugin Value

Allows editing any field value in a plugin entry by its ID. The script displays current values and allows you to modify a specific field.

Usage: Enter plugin ID, then select field to edit and provide new value

#### 7. Add Item to JSON

Adds a new field to a plugin entry by its ID. The script allows you to:
- Select data type (string, number, boolean, array, object)
- Enter the value according to selected type
- Add the new field to the plugin

#### 8. Edit Config Values

Allows editing specific fields in cfg.yml without rewriting the entire configuration. Select which fields you want to modify by entering them as a comma-separated list.

#### 9. Rewrite Script Config

Allows reconfiguration of the script settings by recreating the cfg.yml file.

#### 10. Create .gitignore for cfg.yml

Creates or updates .gitignore file to exclude cfg.yml from version control.

### Version Management

The script includes version comparison to prevent accidental downgrades:

- Parses version strings (e.g., "1.2.3") into comparable components
- Compares new version against existing version when updating plugins
- If new version is lower than current version:
  - Displays warning with both versions
  - Asks for confirmation to proceed (unless allowDowngrade is enabled)
  - Skips update if user declines

Version states are normalized:
- "rel", "stable" → "release"
- Other keywords remain as-is

### Backup System

When enabled, the script creates timestamped backups before modifying config.json:

Format: backup-HH-MM-SS-DD-MM-YYYY.json

### Latest Log

When writeLastLog is enabled, the script generates latest.log with:

- Timestamp of update
- Total plugin count
- Count of added, updated, and deleted plugins
- Detailed list of:
  - New plugins (name, id, version)
  - Updated plugins (name, id, version)
  - Deleted plugins (name, id, version)

### For Post File

When createForPost is enabled, the script generates forpost.txt in format suitable for Telegram posts:

```
Added {count} plugins

{name} by {author}
{name} by {author}

Updated {count} plugins

{name} by {author}

Removed {count} plugins

{name} by {author}

Total plugins: {count}
```

### Output Structure

Each plugin entry in config.json contains:

- id: Plugin identifier
- name: Plugin name
- author: Author name
- version: Parsed version number
- state: Version state
- icon: Icon identifier
- suspicious: Security flag (always "false")
- dependencies: Array of dependency IDs
- link: Download URL (constructed from rawDirUrl and filename)
- about: Plugin name (optional)
- description: Plugin description (optional)
- hash: SHA256 hash (optional)

### Usage

Run the script and select an option from the menu:

1. Add files - Process plugins from working directory
2. Change file - Update specific plugin entry
3. Delete files - Remove plugin by filename
4. Clear missing plugins - Remove entries for missing files
5. Dir status - Preview changes before adding
6. Edit plugin value - Modify field in plugin entry
7. Add item to json - Add new field to plugin entry
8. Edit config values - Modify specific cfg.yml fields
9. Rewrite script cfg - Reconfigure script settings
10. Create .gitignore for cfg.yml - Add cfg.yml to gitignore
11. Exit - Quit the script

---

## Русская документация

Скрипт для управления конфигурационными файлами репозитория плагинов.

Скачать: https://github.com/shareui/packit/blob/main/add.py

> ВАЖНО ЗНАТЬ: Этот скрипт был создан для личного использования, но я решил опубликовать его

### Обзор

Этот скрипт автоматизирует процесс добавления, обновления и управления плагинами в конфигурационном файле репозитория. Он извлекает метаданные из файлов плагинов, управляет версиями, создаёт резервные копии и поддерживает JSON конфигурацию.

### Конфигурация

При первом запуске скрипт создаёт конфигурационный файл (cfg.yml) со следующими настройками:

- addAbout: Включать поле "about" в записи плагина
- addDescription: Включать поле "description" в записи плагина
- addHash: Включать SHA256 хеш для каждого плагина
- writeLastLog: Генерировать лог-файл после обновлений
- createForPost: Генерировать файл для постов в Telegram после обновлений
- createBackups: Создавать резервные копии config.json перед изменениями
- allowDowngrade: Разрешить понижение версии без подтверждения (по умолчанию: false)
- manualInputDescriptions: Вручную вводить описания при добавлении плагина
- manualInputAbout: Вручную вводить текст about на английском и русском
- configPath: Путь к конфигурационному файлу репозитория (по умолчанию: config.json)
- workingDir: Директория с файлами плагинов (по умолчанию: workingdir)
- backupDir: Директория для резервных копий (по умолчанию: backups)
- stateKeywords: Ключевые слова для состояний версии (по умолчанию: alpha,beta,dev,rc,release,rel,stable)
- rawDirUrl: Базовый URL для загрузки плагинов (по умолчанию: https://raw.githubusercontent.com/user/repo/refs/heads/main/plugins)

### Метаданные плагина

Скрипт извлекает следующие метаданные из файлов плагинов:

- __id__: Уникальный идентификатор плагина
- __name__: Имя плагина
- __author__: Имя автора
- __description__: Описание плагина
- __version__: Строка версии
- __icon__: Идентификатор иконки
- __dependencies__: Список зависимостей плагина

### Функции

#### 1. Add Files (Добавить файлы)

Сканирует рабочую директорию на наличие файлов плагинов и добавляет или обновляет их в конфигурации репозитория. Скрипт:

- Вычисляет SHA256 хеш для каждого файла
- Пропускает файлы с существующими хешами
- Обновляет существующие плагины, если ID совпадает
- Выполняет сравнение версий перед обновлением
- Предупреждает о понижении версии и запрашивает подтверждение (если не включён allowDowngrade)
- Добавляет новые плагины, если ID не найден
- Генерирует лог-файл, если включено
- Генерирует файл для поста в Telegram, если включено

#### 2. Change File (Изменить файл)

Обновляет конкретную запись плагина, указав имя файла. Скрипт автоматически читает ID плагина из файла и заменяет существующую запись метаданными из нового файла.

Использование: filename

#### 3. Delete Files (Удалить файлы)

Удаляет плагин из конфигурации, указав имя файла. Скрипт автоматически читает ID плагина из файла и удаляет его из конфигурации. Физический файл также удаляется из рабочей директории.

Использование: filename

#### 4. Clear Missing Plugins (Очистить отсутствующие плагины)

Удаляет записи плагинов из конфигурации, если соответствующие файлы отсутствуют в рабочей директории. Записывает все удаления в лог, если включён writeLastLog.

#### 5. Dir Status (Статус директории)

Показывает предварительный просмотр того, что произойдёт, если начать добавление файлов сейчас:
- Will be added: Количество новых плагинов
- Will be updated: Количество существующих плагинов, которые будут обновлены
- Will be removed: Количество плагинов, которые будут удалены (файлы отсутствуют в директории)

#### 6. Edit Plugin Value (Редактировать значение плагина)

Позволяет редактировать значение любого поля в записи плагина по его ID. Скрипт отображает текущие значения и позволяет изменить конкретное поле.

Использование: Введите ID плагина, затем выберите поле для редактирования и укажите новое значение

#### 7. Add Item to JSON (Добавить элемент в JSON)

Добавляет новое поле в запись плагина по его ID. Скрипт позволяет:
- Выбрать тип данных (строка, число, булево значение, массив, объект)
- Ввести значение в соответствии с выбранным типом
- Добавить новое поле к плагину

#### 8. Edit Config Values (Редактировать значения конфигурации)

Позволяет редактировать конкретные поля в cfg.yml без перезаписи всей конфигурации. Выберите, какие поля вы хотите изменить, введя их через запятую.

#### 9. Rewrite Script Config (Переписать конфигурацию скрипта)

Позволяет переконфигурировать настройки скрипта, пересоздав файл cfg.yml.

#### 10. Create .gitignore for cfg.yml (Создать .gitignore для cfg.yml)

Создаёт или обновляет файл .gitignore, чтобы исключить cfg.yml из системы контроля версий.

### Управление версиями

Скрипт включает сравнение версий для предотвращения случайного понижения версии:

- Разбирает строки версий (например, "1.2.3") на сравниваемые компоненты
- Сравнивает новую версию с существующей при обновлении плагинов
- Если новая версия ниже текущей версии:
  - Отображает предупреждение с обеими версиями
  - Запрашивает подтверждение для продолжения (если не включён allowDowngrade)
  - Пропускает обновление, если пользователь отказывается

Состояния версий нормализуются:
- "rel", "stable" → "release"
- Другие ключевые слова остаются как есть

### Система резервного копирования

При включении скрипт создаёт резервные копии с временными метками перед изменением config.json:

Формат: backup-HH-MM-SS-DD-MM-YYYY.json

### Последний лог

Когда включён writeLastLog, скрипт генерирует latest.log с:

- Временной меткой обновления
- Общим количеством плагинов
- Количеством добавленных, обновлённых и удалённых плагинов
- Подробным списком:
  - Новых плагинов (имя, id, версия)
  - Обновлённых плагинов (имя, id, версия)
  - Удалённых плагинов (имя, id, версия)

### Файл для поста

Когда включён createForPost, скрипт генерирует forpost.txt в формате, подходящем для постов в Telegram:

```
Added {количество} plugins

{name} by {author}
{name} by {author}

Updated {количество} plugins

{name} by {author}

Removed {количество} plugins

{name} by {author}

Total plugins: {количество}
```

### Структура вывода

Каждая запись плагина в config.json содержит:

- id: Идентификатор плагина
- name: Имя плагина
- author: Имя автора
- version: Разобранный номер версии
- state: Состояние версии
- icon: Идентификатор иконки
- suspicious: Флаг безопасности (всегда "false")
- dependencies: Массив ID зависимостей
- link: URL загрузки (сконструированный из rawDirUrl и имени файла)
- about: Имя плагина (опционально)
- description: Описание плагина (опционально)
- hash: SHA256 хеш (опционально)

### Использование

Запустите скрипт и выберите опцию из меню:

1. Add files - Обработать плагины из рабочей директории
2. Change file - Обновить конкретную запись плагина
3. Delete files - Удалить плагин по имени файла
4. Clear missing plugins - Удалить записи для отсутствующих файлов
5. Dir status - Предварительный просмотр изменений перед добавлением
6. Edit plugin value - Изменить поле в записи плагина
7. Add item to json - Добавить новое поле в запись плагина
8. Edit config values - Изменить конкретные поля cfg.yml
9. Rewrite script cfg - Переконфигурировать настройки скрипта
10. Create .gitignore for cfg.yml - Добавить cfg.yml в gitignore
11. Exit - Выйти из скрипта
