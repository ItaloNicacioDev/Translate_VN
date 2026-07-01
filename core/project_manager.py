"""
project_manager.py

Gerencia os projetos do Translate VN.
"""

from pathlib import Path
from datetime import datetime
import json

from core.database import Database
from core.logger import Logger
from core.config_manager import ConfigManager


class ProjectManager:

    def __init__(self):

        self.logger = Logger()
        self.config = ConfigManager()

        projects_folder = Path(
            self.config.get("projects_folder")
        )

        projects_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.projects_folder = projects_folder

        self.database = Database()

        self.database.initialize()

    def create(self,
               name: str,
               engine: str,
               version: str,
               game_path: str,
               original_language: str = "",
               translation_language: str = "pt_BR"):

        project_folder = self.projects_folder / name

        if project_folder.exists():

            raise FileExistsError(
                f"O projeto '{name}' já existe."
            )

        project_folder.mkdir()

        (project_folder / "backups").mkdir()

        (project_folder / "exports").mkdir()

        (project_folder / "temp").mkdir()

        created_at = datetime.now().isoformat()

        project_data = {

            "name": name,
            "engine": engine,
            "version": version,
            "game_path": game_path,
            "language_original": original_language,
            "language_translation": translation_language,
            "created_at": created_at

        }

        with open(
            project_folder / "project.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                project_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        self.database.execute(

            """
            INSERT INTO projects(

                name,
                engine,
                version,
                game_path,
                language_original,
                language_translation,
                created_at,
                updated_at

            )

            VALUES(?,?,?,?,?,?,?,?)

            """,

            (

                name,
                engine,
                version,
                game_path,
                original_language,
                translation_language,
                created_at,
                created_at

            )

        )

        self.logger.info(
            f"Projeto '{name}' criado."
        )

        return project_folder

    def open(self, name: str):

        project = self.projects_folder / name

        if not project.exists():

            raise FileNotFoundError(
                "Projeto não encontrado."
            )

        with open(
            project / "project.json",
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.logger.info(
            f"Projeto '{name}' aberto."
        )

        return data

    def list_projects(self):

        projects = []

        for folder in self.projects_folder.iterdir():

            if folder.is_dir():

                project_file = folder / "project.json"

                if project_file.exists():

                    with open(
                        project_file,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        projects.append(
                            json.load(file)
                        )

        return projects

    def delete(self, name: str):

        import shutil

        project = self.projects_folder / name

        if not project.exists():

            raise FileNotFoundError(
                "Projeto não encontrado."
            )

        shutil.rmtree(project)

        self.database.execute(

            "DELETE FROM projects WHERE name=?",

            (name,)

        )

        self.logger.warning(
            f"Projeto '{name}' removido."
        )

    def exists(self, name: str):

        return (
            self.projects_folder / name
        ).exists()

    def get_id(self, name: str):
        """Retorna o id do projeto no banco de dados (necessário para o CRUD de diálogos)."""

        return self.database.get_project_id(name)

    def get_folder(self, name: str) -> Path:

        return self.projects_folder / name

    def get_temp_folder(self, name: str) -> Path:

        folder = self.get_folder(name) / "temp"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def get_exports_folder(self, name: str) -> Path:

        folder = self.get_folder(name) / "exports"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def get_backups_folder(self, name: str) -> Path:

        folder = self.get_folder(name) / "backups"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    # ===================================================
    # CRUD de diálogos (wrappers do Database, para o resto
    # da aplicação não precisar acessar o banco diretamente)
    # ===================================================

    def save_dialogues(self, project_id: int, dialogues: list):
        """Substitui os diálogos do projeto pelos recém extraídos."""

        self.database.clear_dialogues(project_id)

        saved = []

        for dialogue in dialogues:

            dialogue_id = self.database.insert_dialogue(
                project_id=project_id,
                file_path=dialogue["file"],
                line=dialogue["line"],
                original=dialogue["original"],
                translated=dialogue.get("translated", ""),
                status=dialogue.get("status", "pending")
            )

            saved.append({
                "id": dialogue_id,
                "file": dialogue["file"],
                "line": dialogue["line"],
                "original": dialogue["original"],
                "translated": dialogue.get("translated", ""),
                "status": dialogue.get("status", "pending")
            })

        return saved

    def load_dialogues(self, project_id: int):

        rows = self.database.get_dialogues_by_project(project_id)

        dialogues = []

        for row in rows:

            file_path, _, line = row["character"].rpartition(":")

            dialogues.append({
                "id": row["id"],
                "file": file_path,
                "line": int(line) if line.isdigit() else 0,
                "original": row["original"],
                "translated": row["translated"] or "",
                "status": row["status"]
            })

        return dialogues

    def update_dialogue_translation(
        self,
        dialogue_id: int,
        translated: str,
        status: str = "translated"
    ):

        self.database.update_dialogue(dialogue_id, translated, status)

    def delete_dialogue(self, dialogue_id: int):

        self.database.delete_dialogue(dialogue_id)

    def get_dialogue(self, dialogue_id: int):

        row = self.database.get_dialogue(dialogue_id)

        if row is None:
            return None

        file_path, _, line = row["character"].rpartition(":")

        return {
            "id": row["id"],
            "file": file_path,
            "line": int(line) if line.isdigit() else 0,
            "original": row["original"],
            "translated": row["translated"] or "",
            "status": row["status"]
        }

    def restore_dialogue(self, dialogue_id: int):

        self.database.restore_dialogue(dialogue_id)

    # ===================================================
    # CRUD de idiomas
    # ===================================================

    def add_language(self, code: str, name: str):

        language_id = self.database.insert_language(code, name)

        self.logger.info(f"Idioma '{name}' ({code}) adicionado.")

        return language_id

    def list_languages(self):

        rows = self.database.get_languages()

        return [dict(row) for row in rows]

    def edit_language(self, language_id: int, code: str, name: str):

        self.database.update_language(language_id, code, name)

        self.logger.info(f"Idioma #{language_id} atualizado.")

    def remove_language(self, language_id: int):

        self.database.delete_language(language_id)

        self.logger.warning(f"Idioma #{language_id} removido.")

    def set_default_language(self, code: str):

        self.database.set_setting("default_language", code)

        self.logger.info(f"Idioma padrão definido: {code}")

    def get_default_language(self):

        return self.database.get_setting("default_language", "pt_BR")