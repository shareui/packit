from ui.settings import Header, Text, Divider
from ui.bulletin import BulletinHelper


class InterfaceSettings:
    def __init__(self):
        pass
    
    def _showNotReady(self, view):
        BulletinHelper.show_info("Not ready")
    
    def build(self):
        return [
            Header(text="Actions"),
            Text(
                text="Install",
                icon="msg_download",
                on_click=self._showNotReady
            ),
            Text(
                text="Update",
                icon="msg_retry",
                on_click=self._showNotReady
            ),
            Text(
                text="Upgrade",
                icon="gift_upgrade",
                on_click=self._showNotReady
            ),
            Text(
                text="Uninstall",
                icon="msg_delete",
                red=True,
                on_click=self._showNotReady
            ),
            Divider(),
            Text(
                text="Search",
                icon="msg_search",
                on_click=self._showNotReady
            ),
            Text(
                text="Plugin List",
                icon="msg_list",
                on_click=self._showNotReady
            ),
            Text(
                text="Repository List",
                icon="msg_folders",
                on_click=self._showNotReady
            )
        ]