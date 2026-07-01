"""
translator.py

Gerencia traduções utilizando o Google Tradutor, com paralelização
controlada e retentativa automática, pra viabilizar volumes grandes
(dezenas de milhares de linhas, comuns em Visual Novels) num tempo
razoável sem tomar bloqueio do serviço gratuito.
"""

import time
import threading
import concurrent.futures

from deep_translator import GoogleTranslator

from core.logger import Logger


class Translator:

    # Quantas traduções em paralelo. Mais rápido, mas também mais
    # chance de o serviço gratuito reclamar de uso excessivo - o
    # sistema de retentativa automática cobre isso quando acontece.
    MAX_WORKERS = 5

    # Pequeno espaçamento antes de cada requisição dentro de uma
    # mesma worker thread, pra suavizar picos.
    REQUEST_DELAY_SECONDS = 0.05

    # Pausa periódica a cada N traduções concluídas (somando todas
    # as threads), pra dar um respiro pro serviço.
    BATCH_SIZE = 300
    BATCH_PAUSE_SECONDS = 3

    # Retentativas automáticas com espera crescente entre rodadas.
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

    def set_source_language(self, language: str):

        self.source_language = language

        self.logger.info(
            f"Idioma de origem alterado para {language}"
        )

    def set_target_language(self, language: str):

        self.target_language = language

        self.logger.info(
            f"Idioma de destino alterado para {language}"
        )

    def translate(self, text: str) -> tuple[str, bool]:
        """Retorna (texto_traduzido, sucesso). Cria uma instância
        própria do GoogleTranslator a cada chamada, porque isso é
        chamado a partir de várias threads ao mesmo tempo e não é
        seguro compartilhar uma instância entre elas."""

        if not text.strip():

            return text, True

        try:

            translator = GoogleTranslator(
                source=self.source_language,
                target=self.target_language
            )

            translated = translator.translate(text)

            self.logger.debug(
                f"Traduzido: {text[:40]}"
            )

            return translated, True

        except Exception as error:

            self.logger.error(str(error))

            return text, False

    def translate_list(self, texts: list[str]):
        """Traduz a lista inteira em paralelo (MAX_WORKERS por vez),
        retentando automaticamente o que falhar entre rodadas, com
        pausas crescentes. Retorna lista de tuplas
        (texto_traduzido, sucesso), na mesma ordem/tamanho de
        `texts`. Só sobra como sucesso=False o que falhar mesmo
        depois de todas as retentativas."""

        total = len(texts)

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
                f"Traduzindo {len(pending_indices)} texto(s) "
                f"({self.MAX_WORKERS} em paralelo)..."
            )

            still_pending = []

            completed = 0
            lock = threading.Lock()

            def process(index):

                time.sleep(self.REQUEST_DELAY_SECONDS)

                translated, ok = self.translate(texts[index])

                return index, translated, ok

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.MAX_WORKERS
            ) as executor:

                futures = [
                    executor.submit(process, index)
                    for index in pending_indices
                ]

                for future in concurrent.futures.as_completed(futures):

                    index, translated, ok = future.result()

                    results[index] = (translated, ok)

                    with lock:

                        completed += 1

                        if not ok:
                            still_pending.append(index)

                        print(
                            f"[{completed}/{len(pending_indices)}]"
                            + (
                                f" ({len(still_pending)} falharam)"
                                if still_pending else ""
                            ),
                            end="\r"
                        )

                        if completed % self.BATCH_SIZE == 0 and completed != len(pending_indices):

                            self.logger.info(
                                f"Pausa de {self.BATCH_PAUSE_SECONDS}s "
                                f"a cada {self.BATCH_SIZE} linhas, pra "
                                "evitar bloqueio por uso excessivo..."
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