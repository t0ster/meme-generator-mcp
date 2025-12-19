import json
import os
import shutil
import sys
from functools import cache
from pathlib import Path

from app.types import MemeConfig

_dev_mode = False


def set_dev_mode(enabled: bool) -> None:
    global _dev_mode
    _dev_mode = enabled


def get_bundle_dir() -> Path:
    return Path(__file__).parent


def get_fallback_font_path() -> Path:
    return get_bundle_dir() / "fonts" / "Anton-Regular.ttf"


def get_config_dir() -> Path:
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Local" / "meme-generator-mcp"
    return Path.home() / ".config" / "meme-generator-mcp"


def get_templates_dir() -> Path:
    if _dev_mode:
        return get_bundle_dir() / "meme_templates"
    if templates_path := os.environ.get("MEME_GENERATOR_MCP_TEMPLATES_PATH"):
        return Path(templates_path)
    return get_config_dir() / "meme_templates"


def get_output_dir() -> Path:
    if output_path := os.environ.get("MEME_GENERATOR_MCP_OUTPUT_PATH"):
        return Path(output_path)
    return get_config_dir() / "generated_memes"


def init():
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    get_output_dir().mkdir(parents=True, exist_ok=True)

    if _dev_mode:
        return

    config_file = config_dir / "meme_configs.json"
    if not config_file.exists():
        bundle_config = get_bundle_dir() / "meme_configs.json"
        shutil.copy(bundle_config, config_file)

    templates_dir = config_dir / "meme_templates"
    if not templates_dir.exists():
        bundle_templates = get_bundle_dir() / "meme_templates"
        shutil.copytree(bundle_templates, templates_dir)


@cache
def get_meme_configs() -> dict[str, MemeConfig]:
    if _dev_mode:
        config_path = get_bundle_dir() / "meme_configs.json"
    elif config_path := os.environ.get("MEME_GENERATOR_MCP_CONFIGS_PATH"):
        config_path = Path(config_path)
    else:
        config_path = get_config_dir() / "meme_configs.json"
    with open(config_path) as f:
        raw = json.load(f)
    return {name: MemeConfig.model_validate(config) for name, config in raw.items()}
