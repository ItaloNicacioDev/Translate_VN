"""
translator.py

Gerencia traduções utilizando o Google Tradutor.
"""

from deep_translator import GoogleTranslator

from core.logger import Logger


class Translator:

    def __init__(
        self,
        source_language="auto",
        target_language="pt"
    ):

        self.logger = Logger()

        self.source_language = source_language
        self.target_language = target_language

        self.translator = GoogleTranslator(
            source=self.source_language,
            target=self.target_language
        )

    def set_source_language(self, language: str):

        self.source_language = language

        self.translator = GoogleTranslator(
            source=self.source_language,
            target=self.target_language
        )

        self.logger.info(
            f"Idioma de origem alterado para {language}"
        )

    def set_target_language(self, language: str):

        self.target_language = language

        self.translator = GoogleTranslator(
            source=self.source_language,
            target=self.target_language
        )

        self.logger.info(
            f"Idioma de destino alterado para {language}"
        )

    def translate(self, text: str) -> str:

        if not text.strip():

            return text

        try:

            translated = self.translator.translate(text)

            self.logger.debug(
                f"Traduzido: {text[:40]}"
            )

            return translated

        except Exception as error:

            self.logger.error(str(error))

            return text

    def translate_list(self, texts: list[str]):

        result = []

        total = len(texts)

        self.logger.info(
            f"Traduzindo {total} textos..."
        )

        for index, text in enumerate(texts, start=1):

            translated = self.translate(text)

            result.append(translated)

            print(
                f"[{index}/{total}]",
                end="\r"
            )

        print()

        self.logger.info(
            "Tradução concluída."
        )

        return result

    def detect_language(self, text: str):

        try:

            detector = GoogleTranslator(
                source="auto",
                target=self.target_language
            )

            detector.translate(text)

            return detector.source

        except Exception:

            return "unknown"