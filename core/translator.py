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

    @staticmethod
    def _format_duration(seconds: float) -> str:

        seconds = int(seconds)

        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h{minutes:02d}min"

        if minutes > 0:
            return f"{minutes}min{secs:02d}s"

        return f"{secs}s"

    def translate_list(self, texts: list[str]):
        """Traduz a lista inteira em paralelo (MAX_WORKERS por vez),
        retentando automaticamente o que falhar entre rodadas, com
        pausas crescentes. Retorna (results, interrompido):

        - results: lista de tuplas (texto_traduzido, sucesso), na
          mesma ordem/tamanho de `texts`. Itens não processados por
          causa de uma interrupção ficam como (texto_original, False).
        - interrompido: True se o usuário apertou Ctrl+C no meio do
          processo.

        Só sobra como sucesso=False o que falhar mesmo depois de
        todas as retentativas, ou o que não deu tempo de processar
        antes de uma interrupção."""

        total = len(texts)

        results = [None] * total
        pending_indices = list(range(total))

        round_number = 0

        # Usados pra calcular o tempo estimado restante: taxa real
        # de sucessos por segundo, medida desde o início (isso já
        # embute o tempo perdido com retentativas, então a estimativa
        # fica mais realista com o passar do tempo, não só otimista
        # baseada na primeira rodada).
        start_time = time.time()
        success_count = 0

        interrupted = False

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

            # Sem "with": controlamos o shutdown na mão, porque o
            # comportamento padrão do context manager é esperar TODAS
            # as tarefas enfileiradas terminarem antes de sair - e
            # aqui enfileiramos tudo de uma vez (só MAX_WORKERS rodam
            # por vez, o resto fica na fila). Sem isso, um Ctrl+C não
            # interrompe de verdade: ele fica preso esperando milhares
            # de tarefas que nem começaram ainda.
            executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.MAX_WORKERS
            )

            try:

                futures = [
                    executor.submit(process, index)
                    for index in pending_indices
                ]

                for future in concurrent.futures.as_completed(futures):

                    index, translated, ok = future.result()

                    results[index] = (translated, ok)

                    with lock:

                        completed += 1

                        if ok:
                            success_count += 1
                        else:
                            still_pending.append(index)

                        elapsed = time.time() - start_time

                        remaining_texts = total - success_count

                        if success_count >= 5 and elapsed > 1:

                            rate = success_count / elapsed

                            eta_seconds = remaining_texts / rate if rate > 0 else None

                            eta_text = (
                                f"faltam ~{self._format_duration(eta_seconds)}"
                                if eta_seconds is not None else
                                "calculando tempo restante..."
                            )

                        else:

                            eta_text = "calculando tempo restante..."

                        print(
                            f"[{success_count}/{total} traduzidos]"
                            + (
                                f" ({len(still_pending)} falharam nesta rodada)"
                                if still_pending else ""
                            )
                            + f" | {eta_text}    ",
                            end="\r"
                        )

                        if completed % self.BATCH_SIZE == 0 and completed != len(pending_indices):

                            self.logger.info(
                                f"Pausa de {self.BATCH_PAUSE_SECONDS}s "
                                f"a cada {self.BATCH_SIZE} linhas, pra "
                                "evitar bloqueio por uso excessivo..."
                            )

                            time.sleep(self.BATCH_PAUSE_SECONDS)

                executor.shutdown(wait=True)

                print()

            except KeyboardInterrupt:

                print()

                self.logger.warning(
                    "Interrompido pelo usuário. Cancelando tarefas "
                    "que ainda não começaram e aguardando as "
                    f"{self.MAX_WORKERS} em andamento terminarem "
                    "(alguns segundos)..."
                )

                # cancel_futures cancela imediatamente o que ainda
                # está na fila; só as poucas que já estavam
                # executando (no máximo MAX_WORKERS) terminam.
                executor.shutdown(wait=True, cancel_futures=True)

                interrupted = True

                break

            pending_indices = still_pending
            round_number += 1

            if interrupted:
                break

        # Qualquer índice que nunca chegou a ser processado (por
        # causa da interrupção) entra como "não traduzido", em vez
        # de None, pra quem chamar não precisar tratar esse caso
        # separadamente.
        for index in range(total):

            if results[index] is None:

                results[index] = (texts[index], False)

        total_elapsed = time.time() - start_time

        failures = sum(1 for r in results if not r[1])

        if interrupted:

            self.logger.warning(
                f"Tradução interrompida após {self._format_duration(total_elapsed)}. "
                f"{success_count} de {total} traduzidos e já podem ser salvos; "
                f"o restante fica pendente para uma próxima rodada."
            )

        elif failures:

            self.logger.warning(
                f"Tradução concluída em {self._format_duration(total_elapsed)} "
                f"com {failures} falha(s) persistente(s) de {total}, mesmo "
                f"após {self.MAX_RETRY_ROUNDS} retentativa(s). Essas linhas "
                "continuam como pendentes."
            )

        else:

            self.logger.info(
                f"Tradução concluída em {self._format_duration(total_elapsed)}, "
                "todas as linhas com sucesso."
            )

        return results, interrupted

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