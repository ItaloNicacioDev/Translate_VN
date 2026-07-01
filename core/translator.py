"""
translator.py

Gerencia traduções utilizando o Google Tradutor.
"""

import time

from deep_translator import GoogleTranslator

from core.logger import Logger


class Translator:

    # Pausa entre cada requisição, pra não bater no limite de taxa
    # do endpoint gratuito do Google Tradutor.
    REQUEST_DELAY_SECONDS = 0.15

    # Depois de quantas requisições seguidas fazer uma pausa maior,
    # e por quanto tempo. Ajuda em lotes de milhares de linhas.
    BATCH_SIZE = 200
    BATCH_PAUSE_SECONDS = 5

    # Quantas vezes retentar automaticamente as linhas que falharem,
    # com espera crescente entre cada rodada de retentativas.
    MAX_RETRY_ROUNDS = 4
    RETRY_BACKOFF_SECONDS = [2, 5, 15, 30]

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

    def translate(self, text: str) -> tuple[str, bool]:
        """Retorna (texto_traduzido, sucesso). Em caso de falha,
        devolve o texto original com sucesso=False."""

        if not text.strip():

            return text, True

        try:

            translated = self.translator.translate(text)

            self.logger.debug(
                f"Traduzido: {text[:40]}"
            )

            return translated, True

        except Exception as error:

            self.logger.error(str(error))

            return text, False

    def translate_list(self, texts: list[str]):
        """Traduz a lista inteira, retentando automaticamente (com
        pausas crescentes) o que falhar, para minimizar a chance de
        sobrar linha pendente por causa de falha passageira de rede
        ou limite de taxa. Retorna lista de tuplas
        (texto_traduzido, sucesso), na mesma ordem/tamanho de
        `texts`.

        Só sobra como sucesso=False o que falhar mesmo depois de
        todas as retentativas."""

        total = len(texts)

        # Começa assumindo tudo pendente, na ordem original.
        results = [None] * total
        pending_indices = list(range(total))

        round_number = 0

        while pending_indices and round_number <= self.MAX_RETRY_ROUNDS:

            if round_number > 0:

                wait = self.RETRY_BACKOFF_SECONDS[
                    min(round_number - 1, len(self.RETRY_BACKOFF_SECONDS) - 1)
                ]

                self.logger.warning(
                    f"Retentando {len(pending_indices)} linha(s) que "
                    f"falharam (tentativa {round_number + 1}), "
                    f"aguardando {wait}s antes de continuar..."
                )

                time.sleep(wait)

            self.logger.info(
                f"Traduzindo {len(pending_indices)} texto(s)..."
                if round_number == 0 else
                f"Retentando {len(pending_indices)} texto(s)..."
            )

            still_pending = []

            for count, index in enumerate(pending_indices, start=1):

                translated, ok = self.translate(texts[index])

                results[index] = (translated, ok)

                if not ok:
                    still_pending.append(index)

                print(
                    f"[{count}/{len(pending_indices)}]"
                    + (f" ({len(still_pending)} falharam)" if still_pending else ""),
                    end="\r"
                )

                time.sleep(self.REQUEST_DELAY_SECONDS)

                if count % self.BATCH_SIZE == 0 and count != len(pending_indices):

                    self.logger.info(
                        f"Pausa de {self.BATCH_PAUSE_SECONDS}s a cada "
                        f"{self.BATCH_SIZE} linhas, pra evitar bloqueio "
                        "por uso excessivo..."
                    )

                    time.sleep(self.BATCH_PAUSE_SECONDS)

            print()

            pending_indices = still_pending
            round_number += 1

        failures = sum(1 for r in results if not r[1])

        if failures:

            self.logger.warning(
                f"Tradução concluída com {failures} falha(s) "
                f"persistente(s) de {total}, mesmo após "
                f"{self.MAX_RETRY_ROUNDS} retentativa(s). Essas "
                "linhas continuam como pendentes."
            )

        else:

            self.logger.info(
                "Tradução concluída, todas as linhas com sucesso."
            )

        return results

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