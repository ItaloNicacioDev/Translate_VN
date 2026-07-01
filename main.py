"""
main.py

Translate VN
Versão de testes (CLI)
"""

import shutil
from pathlib import Path

from core.logger import Logger
from core.project_manager import ProjectManager

from engine.renpy.detector import RenPyDetector
from engine.renpy.extractor import RenPyExtractor
from engine.renpy.parser import RenPyParser
from engine.renpy.compiler import RenPyCompiler
from engine.renpy.patcher import RenPyPatcher

from core.translator import Translator


class TranslateVN:

    VERSION = "0.1.0"

    def __init__(self):

        self.logger = Logger()

        self.project_manager = ProjectManager()

        self.detector = RenPyDetector()

        self.extractor = RenPyExtractor()

        self.parser = RenPyParser()

        self.compiler = RenPyCompiler()

        self.patcher = RenPyPatcher()

        self.translator = Translator()

    # ===================================================

    def banner(self):

        print("=" * 50)
        print("Translate VN")
        print(f"Versão {self.VERSION}")
        print("=" * 50)

    # ===================================================

    def menu(self):

        while True:

            self.banner()

            print("1 - Novo Projeto")
            print("2 - Abrir Projeto")
            print("3 - Listar Projetos")
            print("4 - Idiomas")
            print("5 - Configurações")
            print("0 - Sair")

            option = input("\nEscolha: ")

            match option:

                case "1":
                    self.new_project()

                case "2":
                    self.open_project()

                case "3":
                    self.list_projects()

                case "4":
                    self.languages_menu()

                case "5":
                    self.settings_menu()

                case "0":
                    break

                case _:
                    print("Opção inválida.\n")

    # ===================================================

    def new_project(self):

        print("\n=== Novo Projeto ===\n")

        name = input("Nome do projeto: ")

        game_path = input("Caminho do jogo: ")

        if not Path(game_path).exists():

            print("\nPasta não encontrada.\n")

            return

        try:

            info = self.detector.detect(game_path)

        except Exception as error:

            print(f"\n{error}\n")

            return

        try:

            self.project_manager.create(
                name=name,
                engine=info["engine"],
                version=info["version"],
                game_path=game_path
            )

        except FileExistsError as error:

            print(f"\n{error}\n")

            return

        print("\nProjeto criado com sucesso.\n")

    # ===================================================

    def list_projects(self):

        print()

        projects = self.project_manager.list_projects()

        if not projects:

            print("Nenhum projeto encontrado.\n")

            return

        for index, project in enumerate(projects, start=1):

            print(
                f"{index}. "
                f"{project['name']} "
                f"({project['engine']})"
            )

        print()

    # ===================================================

    def open_project(self):

        print()

        projects = self.project_manager.list_projects()

        if not projects:

            print("Nenhum projeto encontrado.\n")

            return

        for index, project in enumerate(projects, start=1):

            print(f"{index} - {project['name']}")

        option = input("\nProjeto: ")

        try:

            project = projects[int(option) - 1]

        except (ValueError, IndexError):

            print("\nProjeto inválido.\n")

            return

        # O project.json não guarda o id do banco, então
        # resolvemos aqui e anexamos ao dicionário em memória
        # para o resto do menu não precisar buscar de novo.

        project_id = self.project_manager.get_id(project["name"])

        if project_id is None:

            print(
                "\nEste projeto não possui registro no banco de "
                "dados (foi criado por uma versão antiga?). "
                "Recrie o projeto.\n"
            )

            return

        project["id"] = project_id

        self.project_menu(project)

    # ===================================================

    def project_menu(self, project):

        while True:

            print("\n==============================")

            print(project["name"])

            print("==============================")

            print("1 - Detectar jogo")
            print("2 - Extrair arquivos")
            print("3 - Ler diálogos (indexar)")
            print("4 - Traduzir automaticamente")
            print("5 - Revisar / editar diálogos")
            print("6 - Gerar pacote de tradução")
            print("7 - Aplicar tradução")
            print("8 - Remover tradução aplicada")
            print("0 - Voltar")

            option = input("\nEscolha: ")

            try:

                match option:

                    case "1":
                        self._detect(project)

                    case "2":
                        self._extract(project)

                    case "3":
                        self._index(project)

                    case "4":
                        self._translate(project)

                    case "5":
                        self._review(project)

                    case "6":
                        self._generate_package(project)

                    case "7":
                        self._apply_translation(project)

                    case "8":
                        self._remove_translation(project)

                    case "0":
                        break

                    case _:
                        print("Opção inválida.")

            except Exception as error:

                self.logger.error(str(error))

                print(f"\nErro: {error}\n")

    # ===================================================
    # Passo 1 - Detectar
    # ===================================================

    def _detect(self, project):

        info = self.detector.detect(project["game_path"])

        print()
        print(f"Engine: {info['engine']}")
        print(f"Versão: {info['version']}")
        print(f"Scripts .rpy: {len(info['scripts'])}")
        print(f"Scripts compilados .rpyc: {len(info['compiled_scripts'])}")
        print(f"Arquivos .rpa: {len(info['archives'])}")

    # ===================================================
    # Passo 2 - Extrair
    # ===================================================

    def _extract(self, project):

        info = self.detector.detect(project["game_path"])

        if info["compiled_scripts"] and shutil.which("unrpyc") is None:

            print(
                "\nAviso: existem scripts .rpyc compilados, mas a "
                "ferramenta 'unrpyc' não foi encontrada no PATH. "
                "Eles não serão descompilados agora.\n"
            )

            info["compiled_scripts"] = []

        if info["archives"] and shutil.which("unrpa") is None:

            print(
                "\nAviso: existem arquivos .rpa, mas a ferramenta "
                "'unrpa' não foi encontrada no PATH. Eles não serão "
                "extraídos agora.\n"
            )

            info["archives"] = []

        temp_folder = self.project_manager.get_temp_folder(
            project["name"]
        )

        self.extractor.extract_all(info, str(temp_folder))

        print(f"\nArquivos extraídos para: {temp_folder}\n")

    # ===================================================
    # Passo 3 - Indexar (ler diálogos e salvar no banco)
    # ===================================================

    def _index(self, project):

        temp_folder = self.project_manager.get_temp_folder(
            project["name"]
        )

        dialogues = self.parser.parse_project(str(temp_folder))

        if not dialogues:

            print(
                "\nNenhum diálogo encontrado. Extraia os arquivos "
                "primeiro (opção 2).\n"
            )

            return

        saved = self.project_manager.save_dialogues(
            project["id"],
            dialogues
        )

        print(f"\n{len(saved)} diálogos indexados no banco de dados.\n")

    # ===================================================
    # Passo 4 - Traduzir automaticamente
    # ===================================================

    def _translate(self, project):

        dialogues = self.project_manager.load_dialogues(project["id"])

        pending = [d for d in dialogues if d["status"] == "pending"]

        if not pending:

            print(
                "\nNenhum diálogo pendente. Indexe os diálogos "
                "primeiro (opção 3).\n"
            )

            return

        target = project.get("language_translation", "pt_BR").split("_")[0]

        self.translator.set_target_language(target)

        texts = [d["original"] for d in pending]

        translated_texts = self.translator.translate_list(texts)

        for dialogue, translated in zip(pending, translated_texts):

            self.project_manager.update_dialogue_translation(
                dialogue["id"],
                translated,
                status="translated"
            )

        print(f"\n{len(pending)} diálogos traduzidos.\n")

    # ===================================================
    # Passo 5 - Revisar / editar diálogos individualmente
    # ===================================================

    def _review(self, project):

        while True:

            dialogues = self.project_manager.load_dialogues(project["id"])

            if not dialogues:

                print(
                    "\nNenhum diálogo indexado ainda (opção 3).\n"
                )

                return

            print()

            for dialogue in dialogues:

                print(
                    f"[{dialogue['id']}] ({dialogue['status']}) "
                    f"{dialogue['original']!r} -> "
                    f"{dialogue['translated']!r}"
                )

            print(
                "\nDigite o ID de um diálogo para editar, "
                "'r<ID>' para restaurar (ex: r12), "
                "'d<ID>' para excluir a tradução (ex: d12), "
                "ou 0 para voltar."
            )

            choice = input("\n> ").strip()

            if choice == "0":
                return

            if choice.lower().startswith("r"):

                self._restore_dialogue(choice[1:])
                continue

            if choice.lower().startswith("d"):

                self._delete_dialogue(choice[1:])
                continue

            if not choice.isdigit():

                print("\nEntrada inválida.\n")
                continue

            dialogue = self.project_manager.database.get_dialogue(
                int(choice)
            )

            if dialogue is None:

                print("\nDiálogo não encontrado.\n")
                continue

            print(f"\nOriginal: {dialogue['original']}")
            print(f"Tradução atual: {dialogue['translated']}")

            new_text = input("Nova tradução: ")

            self.project_manager.update_dialogue_translation(
                int(choice),
                new_text,
                status="reviewed"
            )

            print("\nAtualizado.\n")

    def _restore_dialogue(self, raw_id):

        if not raw_id.isdigit():

            print("\nID inválido.\n")
            return

        self.project_manager.restore_dialogue(int(raw_id))

        print("\nDiálogo restaurado ao original.\n")

    def _delete_dialogue(self, raw_id):

        if not raw_id.isdigit():

            print("\nID inválido.\n")
            return

        self.project_manager.delete_dialogue(int(raw_id))

        print("\nTradução da linha excluída.\n")

    # ===================================================
    # Passo 6 - Gerar pacote de tradução
    # ===================================================

    def _generate_package(self, project):

        dialogues = self.project_manager.load_dialogues(project["id"])

        translated = [d for d in dialogues if d["translated"]]

        if not translated:

            print(
                "\nNenhum diálogo traduzido para gerar o pacote. "
                "Traduza primeiro (opção 4 ou 5).\n"
            )

            return

        temp_folder = self.project_manager.get_temp_folder(
            project["name"]
        )

        exports_folder = self.project_manager.get_exports_folder(
            project["name"]
        )

        self.compiler.compile(
            translated,
            str(exports_folder),
            source_base=str(temp_folder)
        )

        print(f"\nPacote de tradução gerado em: {exports_folder}\n")

    # ===================================================
    # Passo 7 - Aplicar tradução no jogo
    # ===================================================

    def _apply_translation(self, project):

        exports_folder = self.project_manager.get_exports_folder(
            project["name"]
        )

        if not any(exports_folder.rglob("*")):

            print(
                "\nNenhum pacote gerado ainda. Use a opção 6 "
                "primeiro.\n"
            )

            return

        game_folder = Path(project["game_path"]) / "game"

        confirm = input(
            f"\nIsso vai copiar os arquivos traduzidos para dentro "
            f"de '{game_folder}', com backup automático antes. "
            f"Confirmar? (s/n): "
        )

        if confirm.lower() != "s":

            print("\nOperação cancelada.\n")
            return

        self.patcher.apply_patch(
            str(exports_folder),
            str(game_folder),
            create_backup=True
        )

        print("\nTradução aplicada com sucesso.\n")

    # ===================================================
    # Passo 8 - Remover tradução aplicada
    # ===================================================

    def _remove_translation(self, project):

        game_folder = Path(project["game_path"]) / "game"

        if not self.patcher.is_patched(str(game_folder)):

            print("\nEste jogo não possui tradução aplicada.\n")
            return

        confirm = input(
            "\nIsso vai remover os arquivos de tradução do jogo. "
            "Confirmar? (s/n): "
        )

        if confirm.lower() != "s":

            print("\nOperação cancelada.\n")
            return

        removed = self.patcher.remove_patch(str(game_folder))

        print(f"\n{removed} arquivos de tradução removidos.\n")

    # ===================================================
    # Idiomas (CRUD global)
    # ===================================================

    def languages_menu(self):

        while True:

            print("\n=== Idiomas ===")

            languages = self.project_manager.list_languages()

            default = self.project_manager.get_default_language()

            if not languages:

                print("Nenhum idioma cadastrado.")

            for language in languages:

                marker = " (padrão)" if language["code"] == default else ""

                print(
                    f"[{language['id']}] {language['name']} "
                    f"({language['code']}){marker}"
                )

            print(
                "\na - Adicionar   e<ID> - Editar   "
                "r<ID> - Remover   p<ID> - Definir como padrão   "
                "0 - Voltar"
            )

            choice = input("\n> ").strip()

            if choice == "0":
                return

            if choice == "a":

                code = input("Código do idioma (ex: pt, en): ").strip()
                name = input("Nome do idioma (ex: Português): ").strip()

                self.project_manager.add_language(code, name)
                continue

            if choice.lower().startswith("e") and choice[1:].isdigit():

                code = input("Novo código: ").strip()
                name = input("Novo nome: ").strip()

                self.project_manager.edit_language(
                    int(choice[1:]), code, name
                )
                continue

            if choice.lower().startswith("r") and choice[1:].isdigit():

                self.project_manager.remove_language(int(choice[1:]))
                continue

            if choice.lower().startswith("p") and choice[1:].isdigit():

                language = next(
                    (l for l in languages if l["id"] == int(choice[1:])),
                    None
                )

                if language is None:

                    print("\nIdioma não encontrado.\n")
                    continue

                self.project_manager.set_default_language(
                    language["code"]
                )
                continue

            print("\nOpção inválida.\n")

    # ===================================================
    # Configurações
    # ===================================================

    def settings_menu(self):

        config = self.project_manager.config

        editable_keys = [
            "language",
            "theme",
            "projects_folder",
            "auto_backup",
            "auto_save",
            "log_level"
        ]

        while True:

            print("\n=== Configurações ===\n")

            for index, key in enumerate(editable_keys, start=1):

                print(f"{index} - {key}: {config.get(key)}")

            print("0 - Voltar")

            option = input("\nEscolha o número para editar: ").strip()

            if option == "0":
                return

            if not option.isdigit() or not (1 <= int(option) <= len(editable_keys)):

                print("\nOpção inválida.\n")
                continue

            key = editable_keys[int(option) - 1]

            current = config.get(key)

            new_value = input(f"Novo valor para '{key}' (atual: {current}): ").strip()

            if isinstance(current, bool):

                new_value = new_value.lower() in ("1", "true", "s", "sim")

            config.set(key, new_value)

            print("\nSalvo.\n")

    # ===================================================


if __name__ == "__main__":

    app = TranslateVN()

    app.menu()
