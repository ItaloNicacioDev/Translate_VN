"""
config_manager.py

Gerencia todas as configurações da aplicação.
"""

from pathlib import Path
import json


class ConfigManager:

    DEFAULT_CONFIG = {
        "language": "pt_BR",
        "theme": "dark",
        "projects_folder": "projects",
        "backups_folder": "backups",
        "exports_folder": "exports",
        "temp_folder": "temp",
        "auto_backup": True,
        "auto_save": True,
        "log_level": "INFO"
    }

    def __init__(self, config_file: str = "config.json"):

        self.config_path = Path(config_file)

        if not self.config_path.exists():
            self.reset()

        self.load()

    def load(self):

        with open(self.config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)

        return self.config

    def save(self):

        with open(self.config_path, "w", encoding="utf-8") as file:
            json.dump(
                self.config,
                file,
                indent=4,
                ensure_ascii=False
            )

    def get(self, key, default=None):

        return self.config.get(key, default)

    def set(self, key, value):

        self.config[key] = value
        self.save()

    def update(self, data: dict):

        self.config.update(data)
        self.save()

    def reset(self):

        self.config = self.DEFAULT_CONFIG.copy()
        self.save()

    def all(self):

        return self.config