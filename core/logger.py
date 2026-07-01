"""
logger.py

Responsável pelo sistema de logs da aplicação.
"""

from pathlib import Path
from datetime import datetime
import logging


class Logger:

    def __init__(self, logs_dir: str = "logs"):

        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        log_name = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{log_name}.log"

        self.logger = logging.getLogger("TranslateVN")

        if not self.logger.handlers:

            self.logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s | %(message)s",
                datefmt="%H:%M:%S"
            )

            file_handler = logging.FileHandler(
                log_file,
                encoding="utf-8"
            )

            file_handler.setFormatter(formatter)

            console_handler = logging.StreamHandler()

            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def critical(self, message: str):
        self.logger.critical(message)