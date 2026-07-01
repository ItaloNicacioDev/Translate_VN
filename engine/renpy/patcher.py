"""
patcher.py

Responsável por aplicar e remover traduções
em jogos Ren'Py.
"""

from pathlib import Path
import shutil

from core.logger import Logger
from core.backup import BackupManager


class RenPyPatcher:

    def __init__(self):

        self.logger = Logger()

        self.backup = BackupManager()

    # -----------------------------------------------------

    def apply_patch(
        self,
        translated_folder: str,
        game_folder: str,
        create_backup: bool = True
    ):

        translated = Path(translated_folder)

        game = Path(game_folder)

        if not translated.exists():

            raise FileNotFoundError(
                "Pasta da tradução não encontrada."
            )

        if not game.exists():

            raise FileNotFoundError(
                "Pasta do jogo não encontrada."
            )

        if create_backup:

            backup_folder = game / "translatevn_backups"

            self.backup.create_backup(
                source_folder=str(game),
                backup_folder=str(backup_folder)
            )

        copied = 0

        for file in translated.rglob("*"):

            if not file.is_file():
                continue

            destination = game / file.relative_to(translated)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                file,
                destination
            )

            copied += 1

        self.logger.info(
            f"{copied} arquivos aplicados."
        )

        return copied

    # -----------------------------------------------------

    def remove_patch(
        self,
        game_folder: str
    ):

        game = Path(game_folder)

        removed = 0

        for file in game.rglob("*_pt.rpy"):

            file.unlink()

            removed += 1

        self.logger.info(
            f"{removed} arquivos removidos."
        )

        return removed

    # -----------------------------------------------------

    def restore_last_backup(
        self,
        game_folder: str
    ):

        backup_folder = (
            Path(game_folder)
            / "translatevn_backups"
        )

        backups = self.backup.list_backups(
            str(backup_folder)
        )

        if not backups:

            raise FileNotFoundError(
                "Nenhum backup encontrado."
            )

        latest = backups[0]

        self.backup.restore_backup(
            str(latest),
            game_folder
        )

        self.logger.info(
            "Backup restaurado."
        )

    # -----------------------------------------------------

    def is_patched(
        self,
        game_folder: str
    ) -> bool:

        game = Path(game_folder)

        for file in game.rglob("*_pt.rpy"):

            return True

        return False