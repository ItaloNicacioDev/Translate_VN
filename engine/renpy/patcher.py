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

        files_to_copy = [
            file for file in translated.rglob("*") if file.is_file()
        ]

        if create_backup:

            backup_folder = game / "translatevn_backups"

            # Só faz backup dos arquivos que já existem no jogo e
            # vão ser sobrescritos - não do jogo inteiro. A tradução
            # normalmente só adiciona arquivos novos (ex: script_pt.
            # rpy), então na maioria das vezes isso nem vai ter nada
            # pra fazer backup.
            files_that_would_be_overwritten = [
                (game / file.relative_to(translated))
                for file in files_to_copy
                if (game / file.relative_to(translated)).exists()
            ]

            self.backup.create_selective_backup(
                base_folder=str(game),
                files=files_that_would_be_overwritten,
                backup_folder=str(backup_folder)
            )

        copied = 0

        for file in files_to_copy:

            destination = game / file.relative_to(translated)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # Remove traduções antigas do mesmo arquivo de origem
            # que já estejam no jogo (ex: de uma compilação
            # anterior com outro código de idioma), pra não deixar
            # duplicadas junto com a nova (ex: "..._pt.rpy" e
            # "..._pt_pt.rpy" para o mesmo script).
            if "__translatevn_" in destination.stem:

                base_stem = destination.stem.split(
                    "__translatevn_"
                )[0]

                old_pattern = (
                    base_stem
                    + "__translatevn_*"
                    + destination.suffix
                )

                for old_file in destination.parent.glob(old_pattern):

                    if old_file != destination and old_file.is_file():

                        old_file.unlink()

                        self.logger.info(
                            f"Tradução antiga removida do jogo: "
                            f"{old_file.name}"
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

        for file in game.rglob("*__translatevn_*.rpy"):

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

        for file in game.rglob("*__translatevn_*.rpy"):

            return True

        return False