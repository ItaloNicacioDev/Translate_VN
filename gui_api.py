"""
gui_api.py

Ponte entre a interface (ui/index.html, rodando dentro do
pywebview) e o codigo Python que ja existe e ja funciona
(core/, engine/). NENHUMA classe original foi alterada -- este
arquivo so' importa e orquestra, exatamente como o main.py (CLI)
ja fazia.

Cada metodo publico da classe Api fica acessivel no JavaScript
como `pywebview.api.nome_do_metodo(args)`, retornando uma Promise.
"""

import json
import logging
import threading

from core.logger import Logger
from core.project_manager import ProjectManager
from core.config_manager import ConfigManager

from engine.renpy.detector import RenPyDetector
from engine.renpy.extractor import RenPyExtractor
from engine.renpy.parser import RenPyParser
from engine.renpy.compiler import RenPyCompiler
from engine.renpy.patcher import RenPyPatcher

from core.translator import Translator


# ===========================================================
# Handler de logging que empurra cada linha logada (pelo
# Logger ja existente) para o painel de status da GUI, em
# tempo real, via window.evaluate_js. Isso e' so' um "espiao"
# anexado ao logger que ja existe -- core/logger.py continua
# 100% intocado.
# ===========================================================

class GuiLogHandler(logging.Handler):

    def __init__(self, get_window):

        super().__init__()

        self.get_window = get_window

    def emit(self, record):

        window = self.get_window()

        if window is None:
            return

        payload = json.dumps({
            "level": record.levelname.lower(),
            "message": record.getMessage()
        })

        try:
            window.evaluate_js(
                f"window.onBackendLog && window.onBackendLog({payload})"
            )
        except Exception:
            pass


def attach_gui_log_handler(get_window):
    """Anexa o handler acima ao logger 'TranslateVN' que o
    core/logger.py ja cria. So' precisa ser chamado uma vez."""

    logger = logging.getLogger("TranslateVN")

    handler = GuiLogHandler(get_window)

    handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(handler)


# ===========================================================
# Api exposta ao JavaScript
# ===========================================================

class Api:

    def __init__(self):

        self.logger = Logger()

        self.project_manager = ProjectManager()

        self.detector = RenPyDetector()
        self.extractor = RenPyExtractor()
        self.parser = RenPyParser()
        self.compiler = RenPyCompiler()
        self.patcher = RenPyPatcher()

        self.translator = Translator()

        # Guarda o projeto (com id resolvido) atualmente aberto na
        # tela de projeto, igual ao "project" que o main.py (CLI)
        # ia passando de metodo em metodo.
        self._current_project = None

    # -------------------------------------------------
    # Helper interno: sempre devolve {"ok": bool, ...}
    # pro JS nao precisar lidar com excecao/Promise-reject.
    # -------------------------------------------------

    def _wrap(self, fn, *args, **kwargs):

        try:

            data = fn(*args, **kwargs)

            return {"ok": True, "data": data}

        except Exception as error:

            self.logger.error(str(error))

            return {"ok": False, "error": str(error)}

    # ===================================================
    # Projetos
    # ===================================================

    def list_projects(self):

        return self._wrap(self.project_manager.list_projects)

    def new_project(self, name: str, game_path: str):

        def _create():

            info = self.detector.detect(game_path)

            self.project_manager.create(
                name=name,
                engine=info["engine"],
                version=info["version"],
                game_path=game_path,
                translation_language=self.project_manager.get_default_language()
            )

            return self.project_manager.open(name)

        return self._wrap(_create)

    def open_project(self, name: str):

        def _open():

            project = self.project_manager.open(name)

            project_id = self.project_manager.get_id(name)

            if project_id is None:
                raise RuntimeError(
                    "Este projeto nao possui registro no banco de "
                    "dados (foi criado por uma versao antiga?). "
                    "Recrie o projeto."
                )

            project["id"] = project_id

            self._current_project = project

            return project

        return self._wrap(_open)

    def delete_project(self, name: str):

        return self._wrap(self.project_manager.delete, name)

    # ===================================================
    # Fluxo do projeto (equivalente ao project_menu do CLI)
    # ===================================================

    def detect(self):

        def _detect():

            project = self._require_current_project()

            return self.detector.detect(project["game_path"])

        return self._wrap(_detect)

    def extract(self):

        def _extract():

            project = self._require_current_project()

            info = self.detector.detect(project["game_path"])

            temp_folder = self.project_manager.get_temp_folder(
                project["name"]
            )

            warnings = self.extractor.extract_all(info, str(temp_folder))

            return {"temp_folder": str(temp_folder), "warnings": warnings}

        return self._wrap(_extract)

    def index_dialogues(self):

        def _index():

            project = self._require_current_project()

            temp_folder = self.project_manager.get_temp_folder(
                project["name"]
            )

            dialogues = self.parser.parse_project(str(temp_folder))

            if not dialogues:
                raise RuntimeError(
                    "Nenhum dialogo encontrado. Extraia os arquivos "
                    "primeiro."
                )

            saved = self.project_manager.save_dialogues(
                project["id"],
                dialogues
            )

            return {"count": len(saved)}

        return self._wrap(_index)

    def translate(self):

        def _translate():

            project = self._require_current_project()

            dialogues = self.project_manager.load_dialogues(project["id"])

            pending = [d for d in dialogues if d["status"] == "pending"]

            if not pending:
                raise RuntimeError(
                    "Nenhum dialogo pendente. Indexe os dialogos primeiro."
                )

            target = project.get(
                "language_translation", "pt_BR"
            ).split("_")[0]

            self.translator.set_target_language(target)

            unique_texts = []
            text_to_indices = {}

            for index, dialogue in enumerate(pending):

                text = dialogue["original"]

                if text not in text_to_indices:
                    text_to_indices[text] = []
                    unique_texts.append(text)

                text_to_indices[text].append(index)

            results, interrupted = self.translator.translate_list(
                unique_texts
            )

            updates = []

            for text, (translated, ok) in zip(unique_texts, results):

                if not ok:
                    continue

                for pending_index in text_to_indices[text]:

                    dialogue = pending[pending_index]

                    updates.append(
                        (translated, "translated", dialogue["id"])
                    )

            if updates:

                self.project_manager.update_dialogues_translations_bulk(
                    updates
                )

            return {
                "translated": len(updates),
                "pending_remaining": len(pending) - len(updates),
                "interrupted": interrupted
            }

        return self._wrap(_translate)

    def list_dialogues(self, status: str = None):

        def _list():

            project = self._require_current_project()

            return self.project_manager.load_dialogues(
                project["id"],
                status=status
            )

        return self._wrap(_list)

    def dialogue_counts(self):

        def _counts():

            project = self._require_current_project()

            return self.project_manager.count_dialogues_by_status(
                project["id"]
            )

        return self._wrap(_counts)

    def update_dialogue(self, dialogue_id: int, translated: str):

        return self._wrap(
            self.project_manager.update_dialogue_translation,
            int(dialogue_id),
            translated,
            "reviewed"
        )

    def restore_dialogue(self, dialogue_id: int):

        return self._wrap(
            self.project_manager.restore_dialogue,
            int(dialogue_id)
        )

    def delete_dialogue_translation(self, dialogue_id: int):

        return self._wrap(
            self.project_manager.delete_dialogue,
            int(dialogue_id)
        )

    def generate_package(self):

        def _generate():

            project = self._require_current_project()

            dialogues = self.project_manager.load_dialogues(project["id"])

            translated = [d for d in dialogues if d["translated"]]

            if not translated:
                raise RuntimeError(
                    "Nenhum dialogo traduzido para gerar o pacote."
                )

            temp_folder = self.project_manager.get_temp_folder(
                project["name"]
            )

            exports_folder = self.project_manager.get_exports_folder(
                project["name"]
            )

            target = project.get(
                "language_translation", "pt_BR"
            ).split("_")[0]

            self.compiler.compile(
                translated,
                str(exports_folder),
                source_base=str(temp_folder),
                language_code=target
            )

            return {"exports_folder": str(exports_folder)}

        return self._wrap(_generate)

    def apply_translation(self, create_backup: bool = True):

        def _apply():

            project = self._require_current_project()

            from pathlib import Path

            exports_folder = self.project_manager.get_exports_folder(
                project["name"]
            )

            if not any(exports_folder.rglob("*")):
                raise RuntimeError(
                    "Nenhum pacote gerado ainda. Gere o pacote primeiro."
                )

            game_folder = Path(project["game_path"]) / "game"

            self.patcher.apply_patch(
                str(exports_folder),
                str(game_folder),
                create_backup=bool(create_backup)
            )

            return {"applied": True}

        return self._wrap(_apply)

    def remove_translation(self):

        def _remove():

            project = self._require_current_project()

            from pathlib import Path

            game_folder = Path(project["game_path"]) / "game"

            if not self.patcher.is_patched(str(game_folder)):
                raise RuntimeError(
                    "Este jogo nao possui traducao aplicada."
                )

            removed = self.patcher.remove_patch(str(game_folder))

            return {"removed": removed}

        return self._wrap(_remove)

    # ===================================================
    # Idiomas
    # ===================================================

    def list_languages(self):

        return self._wrap(self.project_manager.list_languages)

    def get_default_language(self):

        return self._wrap(self.project_manager.get_default_language)

    def add_language(self, code: str, name: str):

        return self._wrap(self.project_manager.add_language, code, name)

    def edit_language(self, language_id: int, code: str, name: str):

        return self._wrap(
            self.project_manager.edit_language,
            int(language_id),
            code,
            name
        )

    def remove_language(self, language_id: int):

        return self._wrap(
            self.project_manager.remove_language,
            int(language_id)
        )

    def set_default_language(self, code: str):

        return self._wrap(self.project_manager.set_default_language, code)

    # ===================================================
    # Configuracoes
    # ===================================================

    def get_settings(self):

        return self._wrap(lambda: self.project_manager.config.all())

    def save_settings(self, data: dict):

        return self._wrap(self.project_manager.config.update, data)

    # ===================================================
    # Utilitario: escolher pasta via dialogo nativo do SO
    # (evita usar <input type=file webkitdirectory>, que no
    # pywebview nao devolve caminho absoluto real do sistema)
    # ===================================================

    def pick_folder(self):

        import webview

        result = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG
        )

        if not result:
            return {"ok": True, "data": None}

        return {"ok": True, "data": result[0]}

    # ===================================================

    def _require_current_project(self):

        if self._current_project is None:
            raise RuntimeError("Nenhum projeto aberto.")

        return self._current_project