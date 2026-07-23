"""
patcher.py

Responsável por aplicar e remover traduções
em jogos Ren'Py.
"""

from pathlib import Path
import shutil
import re

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
        create_backup: bool = True,
        language_code: str = None
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

        # Detecta o código de idioma a partir do nome dos arquivos
        # gerados (ex: "script__translatevn_pt.rpy" → "pt"),
        # caso não seja passado explicitamente.
        if language_code is None:

            for file in files_to_copy:

                match = re.search(
                    r"__translatevn_([a-z]+)\.rpy$",
                    file.name
                )

                if match:
                    language_code = match.group(1)
                    break

        language_code = language_code or "pt"

        # O arquivo zzz_force_language vai para a raiz do game/
        # (precisa ser carregado antes de tudo, sem estar dentro
        # de tl/, para funcionar corretamente).
        # Os demais vão para game/tl/<idioma>/, mantendo a
        # estrutura de subpastas relativa à pasta translated.
        # Isso é obrigatório para o Ren'Py reconhecer os blocos
        # `translate <idioma> strings:` e aplicar a tradução.
        tl_folder = game / "tl" / language_code

        def _destination(file: Path) -> Path:

            if file.name.startswith("zzz_force_language"):
                return game / file.name

            return tl_folder / file.relative_to(translated)

        if create_backup:

            backup_folder = game / "translatevn_backups"

            files_that_would_be_overwritten = [
                _destination(file)
                for file in files_to_copy
                if _destination(file).exists()
            ]

            self.backup.create_selective_backup(
                base_folder=str(game),
                files=files_that_would_be_overwritten,
                backup_folder=str(backup_folder)
            )

        # Conjunto de destinos desta rodada — usado para não apagar
        # o que estamos prestes a colocar no lugar.
        destinations_this_run = {
            _destination(file) for file in files_to_copy
        }

        # Limpeza PROATIVA: remove arquivos de tradução antigos
        # tanto na raiz do game/ quanto dentro de tl/.
        removed_stale = 0

        for old_file in list(game.rglob("*__translatevn_*.rpy")):

            if old_file in destinations_this_run:
                continue

            old_file.unlink()

            removed_stale += 1

        if removed_stale:

            self.logger.info(
                f"{removed_stale} arquivo(s) de tradução antigos "
                "removidos do jogo antes de aplicar o novo patch."
            )

        copied = 0

        for file in files_to_copy:

            destination = _destination(file)

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