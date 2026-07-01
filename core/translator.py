"""
translator.py

Gerencia traduções utilizando o Google Tradutor.
"""

from deep_translator import GoogleTranslator

from core.logger import Logger


class Translator:

    def __init__(
        self,
        source_language: str = "auto",
        target_language: str = "pt"
    ):

        self.logger = Logger()

        self.source_language = source_language
        self.target_language = target_language

        # Cache das traduções
        self.cache: dict[str, str] = {}

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

        if text is None:
            return ""

        if not text.strip():
            return text

        # Procura no cache
        if text in self.cache:

            self.logger.debug(
                f"Cache: {text[:40]}"
            )

            return self.cache[text]

        try:

            translated = self.translator.translate(text)

            # Salva no cache
            self.cache[text] = translated

            self.logger.debug(
                f"Traduzido: {text[:40]}"
            )

            return translated

        except Exception as error:

            self.logger.error(str(error))

            return text

    def translate_list(self, texts: list[str]) -> list[str]:

        result: list[str] = []

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

    def clear_cache(self):

        self.cache.clear()

        self.logger.info(
            "Cache de traduções limpo."
        )

    def cache_size(self) -> int:

        return len(self.cache)

    def has_cache(self, text: str) -> bool:

        return text in self.cache

    def get_cache(self) -> dict:

        return self.cache.copy()