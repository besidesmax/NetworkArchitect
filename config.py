import sys
from pathlib import Path


def get_runtime_base_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


class Config:
    RUNTIME_BASE_DIR = get_runtime_base_path()

    RESOURCES_DIR = RUNTIME_BASE_DIR / "src" / "network_architect" / "resources"
    ICON_PATH = RESOURCES_DIR / "logo.png"

    HOME_DIR = Path.home()
    USER_DATA_DIR = HOME_DIR / "AppData" / "Local" / "NetworkArchitect"

    DATABASE_DIR = USER_DATA_DIR
    DATABASE_PATH = DATABASE_DIR / "user_DB.db"

    SEED_DATABASE_PATH = (RUNTIME_BASE_DIR
                          / "src"
                          / "network_architect"
                          / "models"
                          / "data"
                          / "seed_DB.db"
                          )
