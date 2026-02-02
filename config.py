from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent
    RESOURCES_DIR = BASE_DIR / "src" / "resources"
    ICON_PATH = RESOURCES_DIR / "logo.png"

    DATABASE_PATH = BASE_DIR / "src" / "models" / "data" / "network_architect.db"
