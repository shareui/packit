__id__ = "shareui_lolcat"
__name__ = "LOLCAT dialect"
__description__ = "Automatically translates all messages to LOLCAT dialect [ENGLISH ONLY]"
__author__ = "@shareui the cat :з"
__version__ = "1.1.0"
__icon__ = "traxodrom52_by_fStikBot/13"
__min_version__ = "12.1.1"

from base_plugin import BasePlugin, HookResult, HookStrategy
from typing import Any
from android_utils import log
from ui.settings import Header, Switch, Divider
import re

class LOLCATPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.lolcat_dict = {
            r'\bthe\b': 'teh',
            r'\band\b': 'an',
            r'\bof\b': 'ov',
            r'\bto\b': '2',
            r'\btoo\b': '2',
            r'\bis\b': 'iz',
            r'\bare\b': 'r',
            r'\bam\b': 'iz',
            r'\bwas\b': 'wuz',
            r'\bwere\b': 'wuz',
            r'\bhave\b': 'haz',
            r'\bhas\b': 'haz',
            r'\bhad\b': 'had',
            r'\bcan\b': 'can',
            r'\bcould\b': 'cud',
            r'\bshould\b': 'shud',
            r'\bwould\b': 'wud',
            r'\bwill\b': 'will',
            r'\bwon\'t\b': 'wont',
            r'\bcan\'t\b': 'cant',
            r'\bdon\'t\b': 'dont',
            r'\bdoesn\'t\b': 'duznt',
            r'\bdidn\'t\b': 'didnt',
            r'\bfor\b': '4',
            r'\bfrom\b': 'frum',
            r'\bwith\b': 'wif',
            r'\bwithout\b': 'wifout',
            r'\bthat\b': 'dat',
            r'\bthis\b': 'dis',
            r'\bthese\b': 'deez',
            r'\bthose\b': 'doze',
            r'\bwhat\b': 'wut',
            r'\bwhen\b': 'wen',
            r'\bwhere\b': 'wher',
            r'\bwhy\b': 'y',
            r'\bhow\b': 'how',
            r'\bme\b': 'meh',
            r'\bmy\b': 'mah',
            r'\bmine\b': 'minez',
            r'\byou\b': 'u',
            r'\byour\b': 'ur',
            r'\byours\b': 'urz',
            r'\blike\b': 'liek',
            r'\blove\b': 'luv',
            r'\bhate\b': 'haet',
            r'\bwant\b': 'wants',
            r'\bneed\b': 'needz',
            r'\bthink\b': 'fink',
            r'\bknow\b': 'knoes',
            r'\bsay\b': 'sez',
            r'\bsaid\b': 'sez',
            r'\bgo\b': 'goe',
            r'\bgoing\b': 'goin',
            r'\bcome\b': 'come',
            r'\bcoming\b': 'comin',
            r'\bsee\b': 'see',
            r'\blook\b': 'luk',
            r'\bmake\b': 'maek',
            r'\bget\b': 'git',
            r'\btake\b': 'taek',
            r'\bgive\b': 'giv',
            r'\bfind\b': 'findz',
            r'\btell\b': 'tellz',
            r'\bask\b': 'askz',
            r'\bwork\b': 'werk',
            r'\bplay\b': 'plai',
            r'\beat\b': 'eatz',
            r'\bsleep\b': 'sleepz',
            r'\bcat\b': 'kitteh',
            r'\bcats\b': 'kittehs',
            r'\bkitty\b': 'kitteh',
            r'\bkitten\b': 'kitteh',
            r'\bhello\b': 'oh hai',
            r'\bhi\b': 'oh hai',
            r'\bhey\b': 'oh hai',
            r'\bgoodbye\b': 'kthxbai',
            r'\bbye\b': 'kthxbai',
            r'\bthanks\b': 'thxbai',
            r'\bthank you\b': 'thanx',
            r'\bplease\b': 'plz',
            r'\bokay\b': 'okai',
            r'\bok\b': 'k',
            r'\byes\b': 'yus',
            r'\bno\b': 'noes',
            r'\bsorry\b': 'sorryz',
            r'\bhappy\b': 'happi',
            r'\bsad\b': 'sad kitteh',
            r'\bangry\b': 'angryz',
            r'\bcute\b': 'kyoot',
            r'\bfunny\b': 'funneh',
            r'\bawesome\b': 'awsum',
            r'\bgreat\b': 'graet',
            r'\bgood\b': 'gud',
            r'\bbad\b': 'bad',
            r'\bvery\b': 'very',
            r'\breally\b': 'rilly',
            r'\bmore\b': 'moar',
            r'\bless\b': 'les',
            r'\bbig\b': 'big',
            r'\bsmall\b': 'smol',
            r'\bfood\b': 'foodz',
            r'\bcheese\b': 'cheezburger',
            r'\bburger\b': 'cheezburger',
            r'\bpizza\b': 'peetza',
            r'\bdog\b': 'doge',
            r'\bdogs\b': 'doges',
            r'\bpeople\b': 'hoomans',
            r'\bperson\b': 'hooman',
            r'\bhuman\b': 'hooman',
            r'\bhumans\b': 'hoomans',
            r'\btime\b': 'tiem',
            r'\bday\b': 'dai',
            r'\bnight\b': 'nite',
            r'\btoday\b': '2day',
            r'\btomorrow\b': '2morro',
            r'\byesterday\b': 'yesturday',
            r'\bnow\b': 'nao',
            r'\blater\b': 'l8r',
            r'\bnever\b': 'nevr',
            r'\balways\b': 'alwayz',
            r'\bsometimes\b': 'sumtiemz',
            r'\bmaybe\b': 'mebbe',
            r'\bprobably\b': 'prolly',
            r'\bdefinitely\b': 'defnitly',
            r'\bobviously\b': 'obviusly',
            r'\bseriously\b': 'srsly',
            r'\bliterally\b': 'literlly',
            r'\bactually\b': 'akshully',
            r'\bbasically\b': 'basicly',
        }

    def on_plugin_load(self):
        self.add_on_send_message_hook()

    def create_settings(self):
        return [
            Header(text="LOLCAT Settings"),
            Switch(
                key="enabled",
                text="Enable LOLCAT Translation",
                default=True,
                subtext="Automatically translate all messages to LOLCAT speak",
                icon="msg_translate"
            ),
            Divider(text="All your messages will be translated to LOLCAT when enabled")
        ]

    def translate_to_lolcat(self, text: str) -> str:
        result = text
        
        for pattern, replacement in self.lolcat_dict.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        result = re.sub(r'ing\b', 'in', result, flags=re.IGNORECASE)
        result = re.sub(r'er\b', 'r', result, flags=re.IGNORECASE)
        
        return result

    def on_send_message_hook(self, account: int, params: Any) -> HookResult:
        enabled = self.get_setting("enabled", True)
        
        if not enabled:
            return HookResult()
        
        if not isinstance(params.message, str):
            return HookResult()
        
        if not params.message.strip():
            return HookResult()
        
        try:
            translated = self.translate_to_lolcat(params.message)
            params.message = translated
            
            return HookResult(strategy=HookStrategy.MODIFY, params=params)
            
        except Exception as e:
            log(f"LOLCAT plugin error: {str(e)}")
            return HookResult()