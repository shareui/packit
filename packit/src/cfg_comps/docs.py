from ui.settings import Header, Text, Divider
from ui.bulletin import BulletinHelper


class DocumentationSettings:
    def __init__(self):
        pass
    
    def _showNotReady(self, view):
        BulletinHelper.show_info("Not ready")
    
    def build(self):
        return [
            Header(text="Documentation"),
            Text(
                text="FAQ",
                icon="msg_help",
                on_click=self._showNotReady
            ),
            Text(
                text="Creating your own repo",
                icon="msg_edit",
                on_click=self._showNotReady
            ),
            Text(
                text="Report a bug",
                icon="msg_report",
                on_click=self._showNotReady
            ),
            Text(
                text="Information",
                icon="msg_info",
                on_click=self._showNotReady
            ),
            Divider(text="Documentation and help resources")
        ]