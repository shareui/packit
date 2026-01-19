from typing import Any
from base_plugin import HookResult, HookStrategy
from elyx import strings, settings


class CommandProcessor:
    def __init__(self, plugin):
        self.plugin = plugin
    
    def processMessage(self, params: Any) -> HookResult:
        if not isinstance(params.message, str):
            return HookResult()
        
        messageText = params.message.strip()
        
        cmdInfo = settings.get("cmd_info", "packit info")
        cmdSearch = settings.get("cmd_search", "packit search")
        cmdInstall = settings.get("cmd_install", "packit install")
        cmdUninstall = settings.get("cmd_uninstall", "packit uninstall")
        cmdPluginlist = settings.get("cmd_pluginlist", "packit pluginlist")
        cmdRepolist = settings.get("cmd_repolist", "packit repolist")
        cmdShare = settings.get("cmd_share", "packit share")
        cmdUpdate = settings.get("cmd_update", "packit update")
        cmdUpgrade = settings.get("cmd_upgrade", "packit upgrade")
        
        if messageText.startswith(cmdInfo):
            return self._handleInfo(messageText, params)
        
        if messageText.startswith(cmdSearch):
            return self._handleSearch(messageText, params)
        
        if messageText.startswith(cmdInstall):
            return self._handleInstall(messageText, params)
        
        if messageText.startswith(cmdUninstall):
            return self._handleUninstall(messageText, params)
        
        if messageText.startswith(cmdPluginlist):
            return self._handlePluginList(messageText, params)
        
        if messageText.startswith(cmdRepolist):
            return self._handleRepoList(messageText, params)
        
        if messageText.startswith(cmdShare):
            return self._handleShare(messageText, params)
        
        if messageText.startswith(cmdUpdate):
            return self._handleUpdate(messageText, params)
        
        if messageText.startswith(cmdUpgrade):
            return self._handleUpgrade(messageText, params)
        
        return HookResult()
    
    def _handleInfo(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
    
    def _handleSearch(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
    
    def _handleInstall(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
    
    def _handleUninstall(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
    
    def _handlePluginList(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
    
    def _handleRepoList(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
    
    def _handleShare(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
    
    def _handleUpdate(self, messageText: str, params: Any) -> HookResult:
        self.plugin.core.updateAllRepositories(silent=False)
        return HookResult(strategy=HookStrategy.CANCEL)
    
    def _handleUpgrade(self, messageText: str, params: Any) -> HookResult:
        params.message = strings.not_ready
        return HookResult(strategy=HookStrategy.MODIFY, params=params)