from ui.settings import Header, Text
from elyx import strings


class OtherSettings:
    def __init__(self):
        pass
    
    def build(self):
        return [
            Header(text=strings.other_settings),
            Text(
                text=strings.not_ready,
                icon="msg_info"
            )
        ]