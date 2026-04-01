import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "bonus"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)  # type: ignore[no-any-return]


def save_config(config: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_token() -> str | None:
    return load_config().get("token")


def set_token(token: str) -> None:
    config = load_config()
    config["token"] = token
    save_config(config)


def get_card_id() -> str | None:
    return load_config().get("card_id")


def set_card_id(card_id: str) -> None:
    config = load_config()
    config["card_id"] = card_id
    save_config(config)


def get_store_id() -> str | None:
    return load_config().get("store_id")


def set_store_id(store_id: str) -> None:
    config = load_config()
    config["store_id"] = store_id
    save_config(config)


def clear_config() -> None:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
