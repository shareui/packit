from ui.settings import Header, Input, Divider, Switch, Text
from elyx import strings


class RepositoriesSettings:
    def __init__(self, repoManager):
        self.repoManager = repoManager
    
    def build(self):
        repos = self.repoManager.getRepositories()
        
        # Если репозиториев нет, создаем первый с дефолтными значениями
        if not repos:
            self.repoManager.addRepository(isFirst=True)
            repos = self.repoManager.getRepositories()
        
        settingsList = [
            Header(text=strings.repositories),
            Text(
                text=strings.add_repository,
                icon="msg_add",
                on_click=lambda view: self.repoManager.addRepository(isFirst=False)
            ),
            Divider()
        ]
        
        def makeOnChange(field, i):
            return lambda value: self.repoManager.updateRepoField(i, field, value)
        
        def makeOnRemove(i):
            return lambda view: self.repoManager.removeRepository(i)
        
        def makeOnToggleCollapse(i):
            def toggle(view):
                repos = self.repoManager.getRepositories()
                if i < len(repos):
                    repos[i]['collapsed'] = not repos[i].get('collapsed', False)
                    self.repoManager.setRepositories(repos)
            return toggle
        
        for idx, repo in enumerate(repos):
            isCollapsed = repo.get("collapsed", False)
            isEnabled = repo.get("enabled", True)
            
            collapseIcon = "msg_go_up" if not isCollapsed else "arrow_more_solar"
            headerText = strings("repository_form", idx + 1)
            
            settingsList.append(Text(
                text=headerText,
                icon=collapseIcon,
                accent=isEnabled,
                on_click=makeOnToggleCollapse(idx)
            ))
            
            if not isCollapsed:
                if len(repos) > 1:
                    settingsList.append(Text(
                        text=strings.remove_repository,
                        icon="msg_filled_blocked_solar",
                        red=True,
                        on_click=makeOnRemove(idx)
                    ))
                
                settingsList.extend([
                    Switch(
                        key=f"repo_enabled_{repo['id']}",
                        text=strings.repo_enabled,
                        default=repo.get("enabled", True),
                        icon="msg_customize",
                        on_change=makeOnChange("enabled", idx)
                    ),
                    Input(
                        key=f"repo_name_{repo['id']}",
                        text=strings.repo_name,
                        default=repo.get("name", ""),
                        icon="msg_edit",
                        on_change=makeOnChange("name", idx)
                    ),
                    Input(
                        key=f"repo_url_{repo['id']}",
                        text=strings.repo_url,
                        default=repo.get("url", ""),
                        icon="msg_link",
                        on_change=makeOnChange("url", idx)
                    )
                ])
            
            settingsList.append(Divider())
        
        if settingsList and isinstance(settingsList[-1], Divider):
            settingsList.pop()
        
        return settingsList