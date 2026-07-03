"""
compiler.py

Responsável por gerar os arquivos traduzidos.
"""

from pathlib import Path
import re
import shutil

from core.logger import Logger


class RenPyCompiler:

    def __init__(self):

        self.logger = Logger()

    # -------------------------------------------------

    @staticmethod
    def normalize_language_code(language_code: str) -> str:
        """Reduz qualquer variação de código de idioma (pt_BR,
        pt-BR, PT_pt, pt-br...) só as letras iniciais em
        minúsculo (ex: "pt"). Isso evita que pequenas diferenças
        de formatação no código do idioma gerem arquivos
        traduzidos duplicados (ex: "..._pt.rpy" e
        "..._pt-BR.rpy" coexistindo para o mesmo arquivo)."""

        if not language_code:

            return "pt"

        match = re.match(r"[a-zA-Z]+", language_code)

        if not match:

            return "pt"

        return match.group(0).lower()

    # -------------------------------------------------

    def compile(
        self,
        dialogues: list,
        output_folder: str,
        source_base: str = None,
        language_code: str = "pt"
    ):

        output = Path(output_folder)

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        # Normaliza o código do idioma pra evitar que variações de
        # formatação (pt_BR, pt-BR, PT...) gerem arquivos
        # duplicados pro mesmo idioma.
        language_code = self.normalize_language_code(language_code)

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
                    source_base,
                    language_code
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
        source_base: str = None,
        language_code: str = "pt"
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

        # Sufixo propositalmente incomum (prefixo duplo "__") e com
        # o código do idioma, pra não colidir com um arquivo que o
        # próprio jogo já tenha (ex: uma tradução PT distribuída
        # pelo autor original chamada "capitulo1_pt.rpy" - um
        # sufixo genérico "_pt" bateria em cima disso).
        output_name = (
            source.stem
            + f"__translatevn_{language_code}"
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

        # Remove qualquer tradução antiga já gerada pra este mesmo
        # arquivo de origem (de execuções anteriores, possivelmente
        # com outro código de idioma) antes de escrever a nova.
        # Evita ficar com "capitulo1__translatevn_pt.rpy" e
        # "capitulo1__translatevn_pt_pt.rpy" duplicados lado a lado.
        old_pattern = (
            source.stem
            + "__translatevn_*"
            + source.suffix
        )

        for old_file in destination_folder.glob(old_pattern):

            if old_file != destination:

                old_file.unlink()

                self.logger.info(
                    f"Tradução antiga removida: {old_file.name}"
                )

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