"""
extractor.py

Responsável pela extração dos arquivos de jogos Ren'Py.
"""

from pathlib import Path
import shutil
import subprocess

from core.logger import Logger


class RenPyExtractor:

    def __init__(self):

        self.logger = Logger()

    def prepare_workspace(self, output_path: str):

        output = Path(output_path)

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        return output

    def copy_scripts(
        self,
        game_folder: str,
        output_path: str
    ):

        game_folder = Path(game_folder)
        output = self.prepare_workspace(output_path)

        copied = 0

        for file in game_folder.rglob("*.rpy"):

            destination = output / file.relative_to(game_folder)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(file, destination)

            copied += 1

        self.logger.info(
            f"{copied} scripts .rpy copiados."
        )

        return copied

    def extract_rpa(
        self,
        rpa_file: str,
        output_path: str,
        unrpa_path: str = "unrpa"
    ):

        rpa = Path(rpa_file)

        if not rpa.exists():

            raise FileNotFoundError(rpa)

        output = self.prepare_workspace(output_path)

        self.logger.info(
            f"Extraindo {rpa.name}"
        )

        subprocess.run(
            [
                unrpa_path,
                str(rpa)
            ],
            cwd=output,
            check=True
        )

        self.logger.info(
            "Extração concluída."
        )

    def decompile_rpyc(
        self,
        game_folder: str,
        unrpyc_path: str = "unrpyc"
    ):

        game_folder = Path(game_folder)

        self.logger.info(
            "Descompilando arquivos .rpyc..."
        )

        subprocess.run(
            [
                unrpyc_path,
                str(game_folder)
            ],
            check=True
        )

        self.logger.info(
            "Descompilação concluída."
        )

    def extract_all(
        self,
        game_info: dict,
        output_path: str
    ):

        output = self.prepare_workspace(output_path)

        # Copia scripts existentes
        self.copy_scripts(
            game_info["game_folder"],
            output
        )

        # Extrai todos os .rpa
        for archive in game_info["archives"]:

            self.extract_rpa(
                archive,
                output
            )

        # Descompila scripts
        if game_info["compiled_scripts"]:

            self.decompile_rpyc(
                game_info["game_folder"]
            )

        self.logger.info(
            "Processo de extração finalizado."
        )