"""
compiler.py

Responsável por gerar os arquivos traduzidos.

Usa o sistema de tradução NATIVO do Ren'Py (bloco `translate <idioma>
strings:`) em vez de copiar e modificar os scripts originais.

Por quê isso é importante:
  - A abordagem anterior (copiar o arquivo inteiro e fazer replace)
    era destrutiva: qualquer texto coincidente em `define`, `style`,
    `screen` ou `image` podia ser substituído acidentalmente,
    corrompendo definições de layout, personagens e UI do jogo.
  - O arquivo copiado incluía `style`, `define`, `screen` etc., e
    quando esses blocos eram ligeiramente alterados ou não carregados
    na ordem certa, causavam erros como "Unknown layout: legenda".
  - Com o bloco `translate`, o Ren'Py sobrepõe APENAS o texto dos
    diálogos — o restante do script original permanece intacto.

Formato gerado (compatível com Ren'Py 6, 7 e 8):

    # Arquivo: script.rpy  linha 42
    translate portuguese strings:
        old "Texto original"
        new "Texto traduzido"

    # Arquivo: outro.rpy  linha 17
    translate portuguese strings:
        old "Outro texto"
        new "Outra tradução"
"""

from pathlib import Path
import re

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

    @staticmethod
    def _escape_renpy_string(text: str) -> str:
        """Escapa aspas duplas e barras invertidas dentro de uma
        string Ren'Py para que o bloco translate seja válido."""

        # Barra invertida primeiro (evita duplo-escape)
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        return text

    # -------------------------------------------------

    def compile(
        self,
        dialogues: list,
        output_folder: str,
        source_base: str = None,
        language_code: str = "pt"
    ):
        """Gera um arquivo de tradução por script de origem,
        usando o formato `translate <idioma> strings:` nativo
        do Ren'Py. Apenas diálogos com tradução preenchida são
        incluídos."""

        output = Path(output_folder)

        output.mkdir(parents=True, exist_ok=True)

        language_code = self.normalize_language_code(language_code)

        # Agrupa os diálogos por arquivo de origem
        files: dict[str, list] = {}

        for dialogue in dialogues:

            if not dialogue.get("translated", "").strip():
                continue

            filename = dialogue["file"]

            files.setdefault(filename, []).append(dialogue)

        if not files:

            self.logger.info(
                "Nenhum diálogo traduzido para compilar."
            )

            return []

        generated = []

        for file, data in files.items():

            result = self._compile_file(
                file,
                data,
                output,
                source_base,
                language_code
            )

            if result:
                generated.append(result)

        self.logger.info(
            f"{len(generated)} arquivos de tradução gerados."
        )

        return generated

    # -------------------------------------------------

    def _compile_file(
        self,
        source_file: str,
        dialogues: list,
        output_folder: Path,
        source_base: str = None,
        language_code: str = "pt"
    ):
        """Gera um único arquivo .rpy com blocos translate para
        todos os diálogos traduzidos do script de origem."""

        source = Path(source_file)

        # Preserva estrutura de subpastas relativa à pasta temp
        if source_base is not None:

            try:
                relative_dir = source.relative_to(
                    Path(source_base)
                ).parent

            except ValueError:
                relative_dir = Path(".")

        else:
            relative_dir = Path(".")

        destination_folder = output_folder / relative_dir

        destination_folder.mkdir(parents=True, exist_ok=True)

        # Nome do arquivo de saída com sufixo incomum para não
        # colidir com arquivos que o jogo já possua.
        output_name = (
            source.stem
            + f"__translatevn_{language_code}"
            + source.suffix
        )

        destination = destination_folder / output_name

        # Remove traduções antigas do mesmo arquivo de origem
        # (de execuções anteriores com outro código de idioma).
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

        # Monta o conteúdo do arquivo de tradução
        lines = []

        lines.append(
            "# Tradução gerada pelo Translate VN"
        )
        lines.append(
            f"# Arquivo de origem: {source.name}"
        )
        lines.append("")

        # O Ren'Py exige que cada `old` seja único dentro do bloco
        # translate strings — se o mesmo texto aparece em várias
        # linhas do script, uma única entrada já cobre todas as
        # ocorrências. Duplicatas causam o erro:
        # 'A translation for "..." already exists'.
        seen_originals: set[str] = set()
        written = 0

        for dialogue in sorted(dialogues, key=lambda d: d.get("line", 0)):

            original = dialogue.get("original", "")
            translated = dialogue.get("translated", "")
            line_num = dialogue.get("line", "?")

            if not original or not translated:
                continue

            # Pula se esse texto original já foi incluído antes
            if original in seen_originals:
                self.logger.info(
                    f"Duplicata ignorada (linha {line_num}): "
                    f"{original[:40]!r}"
                )
                continue

            seen_originals.add(original)

            original_escaped = self._escape_renpy_string(original)
            translated_escaped = self._escape_renpy_string(translated)

            lines.append(
                f"# linha {line_num}"
            )
            lines.append(
                f"translate {language_code} strings:"
            )
            lines.append(
                f'    old "{original_escaped}"'
            )
            lines.append(
                f'    new "{translated_escaped}"'
            )
            lines.append("")

            written += 1

        if written == 0:
            # Só o cabeçalho, nenhuma tradução real — não gera
            # arquivo vazio.
            return None

        destination.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        self.logger.info(
            f"{output_name} criado "
            f"({written} entradas únicas de {len(dialogues)} diálogos)."
        )

        return destination

    # -------------------------------------------------
    # Mantido para compatibilidade com chamadas externas
    # que usavam compile_file diretamente.
    # -------------------------------------------------

    def compile_file(
        self,
        source_file: str,
        dialogues: list,
        output_folder: Path,
        source_base: str = None,
        language_code: str = "pt"
    ):
        return self._compile_file(
            source_file,
            dialogues,
            output_folder,
            source_base,
            language_code
        )