"""
Testes automatizados do RenPyParser.

Cobre: diálogos simples, com personagem, tags Ren'Py, interpolações,
aspas escapadas, barras invertidas, comandos não-diálogo, strings de UI,
extensões de asset, códigos de cor hex, identificadores únicos, blocos
old/new (próprio output do app), múltiplas strings, comentários e linhas
vazias.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.renpy.parser import RenPyParser


def parse_line(text: str):
    """Helper: parseia uma única linha e retorna o diálogo extraído ou None."""
    parser = RenPyParser()
    return parser.extract_dialogue(text)


class TestDialogueExtraction(unittest.TestCase):

    # ---------------------------------------------------------
    # Diálogos válidos
    # ---------------------------------------------------------

    def test_simple_quote(self):
        self.assertEqual(parse_line('"Hello world"'), "Hello world")

    def test_character_and_quote(self):
        # tag + atributos + fala: pega a ÚLTIMA string (a fala)
        self.assertEqual(
            parse_line('e happy "Hello world"'),
            "Hello world"
        )

    def test_multiple_attributes(self):
        self.assertEqual(
            parse_line('m surprised confused "O quê?!"'),
            "O quê?!"
        )

    def test_modifier_after_quote(self):
        self.assertEqual(
            parse_line('e "Olá!" with dissolve'),
            "Olá!"
        )

    def test_voice_modifier(self):
        self.assertEqual(
            parse_line('e "Olá!" (voice="v1.ogg")'),
            "Olá!"
        )

    def test_multiple_quoted_strings_takes_last(self):
        # "Nome" "Texto" -> retorna o Texto
        self.assertEqual(
            parse_line('"Eileen" "Bem-vindo!"'),
            "Bem-vindo!"
        )

    # ---------------------------------------------------------
    # Tags Ren'Py protegidas (não quebram o diálogo)
    # ---------------------------------------------------------

    def test_bold_tag(self):
        self.assertEqual(
            parse_line('e "{b}Negrito{/b}"'),
            "{b}Negrito{/b}"
        )

    def test_size_tag(self):
        self.assertEqual(
            parse_line('e "{size=+2}Grande{/size}"'),
            "{size=+2}Grande{/size}"
        )

    def test_mixed_tags(self):
        self.assertEqual(
            parse_line('e "{b}{i}Negrito e itálico{/i}{/b}"'),
            "{b}{i}Negrito e itálico{/i}{/b}"
        )

    # ---------------------------------------------------------
    # Interpolações Ren'Py
    # ---------------------------------------------------------

    def test_interpolation(self):
        self.assertEqual(
            parse_line('e "Olá, [player_name]!"'),
            "Olá, [player_name]!"
        )

    # ---------------------------------------------------------
    # Aspas escapadas (discurso direto dentro da fala)
    # ---------------------------------------------------------

    def test_escaped_quotes_inside_dialogue(self):
        # \"Sabes...\" deve ser preservado e não fechar a string
        line = r'p "\"Sabes que no viene ni un alma por aquí.\""'
        self.assertEqual(
            parse_line(line),
            '"Sabes que no viene ni un alma por aquí."'
        )

    # ---------------------------------------------------------
    # Barras invertidas escapadas
    # ---------------------------------------------------------

    def test_escaped_backslash(self):
        self.assertEqual(
            parse_line(r'e "Caminho:\\arquivo"'),
            "Caminho:\\arquivo"
        )

    def test_escaped_newline(self):
        self.assertEqual(
            parse_line(r'e "Linha1\nLinha2"'),
            "Linha1\nLinha2"
        )

    # ---------------------------------------------------------
    # Comandos não-diálogo (devem retornar None)
    # ---------------------------------------------------------

    NON_DIALOGUE = [
        'scene "bg forest"',
        'show eileen happy',
        'hide eileen',
        'image eileen happy = "eileen_happy.png"',
        'play music "bgm.ogg"',
        'queue music "intro.ogg"',
        'stop music',
        'define config.name = "Test"',
        'default mood = "happy"',
        'python:',
        'screen main_menu():',
        'style window:',
        'transform fade():',
        'window show',
        'with dissolve',
        'camera zoom',
        'layer master',
        'init python:',
        'label start:',
        'jump start',
        'call start',
        'return',
        'menu:',
        'if True:',
        'elif False:',
        'else:',
        'while x:',
        'for i in range(5):',
        'pause',
        'voice "v1.ogg"',
        'nvl',
        'add "image.png"',
        'use navigation',
        'translate english strings:',
        'config.language = "en"',
        'persistent.seen = True',
        'renpy.restart()',
        'define_music',
        'text "botão"',  # palavra-chave de UI isolada
    ]

    def test_non_dialogue_commands(self):
        for line in self.NON_DIALOGUE:
            with self.subTest(line=line):
                self.assertIsNone(
                    parse_line(line),
                    f"esperava None para: {line}"
                )

    # ---------------------------------------------------------
    # old / new (bloco de translate gerado pelo próprio app)
    # ---------------------------------------------------------

    def test_old_keyword_is_ignored(self):
        self.assertIsNone(parse_line('old "Texto original"'))

    def test_new_keyword_is_ignored(self):
        self.assertIsNone(parse_line('new "Texto traduzido"'))

    # ---------------------------------------------------------
    # Strings de UI (não são falas)
    # ---------------------------------------------------------

    def test_ui_keywords(self):
        for kw in ["window", "button", "frame", "label", "text", "image",
                   "slider", "menu", "screen", "help", "history"]:
            with self.subTest(kw=kw):
                self.assertIsNone(
                    parse_line(f'"{kw}"'),
                    f"esperava None para UI keyword: {kw}"
                )

    # ---------------------------------------------------------
    # Extensões de asset (caminhos de arquivo)
    # ---------------------------------------------------------

    def test_asset_extensions(self):
        for asset in [
            '"images/bg.png"',
            '"images/cg.jpg"',
            '"audio/bgm.ogg"',
            '"fonts/source.ttf"',
            '"video/intro.webm"',
            '"script.rpy"',
            '"data.json"',
        ]:
            with self.subTest(asset=asset):
                self.assertIsNone(
                    parse_line(asset),
                    f"esperava None para asset: {asset}"
                )

    def test_path_without_space_is_asset(self):
        self.assertIsNone(parse_line('"gallery_nav"'))

    # ---------------------------------------------------------
    # Códigos de cor hex
    # ---------------------------------------------------------

    def test_hex_colors(self):
        # Cores hex validas devem ser filtradas (nao sao dialogo)
        for color in ["#FFF", "#FF0000", "#AABBCC", "#12345678", "#abc"]:
            with self.subTest(color=color):
                self.assertIsNone(
                    parse_line(f'"{color}"'),
                    f"esperava None para cor hex: {color}"
                )
        # Cores com letras fora do conjunto hex (ex: R) nao batem no regex
        # e portanto nao sao filtradas como hex - isso e esperado.

    # ---------------------------------------------------------
    # Identificadores únicos (palavra única, sem espaço/pontuação)
    # ---------------------------------------------------------

    def test_single_identifier(self):
        """Identificadores com underline/hifen continuam filtrados (codigo).

        Palavras unicas SOLETRA (ex: "English" sozinho em menu de idioma)
        NAO sao mais filtradas automaticamente - e preferível ter um
        falso-positivo na revisao do que perder um dialogo real de uma
        palavra (ex: e "Hello"). O revisor pode excluir manualmente.
        """
        for ident in ["gallery_nav", "bg_forest-day"]:
            with self.subTest(ident=ident):
                self.assertIsNone(
                    parse_line(f'"{ident}"'),
                    f"esperava None para identificador: {ident}"
                )
        # Palavras unicas sem underline/hifen sao tratadas como dialogo
        for word in ["English", "Hello", "default"]:
            with self.subTest(word=word):
                self.assertEqual(
                    parse_line(f'"{word}"'),
                    word,
                    f"esperava '{word}' como dialogo, nao None"
                )


    # ---------------------------------------------------------
    # Comentários e linhas vazias
    # ---------------------------------------------------------

    def test_comment_line(self):
        self.assertIsNone(parse_line('# este é um comentário'))

    def test_empty_line(self):
        self.assertIsNone(parse_line(""))

    def test_whitespace_only_line(self):
        self.assertIsNone(parse_line("   "))

    # ---------------------------------------------------------
    # Aspas sem fechamento
    # ---------------------------------------------------------

    def test_unclosed_quote(self):
        self.assertIsNone(parse_line('e "texto sem fechamento'))


class TestParserProject(unittest.TestCase):

    def test_parse_project_skips_own_output(self):
        """Arquivos gerados pelo app (__translatevn_) não são reprocessados."""
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        (tmp / "script.rpy").write_text(
            'label start:\n    e "Hello"\n', encoding="utf-8"
        )
        (tmp / "script__translatevn_pt.rpy").write_text(
            'translate pt strings:\n    old "Hello"\n    new "Ola"\n',
            encoding="utf-8"
        )

        parser = RenPyParser()
        dialogues = parser.parse_project(str(tmp))

        self.assertEqual(len(dialogues), 1)
        self.assertEqual(dialogues[0]["original"], "Hello")


if __name__ == "__main__":
    unittest.main()
