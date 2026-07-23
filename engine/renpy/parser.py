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

            result = re.findall(
                r'"(.*?)"',
                line
            )

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

                    result = re.match(
                        r'"(.*?)"',
                        line[quote_index:]
                    )

                    if result:

                        candidate = result.group(1)

        if candidate is None:

            return None

        if self._looks_like_asset_or_identifier(candidate):

            return None

        return candidate

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