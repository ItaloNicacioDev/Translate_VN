"""
backup.py

Gerencia backups dos projetos e jogos.
"""

from pathlib import Path
from datetime import datetime
import zipfile
import shutil

from core.logger import Logger


class BackupManager:

    def __init__(self):

        self.logger = Logger()

    def create_backup(
        self,
        source_folder: str,
        backup_folder: str
    ) -> Path:

        source = Path(source_folder)

        backup_dir = Path(backup_folder)

        backup_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        backup_name = f"{source.name}_{timestamp}.zip"

        backup_path = backup_dir / backup_name

        self.logger.info(
            f"Criando backup: {backup_name}"
        )

        with zipfile.ZipFile(
            backup_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for file in source.rglob("*"):

                if file.is_file():

                    zipf.write(
                        file,
                        file.relative_to(source)
                    )

        self.logger.info(
            "Backup concluído."
        )

        return backup_path

    def create_selective_backup(
        self,
        base_folder: str,
        files: list,
        backup_folder: str
    ):
        """Faz backup só dos arquivos passados em `files` (caminhos
        dentro de base_folder), em vez da pasta inteira. Usado
        quando só um punhado de arquivos específicos está prestes a
        ser sobrescrito - evita compactar GBs de assets (imagens,
        áudio, vídeo) que nem vão ser tocados, o que em jogos
        grandes pode levar de minutos a mais de uma hora à toa,
        principalmente em HD.

        Se `files` estiver vazio, não cria backup nenhum (não há
        nada a proteger) e retorna None."""

        if not files:

            self.logger.info(
                "Nenhum arquivo será sobrescrito, backup não é "
                "necessário."
            )

            return None

        base = Path(base_folder)

        backup_dir = Path(backup_folder)

        backup_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        backup_name = f"{base.name}_{timestamp}.zip"

        backup_path = backup_dir / backup_name

        self.logger.info(
            f"Criando backup seletivo: {backup_name} "
            f"({len(files)} arquivo(s) que serão sobrescritos)"
        )

        with zipfile.ZipFile(
            backup_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for file in files:

                file = Path(file)

                if file.is_file():

                    zipf.write(
                        file,
                        file.relative_to(base)
                    )

        self.logger.info(
            "Backup concluído."
        )

        return backup_path

    def list_backups(
        self,
        backup_folder: str
    ):

        folder = Path(backup_folder)

        if not folder.exists():

            return []

        backups = sorted(
            folder.glob("*.zip"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        return backups

    def restore_backup(
        self,
        backup_file: str,
        destination_folder: str
    ):

        backup = Path(backup_file)

        destination = Path(destination_folder)

        if not backup.exists():

            raise FileNotFoundError(
                "Backup não encontrado."
            )

        if destination.exists():

            shutil.rmtree(destination)

        destination.mkdir(
            parents=True,
            exist_ok=True
        )

        self.logger.info(
            f"Restaurando {backup.name}"
        )

        with zipfile.ZipFile(
            backup,
            "r"
        ) as zipf:

            zipf.extractall(destination)

        self.logger.info(
            "Backup restaurado."
        )

    def delete_backup(
        self,
        backup_file: str
    ):

        backup = Path(backup_file)

        if backup.exists():

            backup.unlink()

            self.logger.warning(
                f"Backup removido: {backup.name}"
            )

    def clear_old_backups(
        self,
        backup_folder: str,
        keep: int = 10
    ):

        backups = self.list_backups(
            backup_folder
        )

        if len(backups) <= keep:

            return

        for backup in backups[keep:]:

            backup.unlink()

            self.logger.warning(
                f"Backup antigo removido: {backup.name}"
            )