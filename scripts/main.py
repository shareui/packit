#!/usr/bin/env python3

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import json
from typing import Optional

import yaml

import configManager
import logWriter
import pluginReader
import scriptCfg
import translator
from versionUtils import compareVersions

PLUGIN_EXTENSIONS = {".plugin", ".elyx", ".eaf"}
IGNORED_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}

LOG_FILENAME = "latest.log"
FORPOST_FILENAME = "forpost.txt"

# colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_MAGENTA = "\033[35m"
C_CYAN = "\033[36m"
C_GRAY = "\033[90m"


def _print(msg: str = "") -> None:
    print(msg)


def _ask(prompt: str, default: str = "") -> str:
    try:
        value = input(prompt).strip()
        return value if value else default
    except (EOFError, KeyboardInterrupt):
        raise


def _confirm(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    raw = _ask(prompt + suffix).lower()
    if not raw:
        return default
    return raw.startswith("y")


def _requireCfg(cfg: dict) -> bool:
    for key in ["config_path", "working_dir"]:
        if not cfg.get(key):
            _print(f"{C_RED}[error]{C_RESET} cfg '{key}' is not set. Run Settings first.")
            return False
    return True


def _scanWorkingDir(workingDir: str) -> list:
    results = []
    if not os.path.isdir(workingDir):
        return results
    for fname in os.listdir(workingDir):
        if fname.startswith(".") or fname in IGNORED_FILES:
            continue
        _, ext = os.path.splitext(fname)
        fullPath = os.path.join(workingDir, fname)
        if os.path.isfile(fullPath) and ext.lower() in PLUGIN_EXTENSIONS:
            results.append(fullPath)
        elif os.path.isdir(fullPath) and _isUnpackedElyx(fullPath):
            results.append(fullPath)
    return results


def _isUnpackedElyx(dirPath: str) -> bool:
    for name in ["refmap.yml", "refmap.yaml", "refmap.json", "refmap.py"]:
        if os.path.isfile(os.path.join(dirPath, name)):
            return True
    return False


def _readAllMeta(paths: list, stateKeywords: list) -> tuple:
    successes = []
    failures = []
    for path in paths:
        if os.path.isdir(path):
            result = pluginReader.readPluginFromDir(path, stateKeywords)
        else:
            result = pluginReader.readPlugin(path, stateKeywords)
        if result.error:
            failures.append((path, result.error))
        else:
            successes.append(result)
    return successes, failures


def _buildEntry(meta, cfg: dict, about) -> dict:
    fileName = os.path.basename(meta.filePath)
    entry = configManager.buildEntry(meta, cfg["raw_dir_url"], fileName, cfg)
    if cfg.get("add_about") and about is not None:
        entry["about"] = about
        entry = configManager._sortFields(entry)
    return entry


def _buildAbout(meta, cfg: dict):
    if not cfg.get("add_about"):
        return None
    if meta.description:
        return translator.buildAbout(meta.description)
    return None


def opScanApply(cfg: dict) -> None:
    configPath = cfg["config_path"]
    workingDir = cfg["working_dir"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} cannot load config: {e}")
        return

    paths = _scanWorkingDir(workingDir)
    if not paths:
        _print(f"{C_GRAY}[info]{C_RESET} no plugin files found in working directory")
        return

    _print(f"{C_CYAN}[scan]{C_RESET} found {C_BOLD}{len(paths)}{C_RESET} file(s)")
    successes, failures = _readAllMeta(paths, cfg.get("state_keywords", []))

    if failures:
        _print(f"\n{C_YELLOW}[warn]{C_RESET} {len(failures)} file(s) had errors:")
        for path, err in failures:
            _print(f"  {C_GRAY}{os.path.basename(path)}{C_RESET}: {err}")

    if not successes:
        _print(f"{C_GRAY}[info]{C_RESET} nothing to process")
        return

    plugins = data["plugins"]
    added = []
    updated = []
    skipped = 0

    for result in successes:
        meta = result.meta
        idx, existing = configManager.findPlugin(plugins, meta.id)

        if existing is None:
            about = _buildAbout(meta, cfg)
            entry = _buildEntry(meta, cfg, about)
            plugins.append(entry)
            added.append({"name": meta.name, "id": meta.id, "version": meta.version,
                          "state": meta.state, "author": meta.author})
            _print(f"  {C_GREEN}[+]{C_RESET} {meta.name} {C_GRAY}({meta.id}){C_RESET} v{C_CYAN}{meta.version}{C_RESET}")
            continue

        if cfg.get("add_hash") and existing.get("hash") == meta.fileHash:
            skipped += 1
            continue

        cmp = compareVersions(meta.version, existing.get("version", "0"))
        prevVersion = existing.get("version", "?")

        if cmp < 0:
            if not cfg.get("allow_downgrade"):
                _print(f"  {C_YELLOW}[warn]{C_RESET} downgrade detected: {meta.name} {C_GRAY}{prevVersion} -> {meta.version}{C_RESET}")
                if not _confirm("    Proceed with downgrade?", default=False):
                    skipped += 1
                    continue
            else:
                _print(f"  {C_YELLOW}[warn]{C_RESET} downgrade: {meta.name} {C_GRAY}{prevVersion} -> {meta.version}{C_RESET}")
        elif cmp == 0:
            if not _confirm(f"  {meta.name}: same version ({meta.version}), different hash. Update?", default=True):
                skipped += 1
                continue

        about = _buildAbout(meta, cfg)
        entry = _buildEntry(meta, cfg, about)
        plugins[idx] = entry
        updated.append({"name": meta.name, "id": meta.id, "version": meta.version,
                        "state": meta.state, "author": meta.author, "prevVersion": prevVersion})
        _print(f"  {C_BLUE}[->]{C_RESET} {meta.name} {C_GRAY}({meta.id}){C_RESET} v{C_GRAY}{prevVersion}{C_RESET} -> v{C_CYAN}{meta.version}{C_RESET}")

    if not added and not updated:
        _print(f"{C_GRAY}[info]{C_RESET} nothing changed ({skipped} skipped)")
        return

    try:
        configManager.saveConfig(configPath, data)
    except OSError as e:
        _print(f"{C_RED}[error]{C_RESET} failed to save config: {e}")
        return

    total = len(plugins)
    _print(f"\n{C_GREEN}[done]{C_RESET} added: {C_GREEN}{len(added)}{C_RESET}, updated: {C_BLUE}{len(updated)}{C_RESET}, skipped: {C_GRAY}{skipped}{C_RESET}, total: {C_BOLD}{total}{C_RESET}")

    if cfg.get("write_log"):
        logPath = os.path.join(_SCRIPT_DIR, LOG_FILENAME)
        logWriter.writeLog(logPath, added, updated, [], total, cfg.get("append_to_log", False))
        _print(f"{C_MAGENTA}[log]{C_RESET} {logPath}")

    if cfg.get("create_forpost"):
        forpostPath = os.path.join(_SCRIPT_DIR, FORPOST_FILENAME)
        logWriter.writeForPost(forpostPath, added, updated, [], total)
        _print(f"{C_MAGENTA}[forpost]{C_RESET} {forpostPath}")


def opDirStatus(cfg: dict) -> None:
    configPath = cfg["config_path"]
    workingDir = cfg["working_dir"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} cannot load config: {e}")
        return

    paths = _scanWorkingDir(workingDir)
    _print(f"{C_CYAN}[scan]{C_RESET} found {C_BOLD}{len(paths)}{C_RESET} file(s) in working directory")
    successes, failures = _readAllMeta(paths, cfg.get("state_keywords", []))

    plugins = data["plugins"]
    seenIds = set()
    toAdd = []
    toUpdate = []
    toDowngrade = []
    unchanged = []

    for result in successes:
        meta = result.meta
        seenIds.add(meta.id)
        idx, existing = configManager.findPlugin(plugins, meta.id)
        if existing is None:
            toAdd.append(meta)
            continue
        if cfg.get("add_hash") and existing.get("hash") == meta.fileHash:
            unchanged.append(meta)
            continue
        cmp = compareVersions(meta.version, existing.get("version", "0"))
        if cmp > 0:
            toUpdate.append((meta, existing.get("version", "?")))
        elif cmp < 0:
            toDowngrade.append((meta, existing.get("version", "?")))
        else:
            unchanged.append(meta)

    missingIds = [p["id"] for p in plugins if p["id"] not in seenIds]

    _print(f"\n{C_BOLD}=== Directory Status ==={C_RESET}")
    if toAdd:
        _print(f"\n{C_GREEN}New plugins ({len(toAdd)}):{C_RESET}")
        for m in toAdd:
            _print(f"  {C_GREEN}[+]{C_RESET} {m.name} {C_GRAY}({m.id}){C_RESET} v{C_CYAN}{m.version}{C_RESET}")
    if toUpdate:
        _print(f"\n{C_BLUE}Updates ({len(toUpdate)}):{C_RESET}")
        for m, oldv in toUpdate:
            _print(f"  {C_BLUE}[->]{C_RESET} {m.name} {C_GRAY}({m.id}){C_RESET} v{C_GRAY}{oldv}{C_RESET} -> v{C_CYAN}{m.version}{C_RESET}")
    if toDowngrade:
        _print(f"\n{C_YELLOW}Downgrades ({len(toDowngrade)}):{C_RESET}")
        for m, oldv in toDowngrade:
            _print(f"  {C_YELLOW}[<-]{C_RESET} {m.name} {C_GRAY}({m.id}){C_RESET} v{C_GRAY}{oldv}{C_RESET} -> v{C_CYAN}{m.version}{C_RESET}")
    if unchanged:
        _print(f"\n{C_GRAY}Unchanged ({len(unchanged)}):{C_RESET}")
        for m in unchanged:
            _print(f"  {C_GRAY}[=]{C_RESET} {m.name} {C_GRAY}({m.id}){C_RESET} v{C_CYAN}{m.version}{C_RESET}")
    if missingIds:
        _print(f"\n{C_RED}Missing files (in config but not in dir) ({len(missingIds)}):{C_RESET}")
        for pid in missingIds:
            entry = next((p for p in plugins if p["id"] == pid), None)
            if entry:
                _print(f"  {C_RED}[-]{C_RESET} {entry.get('name', '?')} {C_GRAY}({pid}){C_RESET}")
    if failures:
        _print(f"\n{C_YELLOW}Errors ({len(failures)}):{C_RESET}")
        for path, err in failures:
            _print(f"  {C_GRAY}{os.path.basename(path)}{C_RESET}: {err}")


def opChangePlugin(cfg: dict) -> None:
    configPath = cfg["config_path"]
    workingDir = cfg["working_dir"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    fname = _ask("Plugin file name: ")
    if not fname:
        return

    fullPath = os.path.join(workingDir, fname)
    if not os.path.exists(fullPath):
        _print(f"{C_RED}[error]{C_RESET} file not found: {fullPath}")
        return

    if os.path.isdir(fullPath):
        result = pluginReader.readPluginFromDir(fullPath, cfg.get("state_keywords", []))
    else:
        result = pluginReader.readPlugin(fullPath, cfg.get("state_keywords", []))

    if result.error:
        _print(f"{C_RED}[error]{C_RESET} {result.error}")
        return

    meta = result.meta
    plugins = data["plugins"]
    idx, existing = configManager.findPlugin(plugins, meta.id)

    if existing is None:
        _print(f"{C_RED}[error]{C_RESET} plugin {meta.id} not found in config")
        return

    about = _buildAbout(meta, cfg)
    entry = _buildEntry(meta, cfg, about)
    plugins[idx] = entry

    try:
        configManager.saveConfig(configPath, data)
    except OSError as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    _print(f"{C_GREEN}[done]{C_RESET} updated {meta.name} to v{C_CYAN}{meta.version}{C_RESET}")


def opDeletePlugin(cfg: dict) -> None:
    configPath = cfg["config_path"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    pid = _ask("Plugin ID to delete: ")
    if not pid:
        return

    plugins = data["plugins"]
    idx, existing = configManager.findPlugin(plugins, pid)
    if existing is None:
        _print(f"{C_RED}[error]{C_RESET} plugin {pid} not found")
        return

    if not _confirm(f"Delete {existing.get('name', '?')} ({pid})?"):
        return

    del plugins[idx]
    configManager.saveConfig(configPath, data)
    _print(f"{C_GREEN}[done]{C_RESET} deleted {existing.get('name', '?')}")


def opClearMissing(cfg: dict) -> None:
    configPath = cfg["config_path"]
    workingDir = cfg["working_dir"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    paths = _scanWorkingDir(workingDir)
    successes, _ = _readAllMeta(paths, cfg.get("state_keywords", []))

    seenIds = {r.meta.id for r in successes}
    plugins = data["plugins"]
    missing = [p for p in plugins if p["id"] not in seenIds]

    if not missing:
        _print(f"{C_GRAY}[info]{C_RESET} no missing plugins")
        return

    _print(f"{C_YELLOW}Missing plugins ({len(missing)}):{C_RESET}")
    for p in missing:
        _print(f"  {p.get('name', '?')} {C_GRAY}({p['id']}){C_RESET}")

    if not _confirm("Remove all missing?"):
        return

    data["plugins"] = [p for p in plugins if p["id"] in seenIds]
    configManager.saveConfig(configPath, data)
    _print(f"{C_GREEN}[done]{C_RESET} removed {len(missing)} plugin(s)")


def opEditPlugin(cfg: dict) -> None:
    configPath = cfg["config_path"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    pid = _ask("Plugin ID: ")
    if not pid:
        return

    plugins = data["plugins"]
    idx, existing = configManager.findPlugin(plugins, pid)
    if existing is None:
        _print(f"{C_RED}[error]{C_RESET} plugin {pid} not found")
        return

    _print(f"\n{C_BOLD}Current fields:{C_RESET}")
    for key, val in existing.items():
        _print(f"  {C_CYAN}{key}{C_RESET}: {val}")

    _print(f"\n{C_GRAY}Enter new values (blank to keep current):{C_RESET}")

    fields = ["name", "author", "version", "state", "icon", "min_version", "suspicious", "link"]
    for key in fields:
        if key not in existing:
            continue
        current = existing[key]
        newVal = _ask(f"  {key} [{current}]: ")
        if newVal:
            existing[key] = newVal

    configManager.saveConfig(configPath, data)
    _print(f"\n{C_GREEN}[done]{C_RESET} updated {existing['name']}")


def opSortPlugins(cfg: dict) -> None:
    configPath = cfg["config_path"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    by = _ask("Sort by (name/id/version) [name]: ", "name")
    data["plugins"] = configManager.sortPlugins(data["plugins"], by)
    configManager.saveConfig(configPath, data)
    _print(f"{C_GREEN}[done]{C_RESET} sorted by '{by}'")


def opResetKey(cfg: dict) -> None:
    configPath = cfg["config_path"]

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    key = _ask("Field name to remove: ")
    if not key:
        return

    try:
        count = configManager.resetKey(data["plugins"], key)
    except ValueError as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    if count == 0:
        _print(f"{C_GRAY}[info]{C_RESET} field '{key}' not found in any plugin")
        return

    configManager.saveConfig(configPath, data)
    _print(f"{C_GREEN}[done]{C_RESET} removed '{key}' from {count} plugin(s)")


def opUnpackElyx(cfg: dict) -> None:
    workingDir = cfg.get("working_dir", "")
    srcPath = _ask("Path to .elyx file: ")
    if not srcPath:
        return

    destDir = _ask(f"Destination directory [{workingDir}]: ", workingDir)
    if not destDir:
        return

    success, msg = pluginReader.unpackElyx(srcPath, destDir)
    if success:
        _print(f"{C_GREEN}[done]{C_RESET} unpacked to: {msg}")
    else:
        _print(f"{C_RED}[error]{C_RESET} {msg}")


def opPackElyx(cfg: dict) -> None:
    workingDir = cfg.get("working_dir", "")
    srcDir = _ask("Directory to pack: ")
    if not srcDir:
        return

    baseName = os.path.basename(srcDir.rstrip("/"))
    destPath = _ask(f"Output .elyx path [{baseName}.elyx]: ", f"{baseName}.elyx")
    if not destPath.endswith(".elyx"):
        destPath += ".elyx"

    success, msg = pluginReader.packElyx(srcDir, destPath)
    if success:
        _print(f"{C_GREEN}[done]{C_RESET} packed to: {msg}")
    else:
        _print(f"{C_RED}[error]{C_RESET} {msg}")


def opClearLogs() -> None:
    for fname in [LOG_FILENAME, FORPOST_FILENAME]:
        path = os.path.join(_SCRIPT_DIR, fname)
        if os.path.isfile(path):
            os.remove(path)
            _print(f"{C_RED}[-]{C_RESET} deleted {fname}")
        else:
            _print(f"{C_GRAY}[skip]{C_RESET} {fname} not found")


def opReset(cfg: dict) -> None:
    configPath = cfg["config_path"]
    workingDir = cfg["working_dir"]

    if not _confirm("This will regenerate the entire config from files. Continue?"):
        return

    try:
        data = configManager.loadConfig(configPath)
    except (ValueError, FileNotFoundError) as e:
        _print(f"{C_RED}[error]{C_RESET} {e}")
        return

    paths = _scanWorkingDir(workingDir)
    successes, failures = _readAllMeta(paths, cfg.get("state_keywords", []))

    if failures:
        _print(f"{C_YELLOW}[warn]{C_RESET} {len(failures)} file(s) had errors (will be skipped):")
        for path, err in failures:
            _print(f"  {C_GRAY}{os.path.basename(path)}{C_RESET}: {err}")

    data["plugins"] = []
    for result in successes:
        meta = result.meta
        about = _buildAbout(meta, cfg)
        entry = _buildEntry(meta, cfg, about)
        data["plugins"].append(entry)
        _print(f"  {C_GREEN}[+]{C_RESET} {meta.name} {C_GRAY}({meta.id}){C_RESET} v{C_CYAN}{meta.version}{C_RESET}")

    configManager.saveConfig(configPath, data)
    _print(f"\n{C_GREEN}[done]{C_RESET} regenerated config with {C_BOLD}{len(data['plugins'])}{C_RESET} plugins")


def opSettings(cfg: dict, scriptDir: str) -> dict:
    _print(f"\n{C_BOLD}Settings{C_RESET} {C_GRAY}(press Enter to keep current value):{C_RESET}\n")

    fields = [
        ("config_path", "Path to plugins.json"),
        ("working_dir", "Working directory (plugin files)"),
        ("raw_dir_url", "Raw download URL base"),
    ]
    for key, label in fields:
        current = cfg.get(key, "")
        raw = _ask(f"  {C_CYAN}{label}{C_RESET} [{C_GRAY}{current}{C_RESET}]: ")
        if raw:
            if key in ("config_path", "working_dir"):
                cfg[key] = scriptCfg.resolveRelPath(raw, scriptDir)
            else:
                cfg[key] = raw

    boolFields = [
        ("add_hash", "Add hash"),
        ("add_min_version", "Add min_version"),
        ("add_about", "Add about (translation)"),
        ("add_description", "Add description"),
        ("write_log", "Write latest.log"),
        ("create_forpost", "Write forpost.txt"),
        ("append_to_log", "Append to log"),
        ("allow_downgrade", "Allow downgrade without confirmation"),
    ]
    for key, label in boolFields:
        current = cfg.get(key, False)
        currentStr = "Y" if current else "N"
        raw = _ask(f"  {C_CYAN}{label}{C_RESET} [{C_GRAY}{currentStr}{C_RESET}]: ").lower()
        if raw in ("y", "yes", "true", "1"):
            cfg[key] = True
        elif raw in ("n", "no", "false", "0"):
            cfg[key] = False

    scriptCfg.saveCfg(scriptDir, cfg)
    _print(f"\n{C_GREEN}[done]{C_RESET} settings saved")
    return cfg


def opFirstRun(scriptDir: str) -> dict:
    _print(f"{C_BOLD}=== First run setup ==={C_RESET}\n")
    cfg = scriptCfg.DEFAULTS.copy()

    _print(f"{C_GRAY}Enter absolute or relative paths (relative to scripts/ directory).{C_RESET}")
    configRaw = _ask(f"  {C_CYAN}Path to plugins.json{C_RESET}: ")
    cfg["config_path"] = scriptCfg.resolveRelPath(configRaw, scriptDir) if configRaw else ""

    workingRaw = _ask(f"  {C_CYAN}Working directory (plugin files){C_RESET}: ")
    cfg["working_dir"] = scriptCfg.resolveRelPath(workingRaw, scriptDir) if workingRaw else ""

    urlRaw = _ask(f"  {C_CYAN}Raw download URL base{C_RESET} [{C_GRAY}{cfg['raw_dir_url']}{C_RESET}]: ")
    if urlRaw:
        cfg["raw_dir_url"] = urlRaw

    scriptCfg.saveCfg(scriptDir, cfg)
    gitResult = scriptCfg.createGitignore(scriptDir)
    _print(f"{C_MAGENTA}[gitignore]{C_RESET} script_cfg.yml: {gitResult}")
    _print(f"\n{C_GREEN}[done]{C_RESET} configuration saved\n")
    return cfg


MENU = f"""
{C_BOLD}{C_CYAN}PackIt Repo Manager{C_RESET}
{C_GRAY}==================={C_RESET}
 {C_BOLD} 1.{C_RESET} {C_GREEN}Scan & Apply{C_RESET}
 {C_BOLD} 2.{C_RESET} {C_CYAN}Dir Status{C_RESET}
 {C_BOLD} 3.{C_RESET} Change Plugin
 {C_BOLD} 4.{C_RESET} {C_RED}Delete Plugin{C_RESET}
 {C_BOLD} 5.{C_RESET} {C_YELLOW}Clear Missing{C_RESET}
 {C_BOLD} 6.{C_RESET} Edit Plugin
 {C_BOLD} 7.{C_RESET} Sort Plugins
 {C_BOLD} 8.{C_RESET} Reset Key
 {C_BOLD} 9.{C_RESET} {C_MAGENTA}Unpack Elyx{C_RESET}
 {C_BOLD}10.{C_RESET} {C_MAGENTA}Pack Elyx{C_RESET}
 {C_BOLD}11.{C_RESET} {C_RED}Clear Logs{C_RESET}
 {C_BOLD}12.{C_RESET} {C_YELLOW}Reset (regen){C_RESET}
 {C_BOLD}13.{C_RESET} {C_BLUE}Settings{C_RESET}
 {C_BOLD} 0.{C_RESET} Exit
"""


def main() -> None:
    scriptDir = _SCRIPT_DIR

    try:
        import yaml
    except ImportError:
        print(f"{C_RED}[error]{C_RESET} pyyaml is required: pip install pyyaml")
        sys.exit(1)

    if not scriptCfg.cfgExists(scriptDir):
        cfg = opFirstRun(scriptDir)
    else:
        try:
            cfg = scriptCfg.loadCfg(scriptDir)
        except ValueError as e:
            print(f"{C_RED}[error]{C_RESET} cannot load script_cfg.yml: {e}")
            sys.exit(1)

    while True:
        _print(MENU)
        choice = _ask(f"{C_BOLD}Choice:{C_RESET} ")
        _print()

        try:
            if choice == "0":
                break
            elif choice == "1":
                if _requireCfg(cfg):
                    opScanApply(cfg)
            elif choice == "2":
                if _requireCfg(cfg):
                    opDirStatus(cfg)
            elif choice == "3":
                if _requireCfg(cfg):
                    opChangePlugin(cfg)
            elif choice == "4":
                if _requireCfg(cfg):
                    opDeletePlugin(cfg)
            elif choice == "5":
                if _requireCfg(cfg):
                    opClearMissing(cfg)
            elif choice == "6":
                if _requireCfg(cfg):
                    opEditPlugin(cfg)
            elif choice == "7":
                if _requireCfg(cfg):
                    opSortPlugins(cfg)
            elif choice == "8":
                if _requireCfg(cfg):
                    opResetKey(cfg)
            elif choice == "9":
                opUnpackElyx(cfg)
            elif choice == "10":
                opPackElyx(cfg)
            elif choice == "11":
                opClearLogs()
            elif choice == "12":
                if _requireCfg(cfg):
                    opReset(cfg)
            elif choice == "13":
                cfg = opSettings(cfg, scriptDir)
            else:
                _print(f"{C_RED}[error]{C_RESET} unknown option")
        except KeyboardInterrupt:
            _print(f"\n{C_YELLOW}[interrupted]{C_RESET}")


if __name__ == "__main__":
    main()
