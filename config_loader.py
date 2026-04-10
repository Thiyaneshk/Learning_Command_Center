from pathlib import Path
import yaml
from typing import Dict, List

CONFIG_PATH = Path("config.yaml")


def load_config() -> Dict:
    if not CONFIG_PATH.exists():
        return {
            "topics": [],
            "providers": [],
            "statuses": [],
            "difficulties": [],
        }

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_topics_from_config(cfg: Dict) -> List[str]:
    return cfg.get("topics", [])


def get_providers_from_config(cfg: Dict) -> List[str]:
    return cfg.get("providers", [])


def get_statuses_from_config(cfg: Dict) -> List[str]:
    return cfg.get("statuses", [])


def get_difficulties_from_config(cfg: Dict) -> List[str]:
    return cfg.get("difficulties", [])
