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
            print("0 - Sair")

            option = input("\nEscolha: ")

            match option:

                case "1":
                    self.new_project()

                case "2":
                    self.open_project()

                case "3":
                    self.list_projects()

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

            print(error)

            return

        self.project_manager.create(

            name=name,

            engine=info["engine"],

            version=info["version"],

            game_path=game_path

        )

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

            project = projects[int(option)-1]

        except:

            print("\nProjeto inválido.\n")

            return

        self.project_menu(project)

    # ===================================================

    def project_menu(self, project):

        while True:

            print("\n==============================")

            print(project["name"])

            print("==============================")

            print("1 - Detectar jogo")

            print("2 - Extrair arquivos")

            print("3 - Ler diálogos")

            print("4 - Traduzir")

            print("5 - Gerar arquivos")

            print("6 - Aplicar tradução")

            print("0 - Voltar")

            option = input("\nEscolha: ")

            match option:

                case "1":

                    info = self.detector.detect(

                        project["game_path"]

                    )

                    print()

                    print(info)

                case "2":

                    print(

                        "\nExtractor ainda será integrado.\n"

                    )

                case "3":

                    print(

                        "\nParser ainda será integrado.\n"

                    )

                case "4":

                    print(

                        "\nTranslator ainda será integrado.\n"

                    )

                case "5":

                    print(

                        "\nCompiler ainda será integrado.\n"

                    )

                case "6":

                    print(

                        "\nPatcher ainda será integrado.\n"

                    )

                case "0":

                    break

                case _:

                    print("Opção inválida.")

    # ===================================================


if __name__ == "__main__":

    app = TranslateVN()

    app.menu()