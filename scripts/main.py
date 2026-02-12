import os
import json
import hashlib
import re
import yaml
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def normalizePath(inputPath: str) -> str:
    return str(Path(inputPath).resolve())

def isCyrillic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    cyrillicCount = sum(1 for c in letters if '\u0400' <= c <= '\u04FF')
    return cyrillicCount / len(letters) > 0.8

def translateText(text: str) -> Optional[str]:
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src="en", dest="ru")
        return result.text
    except ImportError:
        print(f"{Colors.YELLOW}googletrans not installed, skipping translation{Colors.RESET}")
        print(f"{Colors.DIM}install: pip install googletrans==4.0.0-rc1{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}translation error: {e}{Colors.RESET}")
        return None

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def readPluginIdFromFile(filePath: str) -> Optional[str]:
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read(1000)
            match = re.search(r'__id__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except Exception:
        pass
    return None

def findPluginByFilename(repoConfig: Dict, filename: str) -> Optional[Tuple[int, str]]:
    for i, plugin in enumerate(repoConfig["plugins"]):
        link = plugin.get("link", "")
        if link:
            linkFilename = link.split("/")[-1]
            if linkFilename == filename:
                return (i, plugin["id"])
    return None

def calculateSha256(filePath: str) -> str:
    sha256Hash = hashlib.sha256()
    with open(filePath, "rb") as f:
        for byteBlock in iter(lambda: f.read(4096), b""):
            sha256Hash.update(byteBlock)
    return sha256Hash.hexdigest()

def parseVersion(versionString: str, stateKeywords: str) -> Tuple[str, str]:
    versionString = versionString.strip()

    keywordsList = [kw.strip() for kw in stateKeywords.split(',')]

    stateMap = {
        'alpha': 'alpha',
        'beta': 'beta',
        'dev': 'dev',
        'rc': 'rc',
        'release': 'release',
        'rel': 'release',
        'stable': 'release'
    }

    foundState = 'release'
    cleanVersion = versionString

    lowerVersion = versionString.lower()
    for keyword in keywordsList:
        keyword = keyword.lower()
        if keyword in lowerVersion:
            foundState = stateMap.get(keyword, keyword)
            cleanVersion = re.sub(rf'\b{re.escape(keyword)}\b', '', versionString, flags=re.IGNORECASE)
            break

    cleanVersion = re.sub(r'[^\d.]', '', cleanVersion).strip('.')

    if not cleanVersion:
        cleanVersion = '0.0.0'

    return cleanVersion, foundState

def compareVersions(version1: str, version2: str) -> int:
    v1Parts = [int(x) for x in version1.split('.')]
    v2Parts = [int(x) for x in version2.split('.')]

    maxLen = max(len(v1Parts), len(v2Parts))
    v1Parts.extend([0] * (maxLen - len(v1Parts)))
    v2Parts.extend([0] * (maxLen - len(v2Parts)))

    for i in range(maxLen):
        if v1Parts[i] > v2Parts[i]:
            return 1
        elif v1Parts[i] < v2Parts[i]:
            return -1

    return 0

def resolveConflicts(oldPlugin: Dict, newPlugin: Dict, filename: str) -> Dict:
    excludeKeys = {"version", "state", "hash"}
    resolvedPlugin = newPlugin.copy()

    conflicts = []
    for key in newPlugin.keys():
        if key in excludeKeys:
            continue

        if key in oldPlugin:
            oldValue = oldPlugin[key]
            newValue = newPlugin[key]

            if oldValue != newValue:
                conflicts.append((key, oldValue, newValue))

    if not conflicts:
        return resolvedPlugin

    print(f"\n{Colors.RED}{Colors.BOLD}conflicts found in {filename}:{Colors.RESET}")
    print()

    for key, oldValue, newValue in conflicts:
        print(f"{Colors.YELLOW}conflict in field: {Colors.BOLD}{key}{Colors.RESET}")
        print(f"  {Colors.DIM}old:{Colors.RESET} {oldValue}")
        print(f"  {Colors.DIM}new:{Colors.RESET} {newValue}")
        print(f"{Colors.GREEN}1{Colors.RESET}. apply old")
        print(f"{Colors.GREEN}2{Colors.RESET}. apply new")
        print(f"{Colors.GREEN}3{Colors.RESET}. enter a value")

        while True:
            choice = input(f"{Colors.CYAN}choose option: {Colors.RESET}").strip()
            if choice == "1":
                resolvedPlugin[key] = oldValue
                print(f"{Colors.GREEN}keeping old value for {key}{Colors.RESET}")
                break
            elif choice == "2":
                resolvedPlugin[key] = newValue
                print(f"{Colors.GREEN}applying new value for {key}{Colors.RESET}")
                break
            elif choice == "3":
                customValue = input(f"enter custom value for {key}: ").strip()
                resolvedPlugin[key] = customValue
                print(f"{Colors.GREEN}applied custom value for {key}{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}invalid option, choose 1, 2 or 3{Colors.RESET}")

        print()

    return resolvedPlugin

def createBackup(configPath: str, backupDir: str, enabled: bool):
    if not enabled:
        return

    if not os.path.exists(configPath):
        return

    os.makedirs(backupDir, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%H-%M-%S")
    datestamp = now.strftime("%d-%m-%Y")
    backupFilename = f"backup-{timestamp}-{datestamp}.json"
    backupPath = os.path.join(backupDir, backupFilename)

    with open(configPath, 'r', encoding='utf-8') as src:
        with open(backupPath, 'w', encoding='utf-8') as dst:
            dst.write(src.read())

    print(f"{Colors.BLUE}backup created: {backupFilename}{Colors.RESET}")

def loadConfig(configFile: str = "cfg.yml") -> Dict:
    if os.path.exists(configFile):
        with open(configFile, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        requiredKeys = {
            "addAbout": ("add about? (y/n): ", bool),
            "addDescription": ("add description? (y/n): ", bool),
            "addHash": ("add hash? (y/n): ", bool),
            "writeLastLog": ("write last log? (y/n): ", bool),
            "createForPost": ("create for post? (y/n): ", bool),
            "createBackups": ("create backups? (y/n): ", bool),
            "allowDowngrade": ("allow version downgrade? (y/n): ", bool),
            "manualInputDescriptions": ("manually input descriptions? (y/n): ", bool),
            "manualInputAbout": ("manually input about (EN/RU)? (y/n): ", bool),
            "appendToLogs": ("append to logs instead of overwriting? (y/n): ", bool),
            "configPath": ("path to repository config? (default: config.json): ", str),
            "workingDir": ("path to dir working plugins? (default: workingdir): ", str),
            "backupDir": ("path to backup directory? (default: backups): ", str),
            "stateKeywords": ("state keywords (comma separated, default: alpha,beta,dev,rc,release,rel,stable): ", str),
            "rawDirUrl": ("raw directory url? (default: https://raw.githubusercontent.com/user/repo/refs/heads/main/plugins): ", str)
        }

        configUpdated = False

        for key, (prompt, valueType) in requiredKeys.items():
            if key not in config:
                print(f"missing config key: {key}")

                if valueType == bool:
                    config[key] = input(prompt).lower() == 'y'
                else:
                    if key == "configPath":
                        while True:
                            value = input(prompt).strip()
                            if not value:
                                value = "config.json"

                            normalizedPath = normalizePath(value)

                            if os.path.exists(normalizedPath):
                                config[key] = normalizedPath
                                break
                            else:
                                print(f"file '{normalizedPath}' not found")
                                create = input("create it? (y/n): ").lower()
                                if create == 'y':
                                    try:
                                        dirPath = os.path.dirname(normalizedPath)
                                        if dirPath:
                                            os.makedirs(dirPath, exist_ok=True)
                                        with open(normalizedPath, 'w', encoding='utf-8') as f:
                                            json.dump({"plugins": []}, f, indent=2, ensure_ascii=False)
                                        print(f"created {normalizedPath}")
                                        config[key] = normalizedPath
                                        break
                                    except Exception as e:
                                        print(f"failed to create file: {e}")
                                else:
                                    print("enter valid path")
                    elif key in ["workingDir", "backupDir"]:
                        defaultValue = "workingdir" if key == "workingDir" else "backups"
                        while True:
                            value = input(prompt).strip()
                            if not value:
                                value = defaultValue

                            normalizedPath = normalizePath(value)

                            if os.path.exists(normalizedPath) and os.path.isdir(normalizedPath):
                                config[key] = normalizedPath
                                break
                            else:
                                print(f"directory '{normalizedPath}' not found")
                                create = input("create it? (y/n): ").lower()
                                if create == 'y':
                                    try:
                                        os.makedirs(normalizedPath, exist_ok=True)
                                        print(f"created {normalizedPath}/")
                                        config[key] = normalizedPath
                                        break
                                    except Exception as e:
                                        print(f"failed to create directory: {e}")
                                else:
                                    print("enter valid path")
                    else:
                        value = input(prompt).strip()
                        if not value:
                            if "state keywords" in prompt:
                                value = "alpha,beta,dev,rc,release,rel,stable"
                            elif "raw directory url" in prompt:
                                value = "https://raw.githubusercontent.com/user/repo/refs/heads/main/plugins"
                        config[key] = value

                configUpdated = True

        if configUpdated:
            with open(configFile, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            print(f"configuration updated in {configFile}")
            print()

        return config

    return None

def createConfig(configFile: str = "cfg.yml") -> Dict:
    print("first run configuration")
    print()

    addAbout = input("add about? (y/n): ").lower() == 'y'
    addDescription = input("add description? (y/n): ").lower() == 'y'
    addHash = input("add hash? (y/n): ").lower() == 'y'
    writeLastLog = input("write last log? (y/n): ").lower() == 'y'
    createForPost = input("create for post? (y/n): ").lower() == 'y'
    createBackups = input("create backups? (y/n): ").lower() == 'y'
    allowDowngrade = input("allow version downgrade? (y/n): ").lower() == 'y'
    manualInputDescriptions = input("manually input descriptions? (y/n): ").lower() == 'y'
    manualInputAbout = input("manually input about (EN/RU)? (y/n): ").lower() == 'y'
    appendToLogs = input("append to logs instead of overwriting? (y/n): ").lower() == 'y'

    defaultConfigPath = "config.json"
    while True:
        configPath = input(f"path to repository config? (default: {defaultConfigPath}): ").strip()
        if not configPath:
            configPath = defaultConfigPath

        normalizedPath = normalizePath(configPath)

        if os.path.exists(normalizedPath):
            configPath = normalizedPath
            break
        else:
            print(f"file '{normalizedPath}' not found")
            create = input("create it? (y/n): ").lower()
            if create == 'y':
                try:
                    dirPath = os.path.dirname(normalizedPath)
                    if dirPath:
                        os.makedirs(dirPath, exist_ok=True)
                    with open(normalizedPath, 'w', encoding='utf-8') as f:
                        json.dump({"plugins": []}, f, indent=2, ensure_ascii=False)
                    print(f"created {normalizedPath}")
                    configPath = normalizedPath
                    break
                except Exception as e:
                    print(f"failed to create file: {e}")
            else:
                print("enter valid path")

    defaultWorkingDir = "workingdir"
    while True:
        workingDir = input(f"path to dir working plugins? (default: {defaultWorkingDir}): ").strip()
        if not workingDir:
            workingDir = defaultWorkingDir

        normalizedPath = normalizePath(workingDir)

        if os.path.exists(normalizedPath) and os.path.isdir(normalizedPath):
            workingDir = normalizedPath
            break
        else:
            print(f"directory '{normalizedPath}' not found")
            create = input("create it? (y/n): ").lower()
            if create == 'y':
                try:
                    os.makedirs(normalizedPath, exist_ok=True)
                    print(f"created {normalizedPath}/")
                    workingDir = normalizedPath
                    break
                except Exception as e:
                    print(f"failed to create directory: {e}")
            else:
                print("enter valid path")

    defaultBackupDir = "backups"
    while True:
        backupDir = input(f"path to backup directory? (default: {defaultBackupDir}): ").strip()
        if not backupDir:
            backupDir = defaultBackupDir

        normalizedPath = normalizePath(backupDir)

        if os.path.exists(normalizedPath) and os.path.isdir(normalizedPath):
            backupDir = normalizedPath
            break
        else:
            print(f"directory '{normalizedPath}' not found")
            create = input("create it? (y/n): ").lower()
            if create == 'y':
                try:
                    os.makedirs(normalizedPath, exist_ok=True)
                    print(f"created {normalizedPath}/")
                    backupDir = normalizedPath
                    break
                except Exception as e:
                    print(f"failed to create directory: {e}")
            else:
                print("enter valid path")

    defaultStateKeywords = "alpha,beta,dev,rc,release,rel,stable"
    stateKeywords = input(f"state keywords (comma separated, default: {defaultStateKeywords}): ").strip()
    if not stateKeywords:
        stateKeywords = defaultStateKeywords

    defaultRawDirUrl = "https://raw.githubusercontent.com/user/repo/refs/heads/main/plugins"
    rawDirUrl = input(f"raw directory url? (default: {defaultRawDirUrl}): ").strip()
    if not rawDirUrl:
        rawDirUrl = defaultRawDirUrl

    config = {
        "addAbout": addAbout,
        "addDescription": addDescription,
        "addHash": addHash,
        "writeLastLog": writeLastLog,
        "createForPost": createForPost,
        "createBackups": createBackups,
        "allowDowngrade": allowDowngrade,
        "manualInputDescriptions": manualInputDescriptions,
        "manualInputAbout": manualInputAbout,
        "appendToLogs": appendToLogs,
        "configPath": configPath,
        "workingDir": workingDir,
        "backupDir": backupDir,
        "stateKeywords": stateKeywords,
        "rawDirUrl": rawDirUrl
    }

    with open(configFile, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print()
    print(f"configuration saved to {configFile}")
    print()

    return config

def extractMetadata(filePath: str, filename: str) -> Dict[str, any]:
    metadata = {
        "id": "Unknown",
        "name": "Unknown",
        "author": "Unknown",
        "description": "Unknown",
        "version": "Unknown",
        "icon": "Unknown",
        "dependencies": []
    }

    missingFields = []

    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()

        patterns = {
            "id": r'__id__\s*=\s*["\']([^"\']*)["\']',
            "name": r'__name__\s*=\s*["\']([^"\']*)["\']',
            "description": r'__description__\s*=\s*["\']([^"\']+?)["\']',
            "author": r'__author__\s*=\s*["\']([^"\']*)["\']',
            "version": r'__version__\s*=\s*["\']([^"\']*)["\']',
            "icon": r'__icon__\s*=\s*["\']([^"\']*)["\']',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                value = match.group(1)
                if not value or not value.strip():
                    missingFields.append(key)
                    continue
                if value and '\n' in value and key != "description":
                    value = ' '.join(line.strip() for line in value.split('\n') if line.strip())
                metadata[key] = value
            else:
                missingFields.append(key)

        depMatch = re.search(r'__dependencies__\s*=\s*\[([^\]]*)\]', content)
        if depMatch:
            depsStr = depMatch.group(1)
            deps = re.findall(r'["\']([^"\']+)["\']', depsStr)
            metadata["dependencies"] = deps

        if missingFields:
            missingStr = ', '.join(missingFields)
            print(f"{Colors.YELLOW}{filename}{Colors.RESET} missing {Colors.RED}{missingStr}{Colors.RESET} {Colors.DIM}(set to Unknown){Colors.RESET}")

    except Exception as e:
        print(f"{Colors.RED}{filename} failed {e}{Colors.RESET}")
        raise

    return metadata

def createPluginEntry(filePath: str, filename: str, config: Dict) -> Dict[str, any]:
    metadata = extractMetadata(filePath, filename)

    stateKeywords = config.get("stateKeywords", "alpha,beta,dev,rc,release,rel,stable")
    versionNumber, versionState = parseVersion(metadata["version"], stateKeywords)

    rawDirUrl = config.get("rawDirUrl", "https://raw.githubusercontent.com/user/repo/refs/heads/main/plugins")

    pluginEntry = {
        "id": metadata["id"],
        "name": metadata["name"],
        "author": metadata["author"],
        "version": versionNumber,
        "state": versionState,
        "icon": metadata["icon"],
        "suspicious": "false",
        "dependencies": metadata["dependencies"],
        "link": f"{rawDirUrl}/{filename}"
    }

    if config.get("manualInputAbout", False):
        print(f"\n{Colors.CYAN}Enter about for plugin {filename}:{Colors.RESET}")
        aboutEn = input("Enter description on English: ").strip()
        while not aboutEn:
            print(f"{Colors.RED}English description is required{Colors.RESET}")
            aboutEn = input("Enter description on English: ").strip()

        aboutRu = input("Enter description on Russian (or type 'skip'): ").strip()

        if aboutRu.lower() == 'skip':
            pluginEntry["about"] = [aboutEn]
        else:
            pluginEntry["about"] = [aboutEn, aboutRu]
    elif config.get("addAbout", True):
        # auto-translate description to russian if available
        description = metadata.get("description", "")
        
        if description and description != "Unknown":
            # check if description is already in cyrillic (russian)
            if isCyrillic(description):
                # description is russian, use as-is for both
                pluginEntry["about"] = [description, description]
            else:
                # description is english, translate to russian
                translatedDesc = translateText(description)
                
                if translatedDesc and translatedDesc != description:
                    # about[0] = english, about[1] = russian
                    pluginEntry["about"] = [description, translatedDesc]
                    time.sleep(0.5)  # delay to avoid rate limiting
                else:
                    # translation failed or unavailable
                    pluginEntry["about"] = [description]
        else:
            # no description, fallback to plugin name
            pluginEntry["about"] = metadata["name"]

    if config.get("manualInputDescriptions", False):
        print(f"\n{Colors.CYAN}current description for {filename}:{Colors.RESET}")
        print(f"{Colors.DIM}{metadata['description']}{Colors.RESET}")
        print()
        override = input("override description? (y/n): ").strip().lower()
        if override == 'y':
            customDesc = input("enter new description: ").strip()
            if customDesc:
                pluginEntry["description"] = customDesc
            else:
                pluginEntry["description"] = metadata["description"]
        else:
            pluginEntry["description"] = metadata["description"]
    elif config.get("addDescription", True):
        pluginEntry["description"] = metadata["description"]

    if config.get("addHash", True):
        pluginEntry["hash"] = calculateSha256(filePath)

    return pluginEntry

def buildHashMap(plugins: List[Dict]) -> Dict[str, int]:
    hashMap = {}
    for i, plugin in enumerate(plugins):
        if "hash" in plugin:
            hashMap[plugin["hash"]] = i
    return hashMap

def buildIdMap(plugins: List[Dict]) -> Dict[str, int]:
    idMap = {}
    for i, plugin in enumerate(plugins):
        if "id" in plugin:
            idMap[plugin["id"]] = i
    return idMap

def normalizeLoadedConfig(repoConfig: Dict):
    for plugin in repoConfig.get("plugins", []):
        if "description" in plugin and isinstance(plugin["description"], str):
            desc = plugin["description"]
            if '\\n' in desc:
                plugin["description"] = desc.replace('\\n', '\n')

def writeLatestLog(newPlugins: List[Dict], updatedPlugins: List[Dict], deletedPlugins: List[Dict], totalCount: int, appendMode: bool = False):
    latestLogPath = "latest.log"

    try:
        mode = 'a' if appendMode else 'w'
        with open(latestLogPath, mode, encoding='utf-8') as f:
            if appendMode:
                f.write("\n" + "="*50 + "\n")
            
            f.write(f"latest update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"total plugins: {totalCount}\n")
            f.write(f"added: {len(newPlugins)}\n")
            f.write(f"updated: {len(updatedPlugins)}\n")
            f.write(f"deleted: {len(deletedPlugins)}\n\n")

            if newPlugins:
                f.write("new plugins:\n")
                for plugin in newPlugins:
                    f.write(f"  - {plugin['name']} (id: {plugin['id']}, version: {plugin['version']})\n")
                f.write("\n")

            if updatedPlugins:
                f.write("updated plugins:\n")
                for plugin in updatedPlugins:
                    f.write(f"  - {plugin['name']} (id: {plugin['id']}, version: {plugin['version']})\n")
                f.write("\n")

            if deletedPlugins:
                f.write("deleted plugins:\n")
                for plugin in deletedPlugins:
                    f.write(f"  - {plugin['name']} (id: {plugin['id']}, version: {plugin['version']})\n")

        action = "appended to" if appendMode else "written"
        print(f"{Colors.BLUE}log {action}: {latestLogPath}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}log write failed {e}{Colors.RESET}")

def writeForPost(newPlugins: List[Dict], updatedPlugins: List[Dict], deletedPlugins: List[Dict], totalCount: int, appendMode: bool = False):
    forPostPath = "forpost.txt"

    try:
        mode = 'a' if appendMode else 'w'
        with open(forPostPath, mode, encoding='utf-8') as f:
            if appendMode:
                f.write("\n" + "="*50 + "\n")
            
            if newPlugins:
                f.write(f"Added {len(newPlugins)} plugins\n\n")
                for plugin in newPlugins:
                    f.write(f"{plugin['name']} by {plugin['author']}\n")
                f.write("\n")

            if updatedPlugins:
                f.write(f"Updated {len(updatedPlugins)} plugins\n\n")
                for plugin in updatedPlugins:
                    f.write(f"{plugin['name']} by {plugin['author']}\n")
                f.write("\n")

            if deletedPlugins:
                f.write(f"Removed {len(deletedPlugins)} plugins\n\n")
                for plugin in deletedPlugins:
                    f.write(f"{plugin['name']} by {plugin['author']}\n")
                f.write("\n")

            f.write(f"Total plugins: {totalCount}")

        action = "appended to" if appendMode else "written"
        print(f"{Colors.BLUE}post file {action}: {forPostPath}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}post file write failed {e}{Colors.RESET}")

def updateConfigJson(config: Dict):
    configPath = config["configPath"]
    workingDir = config["workingDir"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"config file '{configPath}' not found")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    normalizeLoadedConfig(repoConfig)

    if not os.path.exists(workingDir):
        print(f"directory '{workingDir}/' not found")
        return

    hashMap = buildHashMap(repoConfig.get("plugins", []))
    idMap = buildIdMap(repoConfig.get("plugins", []))

    newPlugins = []
    updatedPlugins = []
    filesProcessed = 0

    for filename in os.listdir(workingDir):
        filePath = os.path.join(workingDir, filename)

        if not os.path.isfile(filePath):
            continue

        try:
            fileHash = calculateSha256(filePath)

            if fileHash in hashMap:
                print(f"{Colors.DIM}{filename} skipped (hash already exists){Colors.RESET}")
                continue

            pluginEntry = createPluginEntry(filePath, filename, config)
            pluginId = pluginEntry["id"]

            if pluginId in idMap:
                pluginIndex = idMap[pluginId]
                oldPlugin = repoConfig["plugins"][pluginIndex]
                oldVersion = oldPlugin.get("version", "0.0.0")
                newVersion = pluginEntry["version"]
                oldHash = oldPlugin.get("hash", "no hash")

                versionComparison = compareVersions(newVersion, oldVersion)

                if versionComparison < 0:
                    allowDowngrade = config.get("allowDowngrade", False)

                    if not allowDowngrade:
                        print(f"{Colors.RED}{Colors.BOLD}{filename} WARNING: downgrade detected!{Colors.RESET}")
                        print(f"  {Colors.YELLOW}current: {oldVersion}, new: {newVersion}{Colors.RESET}")
                        confirm = input(f"  {Colors.CYAN}continue anyway? (y/n): {Colors.RESET}").lower()
                        if confirm != 'y':
                            print(f"{Colors.DIM}{filename} skipped{Colors.RESET}")
                            continue
                    else:
                        print(f"{Colors.YELLOW}{filename} downgrade: {oldVersion} -> {newVersion}{Colors.RESET}")

                resolvedPlugin = resolveConflicts(oldPlugin, pluginEntry, filename)

                repoConfig["plugins"][pluginIndex] = resolvedPlugin
                updatedPlugins.append(resolvedPlugin)
                filesProcessed += 1
                print(f"{Colors.GREEN}{filename} updated{Colors.RESET} (id: {Colors.CYAN}{pluginId}{Colors.RESET}, old hash: {oldHash[:8]}..., new hash: {fileHash[:8]}...)")
            else:
                newPlugins.append(pluginEntry)
                filesProcessed += 1
                print(f"{Colors.GREEN}{filename} added as new plugin{Colors.RESET} (id: {Colors.CYAN}{pluginId}{Colors.RESET})")

        except Exception as e:
            print(f"{Colors.RED}{filename} failed {e}{Colors.RESET}")

    if newPlugins:
        repoConfig["plugins"].extend(newPlugins)

    if newPlugins or updatedPlugins:
        createBackup(configPath, backupDir, createBackupsEnabled)

        with open(configPath, 'w', encoding='utf-8') as f:
            json.dump(repoConfig, f, indent=2, ensure_ascii=False)

        print()
        print(f"{Colors.BOLD}processed {filesProcessed} plugin(s){Colors.RESET}")
        print(f"{Colors.GREEN}added: {len(newPlugins)}{Colors.RESET}, {Colors.BLUE}updated: {len(updatedPlugins)}{Colors.RESET}")

        if config.get("writeLastLog", False):
            appendMode = config.get("appendToLogs", False)
            writeLatestLog(newPlugins, updatedPlugins, [], len(repoConfig["plugins"]), appendMode)

        if config.get("createForPost", False):
            appendMode = config.get("appendToLogs", False)
            writeForPost(newPlugins, updatedPlugins, [], len(repoConfig["plugins"]), appendMode)
    else:
        print("no new or updated plugins")

def changeFile(config: Dict):
    configPath = config["configPath"]
    workingDir = config["workingDir"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"config file '{configPath}' not found")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    filename = input("enter file name: ").strip()
    filePath = os.path.join(workingDir, filename)

    if not os.path.exists(filePath):
        print(f"{filename} not found in {workingDir}/")
        return

    pluginId = readPluginIdFromFile(filePath)
    pluginIndex = None

    if pluginId:
        for i, plugin in enumerate(repoConfig["plugins"]):
            if plugin["id"] == pluginId:
                pluginIndex = i
                break

    if pluginIndex is None:
        print(f"{Colors.YELLOW}cannot extract plugin id from file, searching by filename...{Colors.RESET}")
        result = findPluginByFilename(repoConfig, filename)
        if result:
            pluginIndex, pluginId = result
            print(f"{Colors.GREEN}found plugin by filename: {pluginId}{Colors.RESET}")

    if pluginIndex is None:
        print(f"{Colors.RED}plugin not found (neither by id nor by filename){Colors.RESET}")
        return

    try:
        createBackup(configPath, backupDir, createBackupsEnabled)

        newPluginEntry = createPluginEntry(filePath, filename, config)
        repoConfig["plugins"][pluginIndex] = newPluginEntry

        with open(configPath, 'w', encoding='utf-8') as f:
            json.dump(repoConfig, f, indent=2, ensure_ascii=False)

        print(f"{Colors.GREEN}{pluginId} updated with {filename}{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.RED}{filename} failed {e}{Colors.RESET}")

def deleteFiles(config: Dict):
    configPath = config["configPath"]
    workingDir = config["workingDir"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"config file '{configPath}' not found")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    filename = input("enter filename: ").strip()
    filePath = os.path.join(workingDir, filename)

    if not os.path.exists(filePath):
        print(f"{filename} not found in {workingDir}/")
        return

    pluginId = readPluginIdFromFile(filePath)
    pluginIndex = None

    if pluginId:
        for i, plugin in enumerate(repoConfig["plugins"]):
            if plugin["id"] == pluginId:
                pluginIndex = i
                break

    if pluginIndex is None:
        print(f"{Colors.YELLOW}cannot extract plugin id from file, searching by filename...{Colors.RESET}")
        result = findPluginByFilename(repoConfig, filename)
        if result:
            pluginIndex, pluginId = result
            print(f"{Colors.GREEN}found plugin by filename: {pluginId}{Colors.RESET}")

    if pluginIndex is None:
        print(f"{Colors.RED}plugin not found (neither by id nor by filename){Colors.RESET}")
        return

    createBackup(configPath, backupDir, createBackupsEnabled)

    deletedPlugin = repoConfig["plugins"].pop(pluginIndex)

    with open(configPath, 'w', encoding='utf-8') as f:
        json.dump(repoConfig, f, indent=2, ensure_ascii=False)

    print(f"{Colors.RED}{pluginId} deleted from config{Colors.RESET}")

    if os.path.exists(filePath):
        os.remove(filePath)
        print(f"{filename} deleted from repository")

    if config.get("writeLastLog", False):
        appendMode = config.get("appendToLogs", False)
        writeLatestLog([], [], [deletedPlugin], len(repoConfig["plugins"]), appendMode)

    if config.get("createForPost", False):
        appendMode = config.get("appendToLogs", False)
        writeForPost([], [], [deletedPlugin], len(repoConfig["plugins"]), appendMode)

def clearMissingPlugins(config: Dict):
    configPath = config["configPath"]
    workingDir = config["workingDir"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"config file '{configPath}' not found")
        return

    if not os.path.exists(workingDir):
        print(f"directory '{workingDir}/' not found")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    existingFiles = set()
    for filename in os.listdir(workingDir):
        filePath = os.path.join(workingDir, filename)
        if os.path.isfile(filePath):
            existingFiles.add(filename)

    pluginsToKeep = []
    deletedPlugins = []
    removedCount = 0

    for plugin in repoConfig["plugins"]:
        link = plugin.get("link", "")
        filename = link.split("/")[-1] if link else ""

        if filename in existingFiles:
            pluginsToKeep.append(plugin)
        else:
            print(f"removed {plugin['id']} (file not found: {filename})")
            deletedPlugins.append(plugin)
            removedCount += 1

    if removedCount > 0:
        createBackup(configPath, backupDir, createBackupsEnabled)

        repoConfig["plugins"] = pluginsToKeep

        with open(configPath, 'w', encoding='utf-8') as f:
            json.dump(repoConfig, f, indent=2, ensure_ascii=False)

        print()
        print(f"removed {removedCount} missing plugin(s)")
        print(f"remaining plugins: {len(pluginsToKeep)}")

        if config.get("writeLastLog", False):
            appendMode = config.get("appendToLogs", False)
            writeLatestLog([], [], deletedPlugins, len(pluginsToKeep), appendMode)

        if config.get("createForPost", False):
            appendMode = config.get("appendToLogs", False)
            writeForPost([], [], deletedPlugins, len(pluginsToKeep), appendMode)
    else:
        print("all plugins have corresponding files")

def dirStatus(config: Dict):
    configPath = config["configPath"]
    workingDir = config["workingDir"]

    if not os.path.exists(configPath):
        print(f"config file '{configPath}' not found")
        return

    if not os.path.exists(workingDir):
        print(f"directory '{workingDir}/' not found")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    hashMap = buildHashMap(repoConfig.get("plugins", []))
    idMap = buildIdMap(repoConfig.get("plugins", []))

    existingFiles = set()
    for plugin in repoConfig["plugins"]:
        link = plugin.get("link", "")
        filename = link.split("/")[-1] if link else ""
        if filename:
            existingFiles.add(filename)

    willBeAdded = 0
    willBeUpdated = 0
    willBeRemoved = 0

    filesInDir = set()
    for filename in os.listdir(workingDir):
        filePath = os.path.join(workingDir, filename)

        if not os.path.isfile(filePath):
            continue

        filesInDir.add(filename)

        try:
            fileHash = calculateSha256(filePath)

            if fileHash in hashMap:
                continue

            metadata = extractMetadata(filePath, filename)
            pluginId = metadata.get("id", "Unknown")

            if pluginId in idMap:
                willBeUpdated += 1
            else:
                willBeAdded += 1
        except Exception:
            continue

    for filename in existingFiles:
        if filename not in filesInDir:
            willBeRemoved += 1

    print()
    print("if you start adding now")
    print(f"will be added: {willBeAdded}")
    print(f"will be updated: {willBeUpdated}")
    print(f"will be removed: {willBeRemoved}")

def editPluginValue(config: Dict):
    configPath = config["configPath"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"config file '{configPath}' not found")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    pluginId = input("enter plugin id: ").strip()

    pluginIndex = None
    for i, plugin in enumerate(repoConfig["plugins"]):
        if plugin["id"] == pluginId:
            pluginIndex = i
            break

    if pluginIndex is None:
        print(f"plugin with id '{pluginId}' not found")
        return

    currentPlugin = repoConfig["plugins"][pluginIndex]

    print()
    print(f"current values for {pluginId}:")
    for key, value in currentPlugin.items():
        print(f"  {key}: {value}")
    print()

    fieldName = input("enter field name to edit: ").strip()

    if fieldName not in currentPlugin:
        print(f"field '{fieldName}' not found")
        return

    print(f"current value: {currentPlugin[fieldName]}")
    newValue = input("enter new value: ").strip()

    createBackup(configPath, backupDir, createBackupsEnabled)

    repoConfig["plugins"][pluginIndex][fieldName] = newValue

    with open(configPath, 'w', encoding='utf-8') as f:
        json.dump(repoConfig, f, indent=2, ensure_ascii=False)

    print(f"field '{fieldName}' updated for {pluginId}")

def addItemToJson(config: Dict):
    configPath = config["configPath"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"config file '{configPath}' not found")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    pluginId = input("enter plugin id: ").strip()

    pluginIndex = None
    for i, plugin in enumerate(repoConfig["plugins"]):
        if plugin["id"] == pluginId:
            pluginIndex = i
            break

    if pluginIndex is None:
        print(f"plugin with id '{pluginId}' not found")
        return

    currentPlugin = repoConfig["plugins"][pluginIndex]

    print()
    print(f"current fields for {pluginId}:")
    for key in currentPlugin.keys():
        print(f"  {key}")
    print()

    fieldName = input("enter new field name: ").strip()

    if fieldName in currentPlugin:
        print(f"field '{fieldName}' already exists")
        return

    print("select data type:")
    print("1. string")
    print("2. number")
    print("3. boolean")
    print("4. array")
    print("5. object")

    dataType = input("choose type (1-5): ").strip()

    if dataType == "1":
        value = input("enter string value: ").strip()
    elif dataType == "2":
        valueInput = input("enter number value: ").strip()
        try:
            value = int(valueInput) if '.' not in valueInput else float(valueInput)
        except ValueError:
            print("invalid number format")
            return
    elif dataType == "3":
        value = input("enter boolean value (y/n): ").lower() == 'y'
    elif dataType == "4":
        arrayInput = input("enter array values (comma separated): ").strip()
        value = [item.strip() for item in arrayInput.split(',')] if arrayInput else []
    elif dataType == "5":
        print("enter object as JSON:")
        objectInput = input().strip()
        try:
            value = json.loads(objectInput)
        except json.JSONDecodeError:
            print("invalid JSON format")
            return
    else:
        print("invalid option")
        return

    createBackup(configPath, backupDir, createBackupsEnabled)

    repoConfig["plugins"][pluginIndex][fieldName] = value

    with open(configPath, 'w', encoding='utf-8') as f:
        json.dump(repoConfig, f, indent=2, ensure_ascii=False)

    print(f"field '{fieldName}' added to {pluginId} with value: {value}")

def editConfigValues(config: Dict):
    configFile = "cfg.yml"

    if not os.path.exists(configFile):
        print(f"config file '{configFile}' not found")
        return

    with open(configFile, 'r', encoding='utf-8') as f:
        currentConfig = yaml.safe_load(f)

    print()
    print("current config values:")
    for key, value in currentConfig.items():
        print(f"  {key}: {value}")
    print()

    fieldsToEdit = input("enter field names to edit (comma separated): ").strip()

    if not fieldsToEdit:
        print("no fields specified")
        return

    fieldsList = [field.strip() for field in fieldsToEdit.split(',')]

    for fieldName in fieldsList:
        if fieldName not in currentConfig:
            print(f"field '{fieldName}' not found, skipping")
            continue

        currentValue = currentConfig[fieldName]
        print(f"{fieldName} (current: {currentValue})")

        if isinstance(currentValue, bool):
            newValue = input("new value (y/n): ").lower() == 'y'
            currentConfig[fieldName] = newValue
        else:
            newValue = input("new value: ").strip()
            if newValue:
                # normalize paths for path-related fields
                if fieldName in ["configPath", "workingDir", "backupDir"]:
                    newValue = normalizePath(newValue)
                currentConfig[fieldName] = newValue

        print(f"{fieldName} updated")
        print()

    with open(configFile, 'w', encoding='utf-8') as f:
        yaml.dump(currentConfig, f, allow_unicode=True, default_flow_style=False)

    print(f"configuration updated in {configFile}")

    for key, value in currentConfig.items():
        config[key] = value

def resetAllPlugins(config: Dict):
    configPath = config["configPath"]
    workingDir = config["workingDir"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"{Colors.RED}config file '{configPath}' not found{Colors.RESET}")
        return

    if not os.path.exists(workingDir):
        print(f"{Colors.RED}directory '{workingDir}/' not found{Colors.RESET}")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    repometa = repoConfig.get("repometa", {})

    print(f"{Colors.YELLOW}{Colors.BOLD}WARNING: this will overwrite entire config.json{Colors.RESET}")
    print(f"{Colors.YELLOW}all plugins will be rechecked and rewritten{Colors.RESET}")
    confirm = input(f"{Colors.CYAN}continue? (y/n): {Colors.RESET}").lower()

    if confirm != 'y':
        print(f"{Colors.DIM}reset cancelled{Colors.RESET}")
        return

    createBackup(configPath, backupDir, createBackupsEnabled)

    newPlugins = []
    filesProcessed = 0

    for filename in os.listdir(workingDir):
        filePath = os.path.join(workingDir, filename)

        if not os.path.isfile(filePath):
            continue

        try:
            pluginEntry = createPluginEntry(filePath, filename, config)
            newPlugins.append(pluginEntry)
            filesProcessed += 1
            print(f"{Colors.GREEN}{filename} processed{Colors.RESET} (id: {Colors.CYAN}{pluginEntry['id']}{Colors.RESET})")
        except Exception as e:
            print(f"{Colors.RED}{filename} failed {e}{Colors.RESET}")

    repoConfig = {
        "repometa": repometa,
        "plugins": newPlugins
    }

    with open(configPath, 'w', encoding='utf-8') as f:
        json.dump(repoConfig, f, indent=2, ensure_ascii=False)

    print()
    print(f"{Colors.BOLD}reset complete{Colors.RESET}")
    print(f"{Colors.GREEN}total plugins: {len(newPlugins)}{Colors.RESET}")
    print(f"{Colors.BLUE}files processed: {filesProcessed}{Colors.RESET}")

    if config.get("writeLastLog", False):
        appendMode = config.get("appendToLogs", False)
        writeLatestLog(newPlugins, [], [], len(newPlugins), appendMode)

    if config.get("createForPost", False):
        appendMode = config.get("appendToLogs", False)
        writeForPost(newPlugins, [], [], len(newPlugins), appendMode)

def createGitignore():
    gitignorePath = ".gitignore"
    entries = ["cfg.yml", "forpost.txt", "latest.log", "backups/"]

    existingContent = ""
    if os.path.exists(gitignorePath):
        with open(gitignorePath, 'r', encoding='utf-8') as f:
            existingContent = f.read()

    entriesToAdd = []
    for entry in entries:
        if entry not in existingContent:
            entriesToAdd.append(entry)

    if not entriesToAdd:
        print("all entries already in .gitignore")
        return

    if os.path.exists(gitignorePath):
        with open(gitignorePath, 'a', encoding='utf-8') as f:
            if not existingContent.endswith('\n'):
                f.write('\n')
            for entry in entriesToAdd:
                f.write(f"{entry}\n")

        print(f"added to .gitignore: {', '.join(entriesToAdd)}")
    else:
        with open(gitignorePath, 'w', encoding='utf-8') as f:
            for entry in entriesToAdd:
                f.write(f"{entry}\n")

        print(f".gitignore created with: {', '.join(entriesToAdd)}")

def clearLogs():
    latestLogPath = "latest.log"
    forPostPath = "forpost.txt"
    
    filesCleared = []
    
    if os.path.exists(latestLogPath):
        try:
            os.remove(latestLogPath)
            filesCleared.append(latestLogPath)
        except Exception as e:
            print(f"{Colors.RED}failed to clear {latestLogPath}: {e}{Colors.RESET}")
    
    if os.path.exists(forPostPath):
        try:
            os.remove(forPostPath)
            filesCleared.append(forPostPath)
        except Exception as e:
            print(f"{Colors.RED}failed to clear {forPostPath}: {e}{Colors.RESET}")
    
    if filesCleared:
        print(f"{Colors.GREEN}cleared: {', '.join(filesCleared)}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}no log files found to clear{Colors.RESET}")

def resetPluginKey(config: Dict):
    configPath = config["configPath"]
    backupDir = config["backupDir"]
    createBackupsEnabled = config.get("createBackups", True)

    if not os.path.exists(configPath):
        print(f"{Colors.RED}config file '{configPath}' not found{Colors.RESET}")
        return

    with open(configPath, 'r', encoding='utf-8') as f:
        repoConfig = json.load(f)
    normalizeLoadedConfig(repoConfig)

    plugins = repoConfig.get("plugins", [])
    if not plugins:
        print(f"{Colors.YELLOW}no plugins in config{Colors.RESET}")
        return

    # show example plugin structure
    print(f"\n{Colors.CYAN}example plugin keys:{Colors.RESET}")
    firstPlugin = plugins[0]
    for key in firstPlugin.keys():
        print(f"  - {key}")
    print()

    keyName = input("enter key name to reset for all plugins: ").strip()
    if not keyName:
        print("no key specified")
        return

    # count how many plugins have this key
    pluginsWithKey = sum(1 for p in plugins if keyName in p)
    
    if pluginsWithKey == 0:
        print(f"{Colors.YELLOW}key '{keyName}' not found in any plugin{Colors.RESET}")
        return

    print(f"{Colors.YELLOW}{Colors.BOLD}WARNING: this will remove '{keyName}' from {pluginsWithKey} plugins{Colors.RESET}")
    confirm = input(f"{Colors.CYAN}continue? (y/n): {Colors.RESET}").lower()

    if confirm != 'y':
        print(f"{Colors.DIM}operation cancelled{Colors.RESET}")
        return

    createBackup(configPath, backupDir, createBackupsEnabled)

    # remove key from all plugins
    removedCount = 0
    for plugin in plugins:
        if keyName in plugin:
            del plugin[keyName]
            removedCount += 1

    with open(configPath, 'w', encoding='utf-8') as f:
        json.dump(repoConfig, f, indent=2, ensure_ascii=False)

    print()
    print(f"{Colors.GREEN}removed '{keyName}' from {removedCount} plugins{Colors.RESET}")

def showMenu(config: Dict):
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}    menu    {Colors.RESET}")
    print(f"{Colors.GREEN}1{Colors.RESET}. add files")
    print(f"{Colors.GREEN}2{Colors.RESET}. change file")
    print(f"{Colors.GREEN}3{Colors.RESET}. delete files")
    print(f"{Colors.GREEN}4{Colors.RESET}. clear missing plugins")
    print(f"{Colors.GREEN}5{Colors.RESET}. dir status")
    print(f"{Colors.GREEN}6{Colors.RESET}. edit plugin value")
    print(f"{Colors.GREEN}7{Colors.RESET}. add item to json")
    print(f"{Colors.GREEN}8{Colors.RESET}. edit config values")
    print(f"{Colors.GREEN}9{Colors.RESET}. rewrite script cfg")
    print(f"{Colors.GREEN}10{Colors.RESET}. create .gitignore for cfg.yml")
    print(f"{Colors.YELLOW}11{Colors.RESET}. clear logs/forpost")
    print(f"{Colors.YELLOW}12{Colors.RESET}. reset plugin key")
    print(f"{Colors.YELLOW}13{Colors.RESET}. reset (recheck all files)")
    print(f"{Colors.RED}14{Colors.RESET}. exit")
    
    print()
    choice = input(f"{Colors.CYAN}choose option: {Colors.RESET}").strip()
    return choice

if __name__ == "__main__":
    config = loadConfig()

    if config is None:
        config = createConfig()

    while True:
        choice = showMenu(config)

        if choice == "1":
            updateConfigJson(config)
        elif choice == "2":
            changeFile(config)
        elif choice == "3":
            deleteFiles(config)
        elif choice == "4":
            clearMissingPlugins(config)
        elif choice == "5":
            dirStatus(config)
        elif choice == "6":
            editPluginValue(config)
        elif choice == "7":
            addItemToJson(config)
        elif choice == "8":
            editConfigValues(config)
        elif choice == "9":
            config = createConfig()
        elif choice == "10":
            createGitignore()
        elif choice == "11":
            clearLogs()
        elif choice == "12":
            resetPluginKey(config)
        elif choice == "13":
            resetAllPlugins(config)
        elif choice == "14":
            print("exit")
            break
        else:
            print("invalid option")
