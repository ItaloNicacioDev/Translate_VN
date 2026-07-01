"""
detector.py

Responsável por detectar jogos Ren'Py.
"""

from pathlib import Path
import re

from engine.base_engine import BaseEngine
from core.logger import Logger


class RenPyDetector(BaseEngine):

    NAME = "Ren'Py"

    def __init__(self):

        self.logger = Logger()

    def detect(self, game_path: str) -> dict:

        game_path = Path(game_path)

        if not game_path.exists():
            raise FileNotFoundError("Pasta do jogo não encontrada.")

        game_folder = game_path / "game"

        if not game_folder.exists():
            raise FileNotFoundError(
                "A pasta 'game' não foi encontrada."
            )

        info = {

            "engine": self.NAME,

            "root_path": str(game_path),

            "game_folder": str(game_folder),

            "version": self.get_version(game_path),

            "archives": [],

            "scripts": [],

            "compiled_scripts": [],

            "images": [],

            "audio": [],

            "fonts": [],

            "videos": [],

            "executables": []

        }

        # Arquivos da pasta game
        for file in game_folder.rglob("*"):

            if not file.is_file():
                continue

            suffix = file.suffix.lower()

            match suffix:

                case ".rpa":
                    info["archives"].append(str(file))

                case ".rpy":
                    info["scripts"].append(str(file))

                case ".rpyc":
                    info["compiled_scripts"].append(str(file))

                case ".png" | ".jpg" | ".jpeg" | ".webp":
                    info["images"].append(str(file))

                case ".ogg" | ".wav" | ".mp3" | ".opus":
                    info["audio"].append(str(file))

                case ".ttf" | ".otf":
                    info["fonts"].append(str(file))

                case ".webm" | ".mp4" | ".avi":
                    info["videos"].append(str(file))

        # Executáveis na raiz
        for exe in game_path.glob("*.exe"):

            info["executables"].append(str(exe))

        self.logger.info("Jogo Ren'Py detectado.")

        self.logger.info(
            f"{len(info['scripts'])} scripts encontrados."
        )

        self.logger.info(
            f"{len(info['compiled_scripts'])} scripts compilados."
        )

        self.logger.info(
            f"{len(info['archives'])} arquivos RPA encontrados."
        )

        return info

    def get_version(self, game_path: str) -> str:

        game_path = Path(game_path)

        candidates = [

            game_path / "renpy" / "__init__.py",

            game_path / "renpy" / "version.py",

            game_path / "renpy.py"

        ]

        version_regex = re.compile(
            r"(\d+\.\d+(?:\.\d+)?)"
        )

        for file in candidates:

            if not file.exists():
                continue

            try:

                text = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                match = version_regex.search(text)

                if match:

                    return match.group(1)

            except Exception:

                continue

        return "Desconhecida"

    def is_renpy(self, game_path: str) -> bool:

        try:

            info = self.detect(game_path)

            return info["engine"] == self.NAME

        except Exception:

            return False