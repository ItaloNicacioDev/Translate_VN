"""
compiler.py

Responsável por gerar os arquivos traduzidos.

Usa o sistema de tradução NATIVO do Ren'Py (bloco `translate <idioma>
strings:`) em vez de copiar e modificar os scripts originais.

Formato gerado (compatível com Ren'Py 6, 7 e 8):

    translate pt strings:

        old "Texto original"
        new "Texto traduzido"

        old "Outro texto"
        new "Outra tradução"

Cada arquivo de origem gera um único bloco `translate strings:`
contendo todos os pares old/new daquele arquivo. Isso é o formato
correto que o Ren'Py espera — múltiplos blocos com o mesmo idioma
no mesmo namespace causam conflito.

Os arquivos gerados vão para game/tl/<idioma>/ com o mesmo nome
do script original (sem sufixo extra), espelhando a estrutura que
o Ren'Py usa nativamente (ex: game/tl/English/script.rpy).
"""

from pathlib import Path
import re
import time

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
        traduzidos duplicados."""

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
        do Ren'Py com um único bloco por arquivo contendo todos
        os pares old/new.

        Os arquivos são nomeados igual ao original (sem sufixo
        __translatevn_) e vão para output_folder mantendo a
        estrutura de subpastas — o patcher os coloca em
        game/tl/<idioma>/ onde o Ren'Py os encontra."""

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

        # Set global compartilhado entre TODOS os arquivos gerados —
        # evita duplicatas cross-file que causam o erro:
        # 'A translation for "..." already exists at outro_arquivo.rpy'.
        global_seen: set[str] = set()

        generated = []

        for file, data in files.items():

            result = self._compile_file(
                file,
                data,
                output,
                source_base,
                language_code,
                global_seen
            )

            if result:
                generated.append(result)

        # Gera o arquivo que força o jogo a carregar no idioma
        # traduzido. Fica na raiz do output (vai para game/ direto,
        # não dentro de tl/).
        force_lang_file = self._generate_force_language_file(
            output, language_code
        )

        if force_lang_file:
            generated.append(force_lang_file)

        self.logger.info(
            f"{len(generated)} arquivos de tradução gerados."
        )

        return generated

    # -------------------------------------------------

    def _generate_force_language_file(
        self,
        output_folder: Path,
        language_code: str
    ):
        """Cria um script que ativa o idioma traduzido automaticamente
        na primeira vez que o jogo é iniciado depois do patch aplicado.

        Fica marcado com __translatevn_ no nome para o patcher
        reconhecê-lo e copiá-lo para a raiz do game/ (não para tl/).
        """

        flag_suffix = format(int(time.time()), "x")

        flag_name = (
            f"_translatevn_forced_{language_code}_{flag_suffix}"
        )

        lines = [
            "# Ativa automaticamente o idioma traduzido gerado pelo",
            "# Translate VN na primeira execução após aplicar este",
            "# patch especificamente (a flag muda a cada patch novo,",
            "# entao reaplicar uma traducao sempre forca o idioma de",
            "# novo, mesmo que uma versao anterior ja tenha sido",
            "# aplicada nesse mesmo jogo antes). Nao força novamente",
            "# depois (nao quebra menu de idiomas do proprio jogo,",
            "# se existir).",
            "",
            "init 999 python:",
            f"    if not getattr(persistent, {flag_name!r}, False):",
            f"        _preferences.language = {language_code!r}",
            f"        setattr(persistent, {flag_name!r}, True)",
            "",
        ]

        output_name = (
            f"zzz_force_language__translatevn_{language_code}.rpy"
        )

        destination = output_folder / output_name

        # Remove versoes antigas com outro codigo de idioma
        for old_file in output_folder.glob(
            "zzz_force_language__translatevn_*.rpy"
        ):
            if old_file != destination:
                old_file.unlink()

        destination.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        self.logger.info(
            f"{output_name} criado (ativa o idioma '{language_code}' "
            "automaticamente)."
        )

        return destination

    # -------------------------------------------------

    def _compile_file(
        self,
        source_file: str,
        dialogues: list,
        output_folder: Path,
        source_base: str = None,
        language_code: str = "pt",
        global_seen: set = None
    ):
        """Gera um único arquivo .rpy com um bloco translate strings:
        contendo todos os pares old/new do script de origem.

        O arquivo é nomeado igual ao original (sem sufixo __translatevn_)
        para que o Ren'Py o encontre corretamente em game/tl/<idioma>/."""

        if global_seen is None:
            global_seen = set()

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

        # Nome do arquivo igual ao original — o Ren'Py resolve
        # traduções pelo nome do arquivo dentro de tl/<idioma>/
        output_name = source.name

        destination = destination_folder / output_name

        # Monta os pares old/new, todos dentro de um único bloco
        pairs = []

        for dialogue in sorted(dialogues, key=lambda d: d.get("line", 0)):

            original = dialogue.get("original", "")
            translated = dialogue.get("translated", "")
            line_num = dialogue.get("line", "?")

            if not original or not translated:
                continue

            if original in global_seen:
                self.logger.info(
                    f"Duplicata ignorada (linha {line_num}): "
                    f"{original[:40]!r}"
                )
                continue

            global_seen.add(original)

            original_escaped = self._escape_renpy_string(original)
            translated_escaped = self._escape_renpy_string(translated)

            pairs.append(
                f"    # linha {line_num}\n"
                f'    old "{original_escaped}"\n'
                f'    new "{translated_escaped}"'
            )

        if not pairs:
            return None

        # Um único bloco translate strings: por arquivo
        lines = [
            "# Tradução gerada pelo Translate VN",
            f"# Arquivo de origem: {source.name}",
            "",
            f"translate {language_code} strings:",
            "",
        ]

        lines.append("\n\n".join(pairs))
        lines.append("")

        destination.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        self.logger.info(
            f"{output_name} criado "
            f"({len(pairs)} entradas únicas de {len(dialogues)} diálogos)."
        )

        return destination

    # -------------------------------------------------
    # Mantido para compatibilidade com chamadas externas.
    # -------------------------------------------------

    def compile_file(
        self,
        source_file: str,
        dialogues: list,
        output_folder: Path,
        source_base: str = None,
        language_code: str = "pt",
        global_seen: set = None
    ):
        return self._compile_file(
            source_file,
            dialogues,
            output_folder,
            source_base,
            language_code,
            global_seen
        )