"""
compiler.py

Responsável por gerar os arquivos traduzidos.
"""

from pathlib import Path
import shutil

from core.logger import Logger


class RenPyCompiler:

    def __init__(self):

        self.logger = Logger()

    # -------------------------------------------------

    def compile(
        self,
        dialogues: list,
        output_folder: str,
        source_base: str = None
    ):

        output = Path(output_folder)

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        files = {}

        # Agrupa os diálogos por arquivo
        for dialogue in dialogues:

            filename = dialogue["file"]

            files.setdefault(
                filename,
                []
            ).append(dialogue)

        generated = []

        for file, data in files.items():

            generated.append(
                self.compile_file(
                    file,
                    data,
                    output,
                    source_base
                )
            )

        self.logger.info(
            f"{len(generated)} arquivos gerados."
        )

        return generated

    # -------------------------------------------------

    def compile_file(
        self,
        source_file: str,
        dialogues: list,
        output_folder: Path,
        source_base: str = None
    ):

        source = Path(source_file)

        content = source.read_text(
            encoding="utf-8",
            errors="ignore"
        ).splitlines()

        for dialogue in dialogues:

            line = dialogue["line"] - 1

            original = dialogue["original"]

            translated = dialogue["translated"]

            if not translated:

                continue

            content[line] = content[line].replace(
                original,
                translated,
                1
            )

        output_name = (
            source.stem
            + "_pt"
            + source.suffix
        )

        # Preserva a estrutura de subpastas relativa à pasta
        # de origem (source_base). Sem isso, arquivos com o
        # mesmo nome em pastas diferentes se sobrescreviam e a
        # estrutura ficava incompatível com a pasta "game/"
        # original na hora de reaplicar a tradução.
        if source_base is not None:

            relative_dir = source.relative_to(
                Path(source_base)
            ).parent

        else:

            relative_dir = Path(".")

        destination_folder = output_folder / relative_dir

        destination_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        destination = destination_folder / output_name

        destination.write_text(

            "\n".join(content),

            encoding="utf-8"

        )

        self.logger.info(
            f"{output_name} criado."
        )

        return destination

    # -------------------------------------------------

    def copy_remaining_files(
        self,
        source_folder: str,
        output_folder: str
    ):

        source = Path(source_folder)

        output = Path(output_folder)

        copied = 0

        for file in source.rglob("*"):

            if not file.is_file():
                continue

            if file.suffix == ".rpy":
                continue

            destination = output / file.relative_to(source)

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
            f"{copied} arquivos auxiliares copiados."
        )