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
        incluídos.

        O Ren'Py trata o espaço de nomes `translate strings` como
        GLOBAL por idioma — uma mesma string `old` não pode aparecer
        em dois arquivos .rpy diferentes. Por isso o `seen_originals`
        é criado aqui e compartilhado entre todos os arquivos gerados
        nesta compilação."""

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
        # traduzido. Sem isso, o Ren'Py mantém o idioma original
        # (None) e os blocos "translate ... strings:" acima nunca
        # são exibidos, mesmo estando corretos e presentes no jogo.
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

        Importante:
          - Só força o idioma UMA vez (controlado por uma flag salva
            no persistent). Se o jogo tiver um menu de idiomas nativo
            e o jogador trocar depois, o patch não fica sobrescrevendo
            a escolha dele a cada início - não quebra esse menu.
          - Não altera screens, styles ou defines, então não interfere
            em nenhum outro menu do jogo.
          - init 999 roda bem tarde, depois que preferences/idiomas
            já foram registrados pelo jogo, garantindo que o idioma
            exista quando for aplicado.
        """

        flag_name = f"_translatevn_forced_{language_code}"

        lines = [
            "# Ativa automaticamente o idioma traduzido gerado pelo",
            "# Translate VN na primeira execução após aplicar o",
            "# patch. Não força novamente depois (nao quebra menu",
            "# de idiomas do proprio jogo, se existir).",
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
        """Gera um único arquivo .rpy com blocos translate para
        todos os diálogos traduzidos do script de origem.

        global_seen: set compartilhado entre todos os arquivos da
        compilação para deduplicar strings cross-file."""

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

        # Usa o set global passado pelo compile() para deduplicar
        # tanto dentro deste arquivo quanto entre arquivos diferentes.
        # Cada string `old` deve ser única em todo o jogo.
        written = 0

        for dialogue in sorted(dialogues, key=lambda d: d.get("line", 0)):

            original = dialogue.get("original", "")
            translated = dialogue.get("translated", "")
            line_num = dialogue.get("line", "?")

            if not original or not translated:
                continue

            # Pula se esse texto original já foi incluído antes
            # (neste arquivo ou em qualquer arquivo anterior)
            if original in global_seen:
                self.logger.info(
                    f"Duplicata ignorada (linha {line_num}): "
                    f"{original[:40]!r}"
                )
                continue

            global_seen.add(original)

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