"""
main.py

Translate VN
Versão de testes (CLI)
"""

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

    VERSION = "0.2.3"

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

        temp_folder = self.project_manager.get_temp_folder(
            project["name"]
        )

        warnings = self.extractor.extract_all(info, str(temp_folder))

        for warning in warnings:

            print(f"\nAviso: {warning}")

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

        # Aplica o provedor de tradução salvo em Configurações (se o
        # usuário nunca mexeu nisso, config.get() devolve os mesmos
        # padrões que o Translator() já usa por conta própria, então
        # isso não muda nada pra quem não configurou nada).
        config = self.project_manager.config

        provider = config.get("translation_provider", "google")

        if provider in self.translator.PROVIDERS:

            self.translator.provider_settings = dict(
                config.get("translation_provider_settings", {}) or {}
            )

            self.translator.provider_id = provider

            self.translator.fallback_enabled = config.get(
                "translation_fallback_enabled", True
            )

            self.translator.set_fallback_order(
                config.get(
                    "translation_fallback_order",
                    list(self.translator.DEFAULT_FALLBACK_ORDER)
                )
            )

        # Deduplicação: VNs costumam repetir muita linha (falas
        # curtas, nomes, menus). Traduzimos cada texto único uma vez
        # só e aplicamos o resultado em todas as ocorrências, em vez
        # de fazer uma requisição por linha repetida.
        unique_texts = []
        text_to_pending_indices = {}

        for index, dialogue in enumerate(pending):

            text = dialogue["original"]

            if text not in text_to_pending_indices:

                text_to_pending_indices[text] = []
                unique_texts.append(text)

            text_to_pending_indices[text].append(index)

        duplicates_saved = len(pending) - len(unique_texts)

        if duplicates_saved > 0:

            print(
                f"\n{len(unique_texts)} textos únicos entre "
                f"{len(pending)} diálogos pendentes "
                f"({duplicates_saved} repetidos serão reaproveitados "
                "sem nova requisição).\n"
            )

        if len(unique_texts) > 500:

            print(
                f"{len(unique_texts)} textos para traduzir. Isso "
                "envolve requisições para o serviço de tradução "
                "online (em paralelo, com retentativa automática em "
                "caso de falha) — pode demorar. Só aguardar.\n"
            )

        results, interrupted = self.translator.translate_list(unique_texts)

        updates = []

        for text, (translated, ok) in zip(unique_texts, results):

            if not ok:
                continue

            for pending_index in text_to_pending_indices[text]:

                dialogue = pending[pending_index]

                updates.append((translated, "translated", dialogue["id"]))

        failed_count = len(pending) - len(updates)

        if updates:

            self.project_manager.update_dialogues_translations_bulk(
                updates
            )

        if interrupted:

            print(
                f"\nInterrompido. {len(updates)} diálogos já "
                "traduzidos foram salvos. O restante continua "
                "pendente — rode a opção 4 de novo quando quiser "
                "continuar de onde parou.\n"
            )

            return

        print(f"\n{len(updates)} diálogos traduzidos.")

        if failed_count:

            print(
                f"{failed_count} continuam pendentes mesmo após as "
                "retentativas automáticas (provavelmente algo "
                "persistente, como um problema de conexão). Rode a "
                "opção 4 de novo mais tarde para tentar essas.\n"
            )

        else:

            print()

    # ===================================================
    # Passo 5 - Revisar / editar diálogos individualmente
    # ===================================================

    def _review(self, project):

        while True:

            counts = self.project_manager.count_dialogues_by_status(
                project["id"]
            )

            total = sum(counts.values())

            if total == 0:

                print(
                    "\nNenhum diálogo indexado ainda (opção 3).\n"
                )

                return

            print("\n=== Revisar diálogos ===")
            print(f"Total: {total}")
            print(f"  Traduzidos: {counts.get('translated', 0)}")
            print(f"  Revisados manualmente: {counts.get('reviewed', 0)}")
            print(f"  Pendentes: {counts.get('pending', 0)}")

            print(
                "\n1 - Ver todos"
                "\n2 - Ver só traduzidos"
                "\n3 - Ver só revisados manualmente"
                "\n4 - Ver só pendentes"
                "\n0 - Voltar"
            )

            choice = input("\nEscolha: ").strip()

            status_by_choice = {
                "1": None,
                "2": "translated",
                "3": "reviewed",
                "4": "pending",
            }

            if choice == "0":
                return

            if choice not in status_by_choice:

                print("\nOpção inválida.\n")
                continue

            self._review_list(project, status_by_choice[choice])

    def _review_list(self, project, status_filter):

        page_size = 25
        offset = 0

        while True:

            dialogues = self.project_manager.load_dialogues(
                project["id"],
                status=status_filter
            )

            total = len(dialogues)

            if total == 0:

                print("\nNenhum diálogo encontrado com esse filtro.\n")
                return

            if offset >= total:
                offset = max(0, total - page_size)

            page = dialogues[offset:offset + page_size]

            label = status_filter or "todos"

            print(
                f"\n[{label}] Mostrando "
                f"{offset + 1}-{offset + len(page)} de {total}\n"
            )

            for dialogue in page:

                print(
                    f"[{dialogue['id']}] ({dialogue['status']}) "
                    f"{dialogue['original']!r} -> "
                    f"{dialogue['translated']!r}"
                )

            print(
                "\n'n' próxima página, 'p' página anterior, "
                "ID para editar, 'r<ID>' restaurar (ex: r12), "
                "'d<ID>' excluir tradução (ex: d12), "
                "0 para voltar."
            )

            choice = input("\n> ").strip()

            if choice == "0":
                return

            if choice.lower() == "n":

                if offset + page_size < total:
                    offset += page_size
                else:
                    print("\nJá está na última página.\n")

                continue

            if choice.lower() == "p":

                offset = max(0, offset - page_size)
                continue

            if choice.lower().startswith("r") and choice[1:].isdigit():

                self._restore_dialogue(choice[1:])
                continue

            if choice.lower().startswith("d") and choice[1:].isdigit():

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

            new_text = input(
                "Nova tradução (Enter para manter, sem alterar): "
            )

            if new_text.strip():

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

        target = project.get("language_translation", "pt_BR").split("_")[0]

        self.compiler.compile(
            translated,
            str(exports_folder),
            source_base=str(temp_folder),
            language_code=target
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
            f"de '{game_folder}'. Confirmar? (s/n): "
        )

        if confirm.lower() != "s":

            print("\nOperação cancelada.\n")
            return

        # Backup é opcional: o usuário decide na hora se quer ou
        # não. O valor configurado em "auto_backup" (Configurações)
        # só é usado como sugestão padrão da pergunta.
        default_backup = bool(
            self.project_manager.config.get("auto_backup", True)
        )

        default_label = "S" if default_backup else "N"

        backup_input = input(
            "Criar backup dos arquivos do jogo antes de aplicar a "
            f"tradução? (s/n) [padrão: {default_label}]: "
        ).strip().lower()

        if backup_input == "":

            create_backup = default_backup

        else:

            create_backup = backup_input == "s"

        self.patcher.apply_patch(
            str(exports_folder),
            str(game_folder),
            create_backup=create_backup
        )

        if create_backup:

            print("\nTradução aplicada com sucesso (com backup).\n")

        else:

            print(
                "\nTradução aplicada com sucesso (sem backup).\n"
            )

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
            "log_level",
            "unrpyc_path",
            "translation_provider",
            "translation_fallback_enabled"
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