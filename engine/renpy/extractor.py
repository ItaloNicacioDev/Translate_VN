"""
extractor.py

Responsável pela extração dos arquivos de jogos Ren'Py.

A obtenção das ferramentas externas (unrpa/unrpyc) é delegada ao
ToolManager (core/tool_manager.py): unrpa é instalado via pip
automaticamente se faltar, e o unrpyc é baixado e cacheado sob
demanda nas duas variantes (master = Ren'Py 8, legacy = Ren'Py 6/7),
tentando uma e caindo para a outra automaticamente quando a versão
do jogo não é conhecida de antemão. Isso é o que torna o app
universal: não é necessário descobrir/baixar/configurar nada na mão
na maioria dos casos.

Se o usuário preferir usar uma cópia própria do unrpyc (por exemplo
uma build com deobfuscação customizada para um jogo específico),
ainda é possível apontar para ela via config.json -> "unrpyc_path",
que tem prioridade sobre o download automático.
"""

from pathlib import Path
import shutil
import subprocess

from core.logger import Logger
from core.config_manager import ConfigManager
from core.tool_manager import ToolManager


class RenPyExtractor:

    def __init__(self):

        self.logger = Logger()

        self.config = ConfigManager()

        self.tools = ToolManager(
            self.config.get("tools_folder", "tools")
        )

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

    def copy_scripts(
        self,
        game_folder: str,
        output_path: str
    ):

        game_folder = Path(game_folder)
        output = self.prepare_workspace(output_path)

        copied = 0
        skipped_tl = 0

        for file in game_folder.rglob("*.rpy"):

            # Arquivos dentro de qualquer pasta "tl" são traduções
            # que o PRÓPRIO jogo já traz (estrutura oficial do
            # Ren'Py: game/tl/<idioma>/*.rpy) - não é conteúdo
            # original, é uma tradução já pronta de outra pessoa.
            # Tratar isso como "original a traduzir" duplica
            # trabalho e mistura textos de idiomas diferentes.
            if "tl" in file.relative_to(game_folder).parts[:-1]:

                skipped_tl += 1
                continue

            destination = output / file.relative_to(game_folder)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(file, destination)

            copied += 1

        if skipped_tl:

            self.logger.info(
                f"{skipped_tl} script(s) ignorados por estarem "
                "dentro de uma pasta de tradução já existente do "
                "jogo (game/tl/...)."
            )

        self.logger.info(
            f"{copied} scripts .rpy copiados."
        )

        return copied

    # -------------------------------------------------
    # unrpa
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

        try:
            from unrpa import UnRPA
        except ImportError as error:

            raise RuntimeError(
                "O módulo 'unrpa' não está disponível nesta build. "
                "Ele precisa estar instalado no ambiente usado para "
                "gerar o .exe (pip install unrpa) para que o "
                "PyInstaller o inclua no pacote."
            ) from error

        try:

            unrpa_extractor = UnRPA(
                str(rpa),
                0,
                str(output),
                True,
                None,
                True,
                None,
            )

            unrpa_extractor.extract_files()

        except Exception as error:

            raise RuntimeError(
                f"Falha ao extrair {rpa.name}: {error}"
            ) from error

        self.logger.info(
            "Extração concluída."
        )

    # -------------------------------------------------
    # unrpyc
    # -------------------------------------------------

    def _run_unrpyc(self, tool_path: Path, game_folder: str):

        if tool_path.suffix.lower() == ".py":

            # Modo dev: é o script baixado do GitHub, precisa de um
            # interpretador Python de verdade pra rodar.
            python_executable = ToolManager.get_python_executable()

            if not python_executable:

                raise RuntimeError(
                    "Não foi possível descompilar: nenhum "
                    "interpretador Python de verdade foi encontrado "
                    "no sistema (esta é uma build compilada). "
                    "Instale Python e garanta que ele fique "
                    "acessível no PATH."
                )

            args = [python_executable, str(tool_path), str(game_folder)]

        else:

            # Executável já compilado (bundled ou apontado
            # manualmente em unrpyc_path) -- roda direto, sem
            # depender de nenhum Python instalado.
            args = [str(tool_path), str(game_folder)]

        try:

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=600
            )

        except subprocess.TimeoutExpired:

            raise RuntimeError(
                "Tempo esgotado ao descompilar "
                "(mais de 10 minutos sem resposta)."
            )

        if result.returncode != 0:

            raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    # ---------------------------------------------------

    def decompile_rpyc(self, game_folder: str) -> bool:
        """Tenta descompilar usando, nesta ordem:

        1. unrpyc_path configurado manualmente (se existir)
        2. unrpyc branch 'master' (baixado/cacheado automaticamente)
        3. unrpyc branch 'legacy' (baixado/cacheado automaticamente)

        Retorna True se algum deles funcionou.
        """

        manual_path = self.config.get("unrpyc_path")

        if manual_path and Path(manual_path).exists():

            try:

                self._run_unrpyc(Path(manual_path), game_folder)

                self.logger.info(
                    "Descompilado com sucesso usando o unrpyc "
                    "configurado manualmente."
                )

                return True

            except RuntimeError as error:

                self.logger.warning(
                    f"unrpyc configurado manualmente falhou: {error}"
                )

        for branch in ("master", "legacy"):

            script = self.tools.ensure_unrpyc(branch)

            if script is None:
                # Sem internet ou falha no download - não adianta
                # tentar a outra branch agora, mas não é um erro
                # fatal ainda (pode já ter dado certo com outra).
                continue

            try:

                self._run_unrpyc(script, game_folder)

                self.logger.info(
                    f"Descompilado com sucesso usando unrpyc "
                    f"({branch})."
                )

                return True

            except RuntimeError as error:

                self.logger.warning(
                    f"Falha ao descompilar com unrpyc ({branch}): "
                    f"{error}"
                )

        return False

    # -------------------------------------------------
    # Fluxo completo
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

        # Extrai todos os .rpa, se houver
        if game_info["archives"]:

            if self.tools.ensure_unrpa():

                for archive in game_info["archives"]:

                    self.extract_rpa(archive, output)

            else:

                warnings.append(
                    "Existem arquivos .rpa, mas não foi possível "
                    "instalar/usar 'unrpa' automaticamente. Tente "
                    "manualmente: pip install unrpa"
                )

        # Descompila scripts .rpyc, se houver
        if game_info["compiled_scripts"]:

            success = self.decompile_rpyc(
                game_info["game_folder"]
            )

            if success:

                # O unrpyc gera os .rpy dentro da própria pasta do
                # jogo, ao lado dos .rpyc. Copiamos para o workspace.
                self.copy_scripts(
                    game_info["game_folder"],
                    output
                )

            else:

                warnings.append(
                    "Existem arquivos .rpyc compilados, mas não foi "
                    "possível descompilá-los automaticamente (nem "
                    "com master nem com legacy do unrpyc). Verifique "
                    "sua conexão com a internet, ou configure "
                    "'unrpyc_path' em Configurações apontando para "
                    "uma cópia própria."
                )

        for warning in warnings:

            self.logger.warning(warning)

        self.logger.info(
            "Processo de extração finalizado."
        )

        return warnings