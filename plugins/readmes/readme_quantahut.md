**QuantaHut** — shared library for Quanta plugins. Not intended for standalone use.

**What is this**

A common foundation used by plugins like UiTweaks. Provides localization, caching, UI components and utilities so each plugin doesn't have to implement them from scratch.

**Features**

**Localization**

GitHub-based localization system with SQLite cache. Plugins load strings by client language without storing translations inside the plugin file itself. Language switching and forced file refresh are supported.

**UI components**

• **BottomSheet** — custom bottom sheet with sticker, changelog text, two buttons and avatar support
• **MultiSelector** — multi-select with a limit, Select All and custom subtexts
• **ExpandableSwitch** — toggle with collapsible child items

*Plugin Engine*

• Enhanced plugin search with filter pills
• Plugin settings search via link alias
• Safe Mode: press volume down 5 times quickly — all plugins deactivate without being removed
• Export/import settings for a single plugin or all at once.
