"""
parser.py

Responsável por analisar scripts Ren'Py
e extrair diálogos traduzíveis.
"""

from pathlib import Path
import re

from core.logger import Logger


class RenPyParser:

    def __init__(self):

        self.logger = Logger()

        self.dialogues = []

    # ------------------------------

    def parse_project(self, project_path: str):

        self.dialogues.clear()

        project = Path(project_path)

        for file in project.rglob("*.rpy"):

            self.parse_file(file)

        self.logger.info(
            f"{len(self.dialogues)} diálogos encontrados."
        )

        return self.dialogues

    # ------------------------------

    def parse_file(self, file_path: Path):

        try:

            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception as error:

            self.logger.error(str(error))

            return

        lines = content.splitlines()

        for line_number, line in enumerate(lines, start=1):

            dialogue = self.extract_dialogue(line)

            if dialogue is None:
                continue

            self.dialogues.append({

                "file": str(file_path),

                "line": line_number,

                "original": dialogue,

                "translated": "",

                "status": "pending"

            })

    # ------------------------------

    def extract_dialogue(self, line: str):

        line = line.strip()

        if not line:

            return None

        if line.startswith("#"):
            return None

        # "Texto"

        if line.startswith('"'):

            result = re.findall(
                r'"(.*?)"',
                line
            )

            if result:

                return result[0]

        # e "Texto"

        result = re.search(

            r'^[a-zA-Z_][a-zA-Z0-9_]*\s+"(.*?)"$',

            line

        )

        if result:

            return result.group(1)

        return None

    # ------------------------------

    def get_dialogues(self):

        return self.dialogues

    # ------------------------------

    def count(self):

        return len(self.dialogues)

    # ------------------------------

    def clear(self):

        self.dialogues.clear()