import sys
from pathlib import Path


def get_runtime_base_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


class Config:
    BASE_DIR = get_runtime_base_path()

    RESOURCES_DIR = BASE_DIR / "src" / "network_architect" / "resources"
    ICON_PATH = RESOURCES_DIR / "logo.png"

    DATABASE_DIR = BASE_DIR / "src" / "network_architect" / "models" / "data"
    DATABASE_PATH = DATABASE_DIR / "network_architect.db"
