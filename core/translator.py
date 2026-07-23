"""
translator.py

Gerencia traduções utilizando o Google Tradutor, com paralelização
controlada e retentativa automática, pra viabilizar volumes grandes
(dezenas de milhares de linhas, comuns em Visual Novels) num tempo
razoável sem tomar bloqueio do serviço gratuito.
"""

import re
import time
import threading
import concurrent.futures

from deep_translator import (
    GoogleTranslator,
    MyMemoryTranslator,
    LibreTranslator,
    DeeplTranslator,
    MicrosoftTranslator,
    YandexTranslator,
)

from core.logger import Logger


class Translator:

    # Trechos que precisam ser preservados literalmente durante a
    # tradução, porque o serviço de tradução (Google Tradutor) pode
    # corrompê-los - especialmente aspas escapadas (\"), que às
    # vezes voltam incompletas (some o "\" de fechamento), gerando
    # um .rpy inválido ("end of line expected") na hora de compilar
    # o jogo. Também protege tags Ren'Py ({b}, {size=+2}...),
    # interpolações ([player_name]) e outras barras invertidas (\n,
    # \\), que sofrem do mesmo tipo de problema.
    _PROTECTED_PATTERN = re.compile(
        r'\\"'            # aspas escapadas: \"
        r'|\\n'            # quebra de linha escapada: \n
        r'|\\\\'           # barra invertida escapada: \\
        r'|\{[^{}]*\}'     # tags Ren'Py: {b}, {/b}, {size=+2}...
        r'|\[[^\[\]]*\]'   # interpolação Ren'Py: [player_name]
    )

    # Placeholder feito só de letras/números, sem espaços ou
    # pontuação, pra parecer uma "palavra desconhecida" pro tradutor
    # e assim ter mais chance de sair ilesa da tradução.
    _PLACEHOLDER_RE = re.compile(r'tvnph(\d+)end', re.IGNORECASE)

    @classmethod
    def _protect(cls, text: str):
        """Substitui trechos sensíveis por placeholders antes de
        mandar pro tradutor. Retorna (texto_protegido, lista de
        trechos originais, na ordem dos placeholders)."""

        protected = []

        def _replace(match):

            protected.append(match.group(0))

            return f"tvnph{len(protected) - 1}end"

        protected_text = cls._PROTECTED_PATTERN.sub(_replace, text)

        return protected_text, protected

    @classmethod
    def _restore(cls, text: str, protected: list) -> str:
        """Reverte os placeholders pros trechos originais, depois
        que o texto já voltou traduzido."""

        if not protected:
            return text

        def _replace(match):

            index = int(match.group(1))

            if 0 <= index < len(protected):
                return protected[index]

            return match.group(0)

        return cls._PLACEHOLDER_RE.sub(_replace, text)

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

    # ===================================================
    # Provedores de tradução disponíveis. O Google Tradutor
    # (gratuito, sem chave) bloqueia temporariamente depois de um
    # volume grande de requisições em pouco tempo (comum em VNs
    # com dezenas de milhares de falas) - esses provedores extras
    # servem tanto pra escolha manual quanto pra fallback
    # automático quando isso acontece.
    #
    # "requires_api_key": obrigatório ter uma chave configurada
    # pra esse provedor funcionar.
    # "fields": campos extras que esse provedor aceita (além de
    # source/target), usados tanto pela UI quanto pela validação.
    # ===================================================

    PROVIDERS = {
        "google": {
            "label": "Google Translate",
            "requires_api_key": False,
            "fields": [],
        },
        "mymemory": {
            "label": "MyMemory (gratuito, sem chave)",
            "requires_api_key": False,
            "fields": [],
        },
        "libre": {
            "label": "LibreTranslate",
            "requires_api_key": False,
            "fields": ["base_url", "api_key"],
        },
        "deepl": {
            "label": "DeepL",
            "requires_api_key": True,
            "fields": ["api_key"],
        },
        "microsoft": {
            "label": "Microsoft Translator",
            "requires_api_key": True,
            "fields": ["api_key"],
        },
        "yandex": {
            "label": "Yandex Translate",
            "requires_api_key": True,
            "fields": ["api_key"],
        },
    }

    # Ordem padrão de fallback automático quando um provedor
    # começa a dar erro de bloqueio/limite. Só entram aqui
    # provedores que funcionam sem chave configurada, pra não
    # travar o fallback esperando uma credencial que o usuário
    # nunca colocou.
    DEFAULT_FALLBACK_ORDER = ["google", "mymemory"]

    # Trechos de mensagem de erro que indicam bloqueio/limite
    # excedido (não um erro genérico de rede ou texto inválido),
    # usados pra decidir quando vale a pena trocar de provedor
    # automaticamente em vez de só tentar de novo com o mesmo.
    _BLOCK_INDICATORS = (
        "429",
        "too many requests",
        "blocked",
        "quota",
        "limit exceeded",
        "temporarily unavailable",
        "service unavailable",
    )

    def __init__(
        self,
        source_language="auto",
        target_language="pt",
        provider="google",
        provider_settings=None,
        fallback_enabled=True,
        fallback_order=None
    ):

        self.logger = Logger()

        self.source_language = source_language
        self.target_language = target_language

        if provider not in self.PROVIDERS:
            provider = "google"

        self.provider_id = provider

        # settings por provedor: {"deepl": {"api_key": "..."}, ...}
        self.provider_settings = provider_settings or {}

        self.fallback_enabled = fallback_enabled

        self.fallback_order = (
            [p for p in fallback_order if p in self.PROVIDERS]
            if fallback_order else
            list(self.DEFAULT_FALLBACK_ORDER)
        )

        # Protege a troca de provedor entre threads (translate_list
        # roda várias traduções em paralelo, mas só queremos trocar
        # de provedor uma vez quando o bloqueio é detectado, não
        # uma vez por thread que falhar ao mesmo tempo).
        self._provider_lock = threading.Lock()

    def set_provider(self, provider_id: str, settings: dict = None):
        """Troca o provedor de tradução ativo. `settings` (opcional)
        atualiza as credenciais/config desse provedor específico
        (ex: {"api_key": "..."})."""

        if provider_id not in self.PROVIDERS:

            raise ValueError(f"Provedor de tradução desconhecido: {provider_id}")

        self.provider_id = provider_id

        if settings is not None:
            self.provider_settings[provider_id] = settings

        self.logger.info(
            f"Provedor de tradução alterado para "
            f"'{self.PROVIDERS[provider_id]['label']}'"
        )

    def set_provider_settings(self, provider_id: str, settings: dict):

        if provider_id not in self.PROVIDERS:
            raise ValueError(f"Provedor de tradução desconhecido: {provider_id}")

        self.provider_settings[provider_id] = settings

    def set_fallback_enabled(self, enabled: bool):

        self.fallback_enabled = bool(enabled)

    def set_fallback_order(self, order: list):

        self.fallback_order = [p for p in order if p in self.PROVIDERS]

    def _build_provider_instance(self, provider_id: str):
        """Cria uma instância nova do provedor pedido. Sempre cria
        uma instância nova a cada chamada (não reaproveita), porque
        isso é chamado a partir de várias threads ao mesmo tempo e
        não é seguro compartilhar uma instância entre elas."""

        extra = self.provider_settings.get(provider_id, {}) or {}

        if provider_id == "google":

            return GoogleTranslator(
                source=self.source_language,
                target=self.target_language
            )

        if provider_id == "mymemory":

            return MyMemoryTranslator(
                source=self.source_language,
                target=self.target_language
            )

        if provider_id == "libre":

            return LibreTranslator(
                source=self.source_language,
                target=self.target_language,
                base_url=extra.get("base_url") or "https://libretranslate.de",
                api_key=extra.get("api_key") or None
            )

        if provider_id == "deepl":

            api_key = extra.get("api_key")

            if not api_key:
                raise ValueError(
                    "DeepL requer uma chave de API configurada em "
                    "Configurações > Provedores de tradução."
                )

            return DeeplTranslator(
                api_key=api_key,
                source=self.source_language,
                target=self.target_language,
                use_free_api=extra.get("use_free_api", True)
            )

        if provider_id == "microsoft":

            api_key = extra.get("api_key")

            if not api_key:
                raise ValueError(
                    "Microsoft Translator requer uma chave de API "
                    "configurada em Configurações > Provedores de "
                    "tradução."
                )

            return MicrosoftTranslator(
                api_key=api_key,
                source=self.source_language,
                target=self.target_language
            )

        if provider_id == "yandex":

            api_key = extra.get("api_key")

            if not api_key:
                raise ValueError(
                    "Yandex Translate requer uma chave de API "
                    "configurada em Configurações > Provedores de "
                    "tradução."
                )

            return YandexTranslator(
                source=self.source_language,
                target=self.target_language,
                api_key=api_key
            )

        raise ValueError(f"Provedor de tradução desconhecido: {provider_id}")

    def _looks_like_block(self, error_message: str) -> bool:

        lowered = error_message.lower()

        return any(
            indicator in lowered for indicator in self._BLOCK_INDICATORS
        )

    def _advance_to_fallback_provider(self, failed_provider_id: str):
        """Troca automaticamente pro próximo provedor da lista de
        fallback, quando o provedor atual parece ter bloqueado as
        requisições. Só troca uma vez (protegido por lock), mesmo
        que várias threads detectem o bloqueio ao mesmo tempo."""

        with self._provider_lock:

            if self.provider_id != failed_provider_id:
                # outra thread já trocou antes desta chegar aqui
                return

            try:
                current_index = self.fallback_order.index(failed_provider_id)
            except ValueError:
                current_index = -1

            for candidate in self.fallback_order[current_index + 1:]:

                meta = self.PROVIDERS[candidate]

                if meta["requires_api_key"] and not self.provider_settings.get(
                    candidate, {}
                ).get("api_key"):
                    # pula provedores que exigem chave e não tem
                    # uma configurada, senao so' trocaria pra outro
                    # provedor que tambem vai falhar de cara
                    continue

                self.provider_id = candidate

                self.logger.warning(
                    f"Provedor '{self.PROVIDERS[failed_provider_id]['label']}' "
                    "parece ter bloqueado as requisições (limite excedido). "
                    f"Trocando automaticamente para "
                    f"'{meta['label']}' pro restante da tradução."
                )

                return

            self.logger.warning(
                f"Provedor '{self.PROVIDERS[failed_provider_id]['label']}' "
                "bloqueado e não há outro provedor de fallback disponível "
                "configurado. Configure outro provedor em Configurações "
                "> Provedores de tradução, ou aguarde o limite resetar."
            )

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
        própria do provedor a cada chamada, porque isso é chamado
        a partir de várias threads ao mesmo tempo e não é seguro
        compartilhar uma instância entre elas."""

        if not text.strip():

            return text, True

        provider_id = self.provider_id

        try:

            protected_text, protected = self._protect(text)

            translator = self._build_provider_instance(provider_id)

            translated = translator.translate(protected_text)

            translated = self._restore(translated, protected)

            self.logger.debug(
                f"Traduzido: {text[:40]}"
            )

            return translated, True

        except Exception as error:

            message = str(error)

            self.logger.error(message)

            if self.fallback_enabled and self._looks_like_block(message):

                self._advance_to_fallback_provider(provider_id)

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

                try:

                    translated, ok = self.translate(texts[index])

                except Exception as error:

                    # Qualquer erro inesperado (ex: bug interno,
                    # provedor mal configurado) NUNCA deve derrubar
                    # a tradução inteira - só marca essa linha
                    # específica como falha, pra ser retentada nas
                    # próximas rodadas como qualquer outra falha
                    # normal de tradução.
                    self.logger.error(
                        f"Erro inesperado traduzindo linha: {error}"
                    )

                    return index, texts[index], False

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