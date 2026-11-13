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

            # O usuário pode ter selecionado diretamente a pasta
            # 'game' (em vez da pasta raiz do jogo, que é a que
            # contém 'game' dentro). Nesse caso, `game_path/"game"`
            # nunca vai existir (seria .../game/game). Detectamos
            # esse caso: se o próprio caminho selecionado se chama
            # "game" e tem cara de pasta de jogo Ren'Py (contém
            # scripts .rpy/.rpyc ou o padrão de pasta "images"/
            # "audio"), usamos ele mesmo como game_folder e subimos
            # um nível para achar a pasta raiz.
            if game_path.name.lower() == "game" and (
                any(game_path.glob("*.rpy"))
                or any(game_path.glob("*.rpyc"))
                or any(game_path.rglob("*.rpy"))
                or any(game_path.rglob("*.rpyc"))
            ):

                game_folder = game_path
                game_path = game_path.parent

            else:

                raise FileNotFoundError(
                    "A pasta 'game' não foi encontrada. Selecione a "
                    "pasta RAIZ do jogo (a que contém a pasta "
                    "'game' dentro), não a pasta 'game' em si."
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

            "executables": [],

            # Idioma de ORIGEM detectado do jogo (ex: "en", "pt", "ja").

            # Vem de config.language em options.rpy/gui.rpy e serve de dica

            # pro tradutor (source_language) em vez de confiar só no "auto".

            "source_language": None,

            # Pastas de tradução já existentes em game/tl/ — indica se o jogo

            # já é multilíngue e quais idiomas já vem com tradução nativa.

            "tl_languages": []

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

        # Idioma de origem: lê config.language de options.rpy/gui.rpy, se existir.
        info["source_language"] = self.detect_source_language(game_folder)

        # Quais traduções nativas o jogo já traz em game/tl/.
        info["tl_languages"] = self.list_tl_languages(game_folder)

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

    def detect_source_language(self, game_folder: str | Path) -> str | None:
        """Tenta descobrir o idioma ORIGINAL do jogo lendo config.language
        de options.rpy e gui.rpy (padrão Ren'Py: config.language = "en").

        Retorna o código em minúsculas (ex: "en", "pt", "ja") ou None se não
        conseguir determinar.
        """

        game_folder = Path(game_folder)
        candidates = [
            game_folder / "options.rpy",
            game_folder / "gui.rpy",
        ]

        # Pega o valor entre aspas após config.language =
        lang_regex = re.compile(
            r'config\.language\s*=\s*["\']([a-zA-Z]{2}(?:_[A-Z]{2})?)[\"]\']',
            re.IGNORECASE,
        )

        for file in candidates:
            if not file.exists():
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
                match = lang_regex.search(text)
                if match:
                    return match.group(1).lower()
            except Exception:
                continue

        return None

    def list_tl_languages(self, game_folder: str | Path) -> list[str]:
        """Lista os códigos de idioma das pastas existentes em game/tl/.

        Ex: game/tl/English/, game/tl/Portugues/ -> ["english", "portugues"].
        """

        game_folder = Path(game_folder)
        tl_base = game_folder / "tl"

        if not tl_base.exists() or not tl_base.is_dir():
            return []

        languages = []
        for child in tl_base.iterdir():
            if child.is_dir():
                languages.append(child.name.lower())

        return sorted(languages)

    def is_renpy(self, game_path: str) -> bool:

        try:

            info = self.detect(game_path)

            return info["engine"] == self.NAME

        except Exception:

            return False