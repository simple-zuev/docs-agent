from pathlib import Path

import yaml

BASE = Path.home() / "AI" / "docs-agent"
CHANGE_LOG_ID = "1-6F5MCJR2EkP74pROsYXsPMmu1zPwp82hl0mDi9U3EQ"
CONFIG_PATH = BASE / "config" / "config.yml"


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def config_get(path, default=None):
    cfg = load_config()
    cur = cfg
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def is_readonly_mode():
    return config_get("safety.mode", "readonly") == "readonly"


def is_default_dry_run():
    return bool(config_get("safety.default_dry_run", True))


def ensure_write_allowed(operation_name: str, target: str = ""):
    if is_readonly_mode():
        suffix = f" Target: {target}" if target else ""
        raise RuntimeError(
            f"Write operation blocked in readonly mode: {operation_name}.{suffix}"
        )


def get_master_index_id():
    return config_get("documents.master_index_spreadsheet_id")


def get_master_index_sheet():
    return config_get("documents.master_index_sheet_name", "MASTER_INDEX")


def get_change_log_id():
    return config_get("documents.change_log_spreadsheet_id", CHANGE_LOG_ID)


def get_change_log_sheet():
    return config_get("documents.change_log_sheet_name", "Change Log Lite")


def get_default_test_folder_name():
    if bool(config_get("safety.office_as_default_test_folder", True)):
        return config_get("folders.office_name", "200_Офис")
    return config_get("folders.temp_name", "98_Временное")


def should_dry_run(dry_run: bool = False):
    return dry_run or is_default_dry_run()


def get_safety_mode():
    return config_get("safety.mode", "readonly")


def set_safety_mode_value(mode: str):
    if mode not in {"readonly", "write"}:
        raise RuntimeError(f"Unsupported safety mode: {mode}")

    cfg = load_config()
    if "safety" not in cfg or not isinstance(cfg["safety"], dict):
        cfg["safety"] = {}

    cfg["safety"]["mode"] = mode

    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)


def is_write_mode():
    return get_safety_mode() == "write"


def is_confirm_required():
    return bool(config_get("safety.require_confirm_for_write", True))


def ensure_confirmed(confirm: bool, operation_name: str):
    if is_write_mode() and is_confirm_required() and not confirm:
        raise RuntimeError(
            f"Write operation requires explicit confirmation in write mode: {operation_name}. "
            f"Run with --confirm after a dry-run preview."
        )
