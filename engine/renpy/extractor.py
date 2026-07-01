"""
extractor.py

Responsável pela extração dos arquivos de jogos Ren'Py.

IMPORTANTE sobre as ferramentas externas:

- unrpa (arquivos .rpa): tem pacote pip oficial (`pip install unrpa`),
  então chamamos via `python -m unrpa`, que funciona mesmo quando o
  executável `unrpa` não está no PATH (comum em venvs no Windows).

- unrpyc (arquivos .rpyc): NÃO tem pacote pip oficial. É um script
  `unrpyc.py` (+ pasta `decompiler/`) que o usuário baixa do GitHub
  em https://github.com/CensoredUsername/unrpyc e cuja versão precisa
  bater com a versão do Ren'Py usada para compilar o jogo. Por isso
  o caminho para esse script é configurável (config.json ->
  "unrpyc_path"), e tentamos localizá-lo automaticamente antes de
  desistir.
"""

from pathlib import Path
import shutil
import subprocess
import sys

from core.logger import Logger
from core.config_manager import ConfigManager


class RenPyExtractor:

    def __init__(self):

        self.logger = Logger()

        self.config = ConfigManager()

    # -------------------------------------------------
    # Utilitários
    # -------------------------------------------------

    def prepare_workspace(self, output_path: str):

        output = Path(output_path)

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        return output

    # -------------------------------------------------

    def find_unrpyc(self) -> str | None:
        """Tenta localizar o unrpyc.py em, nesta ordem:

        1. Configuração salva (config.json -> unrpyc_path)
        2. Uma pasta 'tools/unrpyc' ao lado do projeto
        3. O PATH do sistema (caso o usuário tenha criado um .bat/.sh
           chamado 'unrpyc' que encapsule 'python unrpyc.py')
        """

        configured = self.config.get("unrpyc_path")

        if configured:

            path = Path(configured)

            if path.exists():
                return str(path)

            self.logger.warning(
                f"unrpyc_path configurado ('{configured}') não existe."
            )

        local_candidate = Path("tools") / "unrpyc" / "unrpyc.py"

        if local_candidate.exists():
            return str(local_candidate)

        found_on_path = shutil.which("unrpyc")

        if found_on_path:
            return found_on_path

        return None

    # -------------------------------------------------

    def is_unrpa_available(self) -> bool:

        if shutil.which("unrpa"):
            return True

        try:

            result = subprocess.run(
                [sys.executable, "-m", "unrpa", "--version"],
                capture_output=True,
                check=False
            )

            return result.returncode == 0

        except FileNotFoundError:

            return False

    # -------------------------------------------------

    def copy_scripts(
        self,
        game_folder: str,
        output_path: str
    ):

        game_folder = Path(game_folder)
        output = self.prepare_workspace(output_path)

        copied = 0

        for file in game_folder.rglob("*.rpy"):

            destination = output / file.relative_to(game_folder)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(file, destination)

            copied += 1

        self.logger.info(
            f"{copied} scripts .rpy copiados."
        )

        return copied

    # -------------------------------------------------

    def extract_rpa(
        self,
        rpa_file: str,
        output_path: str
    ):

        rpa = Path(rpa_file)

        if not rpa.exists():

            raise FileNotFoundError(rpa)

        output = self.prepare_workspace(output_path)

        self.logger.info(
            f"Extraindo {rpa.name}"
        )

        command = shutil.which("unrpa")

        if command:

            args = [command, "-mp", str(output), str(rpa)]

        else:

            args = [
                sys.executable, "-m", "unrpa",
                "-mp", str(output), str(rpa)
            ]

        result = subprocess.run(
            args,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                "Falha ao extrair "
                f"{rpa.name}: {result.stderr.strip()}"
            )

        self.logger.info(
            "Extração concluída."
        )

    # -------------------------------------------------

    def decompile_rpyc(
        self,
        game_folder: str
    ):

        unrpyc_script = self.find_unrpyc()

        if unrpyc_script is None:

            raise FileNotFoundError(
                "unrpyc.py não encontrado. Baixe em "
                "https://github.com/CensoredUsername/unrpyc "
                "(escolha a versão compatível com o Ren'Py do jogo) "
                "e configure o caminho em Configurações "
                "-> unrpyc_path."
            )

        game_folder = Path(game_folder)

        self.logger.info(
            "Descompilando arquivos .rpyc..."
        )

        result = subprocess.run(
            [sys.executable, unrpyc_script, str(game_folder)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"Falha ao descompilar: {result.stderr.strip()}"
            )

        self.logger.info(
            "Descompilação concluída."
        )

    # -------------------------------------------------

    def extract_all(
        self,
        game_info: dict,
        output_path: str
    ):

        output = self.prepare_workspace(output_path)

        warnings = []

        # Copia scripts .rpy já existentes (jogos não empacotados)
        self.copy_scripts(
            game_info["game_folder"],
            output
        )

        # Extrai todos os .rpa, se houver e a ferramenta estiver
        # disponível
        if game_info["archives"]:

            if self.is_unrpa_available():

                for archive in game_info["archives"]:

                    self.extract_rpa(archive, output)

            else:

                warnings.append(
                    "Existem arquivos .rpa, mas 'unrpa' não está "
                    "disponível. Instale com: pip install unrpa"
                )

        # Descompila scripts .rpyc, se houver e a ferramenta estiver
        # configurada
        if game_info["compiled_scripts"]:

            if self.find_unrpyc():

                self.decompile_rpyc(
                    game_info["game_folder"]
                )

                # Depois de descompilar, os novos .rpy aparecem
                # dentro da própria pasta do jogo (é assim que o
                # unrpyc funciona: gera .rpy ao lado do .rpyc).
                # Precisamos copiá-los também para o workspace.
                self.copy_scripts(
                    game_info["game_folder"],
                    output
                )

            else:

                warnings.append(
                    "Existem arquivos .rpyc compilados, mas "
                    "'unrpyc_path' não está configurado. Baixe o "
                    "unrpyc em "
                    "https://github.com/CensoredUsername/unrpyc "
                    "e configure o caminho em Configurações."
                )

        for warning in warnings:

            self.logger.warning(warning)

        self.logger.info(
            "Processo de extração finalizado."
        )

        return warnings