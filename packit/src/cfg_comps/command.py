from ui.settings import Header, Input
from elyx import strings, settings


class CommandSettings:
    def __init__(self):
        pass
    
    def build(self):
        return [
            Header(text=strings.command_settings),
            Input(
                key="cmd_info",
                text=strings.cmd_info,
                default=settings.get("cmd_info", "packit info"),
                icon="msg_info"
            ),
            Input(
                key="cmd_search",
                text=strings.cmd_search,
                default=settings.get("cmd_search", "packit search"),
                icon="msg_search"
            ),
            Input(
                key="cmd_install",
                text=strings.cmd_install,
                default=settings.get("cmd_install", "packit install"),
                icon="msg_download"
            ),
            Input(
                key="cmd_uninstall",
                text=strings.cmd_uninstall,
                default=settings.get("cmd_uninstall", "packit uninstall"),
                icon="msg_delete"
            ),
            Input(
                key="cmd_update",
                text="Update command",
                default=settings.get("cmd_update", "packit update"),
                icon="msg_retry"
            ),
            Input(
                key="cmd_upgrade",
                text="Upgrade command",
                default=settings.get("cmd_upgrade", "packit upgrade"),
                icon="gift_upgrade"
            ),
            Input(
                key="cmd_pluginlist",
                text=strings.cmd_pluginlist,
                default=settings.get("cmd_pluginlist", "packit pluginlist"),
                icon="msg_list"
            ),
            Input(
                key="cmd_repolist",
                text=strings.cmd_repolist,
                default=settings.get("cmd_repolist", "packit repolist"),
                icon="msg_folders"
            ),
            Input(
                key="cmd_share",
                text=strings.cmd_share,
                default=settings.get("cmd_share", "packit share"),
                icon="msg_share"
            )
        ]