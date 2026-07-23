"""
parser.py

Responsável por analisar scripts Ren'Py
e extrair diálogos traduzíveis.
"""

from pathlib import Path
import re

from core.logger import Logger


class RenPyParser:

    # Palavras que, no início da linha, indicam um comando Ren'Py
    # (não uma fala de personagem) mesmo que a linha tenha o formato
    # "identificador "texto"" - ex: scene "images/bg.png",
    # show "cg.png", image nome = "arquivo.png" (esse último nem
    # bate no regex por causa do "="), play music "trilha.ogg" etc.
    NON_DIALOGUE_KEYWORDS = {
        "scene", "show", "hide", "image", "play", "queue", "stop",
        "define", "default", "python", "screen", "style",
        "transform", "window", "with", "camera", "layer", "init",
        "label", "jump", "call", "return", "menu", "if", "elif",
        "else", "while", "for", "pause", "voice", "nvl", "add",
        "use", "translate", "config", "persistent", "renpy",
        "define_music", "text",
    }

    # Extensões de arquivo comuns em jogos Ren'Py - se o texto
    # "traduzível" termina com uma dessas, é quase certo que é um
    # caminho de asset (imagem, áudio, fonte), não diálogo.
    ASSET_EXTENSIONS = (
        ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif",
        ".ogg", ".mp3", ".wav", ".opus", ".ogv", ".webm", ".mp4",
        ".ttf", ".otf", ".woff", ".rpy", ".rpyc", ".rpym",
        ".rpymc", ".py", ".json", ".txt", ".csv",
    )

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

        first_word_match = re.match(
            r"^([a-zA-Z_][a-zA-Z0-9_]*)",
            line
        )

        if (
            first_word_match
            and first_word_match.group(1).lower() in self.NON_DIALOGUE_KEYWORDS
        ):

            return None

        candidate = None

        # "Texto"  OU  "Nome do Personagem" "Texto" (nesse segundo
        # caso queremos a ÚLTIMA string entre aspas, que é a fala -
        # a primeira é só o nome de exibição do personagem)

        if line.startswith('"'):

            result = self._find_all_quoted_strings(line)

            if result:

                candidate = result[-1]

        else:

            # tag "Texto"   (ex: e "Olá!")
            #
            # OBS: a tag quase sempre vem acompanhada de um ou mais
            # atributos de expressão/pose antes da fala (ex:
            # `e happy "Olá!"`, `m surprised confused "O quê?!"`),
            # e pode ter modificadores depois da fala (ex:
            # `e "Olá!" with dissolve`, `e "Olá!" (voice="v1.ogg")`).
            # Por isso não podemos exigir "tag + espaço + aspas" logo
            # no início nem "aspas" logo no fim da linha - só
            # validamos que tudo ANTES da primeira aspa é uma
            # sequência de identificadores (tag + atributos), sem
            # operadores como "=" (o que descartaria atribuições tipo
            # `mood = "happy"`).

            quote_index = line.find('"')

            if quote_index != -1:

                prefix = line[:quote_index].strip()

                if prefix and re.fullmatch(
                    r'[a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)*',
                    prefix
                ):

                    # Pegamos a PRIMEIRA aspa logo após a tag/atributos
                    # (a fala em si), não a última da linha - depois
                    # da fala pode vir `(voice="arquivo.ogg")` ou
                    # outro modificador com aspas próprias, e essas
                    # não são diálogo.

                    candidate = self._scan_quoted_string(
                        line,
                        quote_index
                    )

        if candidate is None:

            return None

        if self._looks_like_asset_or_identifier(candidate):

            return None

        return candidate

    # ------------------------------

    def _scan_quoted_string(self, line: str, start_index: int):
        """Lê a string entre aspas que começa em line[start_index]
        (que deve ser um caractere '"'), tratando `\\"` e `\\\\`
        como sequências de escape - ou seja, uma aspas escapada
        DENTRO da fala não fecha a string.

        Isso é essencial porque muitos jogos escrevem falas com
        aspas literais dentro do diálogo para indicar discurso
        direto, ex:

            p "\\"Sabes que no viene ni un alma por aquí.\\""

        Um regex simples como `"(.*?)"` fecha no primeiro `\\"`
        que encontra (interpretando a barra invertida como texto
        comum e a aspas seguinte como o fim da string), retornando
        só um caractere de barra invertida como "diálogo" - fazendo
        a fala inteira ser descartada da tradução.

        Retorna o conteúdo JÁ DESESCAPADO (`\\"` -> `"`,
        `\\\\` -> `\\`), que é o valor real que o Ren'Py usa em
        tempo de execução para essa string - o mesmo valor que
        `RenPyCompiler._escape_renpy_string` espera receber para
        regerar a linha `old "..."` idêntica ao original.
        """

        length = len(line)

        if start_index >= length or line[start_index] != '"':
            return None

        buffer = []
        i = start_index + 1

        while i < length:

            char = line[i]

            if char == "\\" and i + 1 < length and line[i + 1] in ('"', "\\"):

                # Escape válido: inclui o caractere escapado como
                # texto literal e pula os DOIS caracteres (barra +
                # caractere), sem fechar a string.
                buffer.append(line[i + 1])
                i += 2
                continue

            if char == '"':

                # Aspas de verdade, não escapada: fim da string.
                return "".join(buffer)

            buffer.append(char)
            i += 1

        # Nunca fechou - string malformada/incompleta na linha.
        return None

    # ------------------------------

    def _find_all_quoted_strings(self, line: str):
        """Encontra TODAS as strings entre aspas de nível superior
        na linha (sem entrar em recursão dentro de uma string já
        aberta), na ordem em que aparecem, já desescapadas.
        Usada para o caso `"Texto"` e `"Nome" "Texto"`, onde
        precisamos da ÚLTIMA string encontrada."""

        results = []

        length = len(line)
        i = 0

        while i < length:

            if line[i] == '"':

                content = self._scan_quoted_string(line, i)

                if content is None:
                    # Aspas sem fechamento correspondente: para de
                    # procurar, o resto da linha não é confiável.
                    break

                results.append(content)

                # Avança para depois da aspas de fechamento. Como
                # não guardamos o índice de fim em _scan_quoted_string,
                # recalculamos aqui percorrendo os mesmos caracteres.
                i = self._index_after_quoted_string(line, i)

            else:

                i += 1

        return results

    # ------------------------------

    def _index_after_quoted_string(self, line: str, start_index: int) -> int:
        """Retorna o índice logo após a aspas de fechamento da
        string que começa em start_index, considerando `\\"` e
        `\\\\` como escapes (mesma lógica de _scan_quoted_string,
        mas devolvendo a posição em vez do conteúdo)."""

        length = len(line)
        i = start_index + 1

        while i < length:

            char = line[i]

            if char == "\\" and i + 1 < length and line[i + 1] in ('"', "\\"):
                i += 2
                continue

            if char == '"':
                return i + 1

            i += 1

        return length

    # ------------------------------

    def _looks_like_asset_or_identifier(self, text: str) -> bool:
        """Heurística pra descartar coisas que batem no formato
        regex de diálogo mas não são fala de verdade: caminhos de
        arquivo de asset, tags de imagem, nomes de tela/transição
        etc."""

        stripped = text.strip()

        if not stripped:
            return True

        lowered = stripped.lower()

        if lowered.endswith(self.ASSET_EXTENSIONS):
            return True

        if "/" in stripped and " " not in stripped:
            return True

        # identificador tipo "gallery_nav", "bg_forest-day": só
        # letras/números/_/- e SEM espaço. Diálogo de verdade quase
        # sempre tem espaço, pontuação ou acento - um token cru com
        # underscore/hífen e nada mais é sinal forte de ser código,
        # não fala.
        if (
            ("_" in stripped or "-" in stripped)
            and " " not in stripped
            and re.fullmatch(r"[a-zA-Z0-9_\-]+", stripped)
        ):

            return True

        return False

    # ------------------------------

    def get_dialogues(self):

        return self.dialogues

    # ------------------------------

    def count(self):

        return len(self.dialogues)

    # ------------------------------

    def clear(self):

        self.dialogues.clear()