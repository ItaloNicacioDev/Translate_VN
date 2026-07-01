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