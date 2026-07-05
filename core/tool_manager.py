"""
tool_manager.py

Obtenção automática das ferramentas externas necessárias para lidar
com jogos Ren'Py compactados/compilados, para que o app funcione de
forma universal sem exigir passos manuais na maioria dos casos.

- unrpa (.rpa): tem pacote pip oficial. Se não estiver disponível,
  instalamos via `pip install unrpa` automaticamente.

- unrpyc (.rpyc): não tem pacote pip. É um script mantido em duas
  branches no GitHub, cada uma compatível com uma faixa de versões
  do Ren'Py:
    - master -> Ren'Py 8.x (bytecode Python 3)
    - legacy -> Ren'Py 6.x / 7.x (bytecode Python 2)
  Como nem sempre dá pra saber de antemão qual branch o jogo precisa,
  baixamos e cacheamos as duas sob demanda, e o extractor tenta uma
  e cai para a outra automaticamente se a primeira falhar.
"""

from pathlib import Path
import subprocess
import sys
import urllib.request
import urllib.error
import zipfile
import io
import shutil

from core.logger import Logger


class ToolManager:

    UNRPYC_BRANCH_URLS = {
        "master": (
            "https://github.com/CensoredUsername/unrpyc/"
            "archive/refs/heads/master.zip"
        ),
        "legacy": (
            "https://github.com/CensoredUsername/unrpyc/"
            "archive/refs/heads/legacy.zip"
        ),
    }

    def __init__(self, tools_folder: str = "tools"):

        self.logger = Logger()

        self.tools_folder = Path(tools_folder)

        self.tools_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    # ===================================================
    # unrpa
    # ===================================================

    def is_unrpa_available(self) -> bool:

        if shutil.which("unrpa"):
            return True

        try:

            result = subprocess.run(
                [sys.executable, "-m", "unrpa", "--version"],
                capture_output=True,
                check=False,
                stdin=subprocess.DEVNULL,
                timeout=30
            )

            return result.returncode == 0

        except (FileNotFoundError, subprocess.TimeoutExpired):

            return False

    # ---------------------------------------------------

    def ensure_unrpa(self) -> bool:
        """Garante que 'unrpa' está disponível, instalando via pip
        automaticamente se necessário. Retorna True se, ao final,
        a ferramenta está disponível (já estava ou acabou de ser
        instalada)."""

        if self.is_unrpa_available():
            return True

        self.logger.info(
            "'unrpa' não encontrado. Instalando automaticamente "
            "via pip..."
        )

        try:

            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "unrpa"],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=120
            )

        except Exception as error:

            self.logger.error(
                f"Falha ao instalar unrpa automaticamente: {error}"
            )

            return False

        if result.returncode != 0:

            self.logger.error(
                "Falha ao instalar unrpa automaticamente: "
                f"{result.stderr.strip()}"
            )

            return False

        self.logger.info("'unrpa' instalado com sucesso.")

        return self.is_unrpa_available()

    # ===================================================
    # unrpyc
    # ===================================================

    def unrpyc_script_path(self, branch: str) -> Path:

        return self.tools_folder / f"unrpyc_{branch}" / "unrpyc.py"

    # ---------------------------------------------------

    def is_unrpyc_cached(self, branch: str) -> bool:

        return self.unrpyc_script_path(branch).exists()

    # ---------------------------------------------------

    def ensure_unrpyc(self, branch: str = "master"):
        """Garante que o unrpyc da branch pedida está baixado e
        cacheado localmente em tools/unrpyc_<branch>/. Retorna o
        Path do unrpyc.py, ou None se não foi possível obter
        (ex: sem internet no momento)."""

        if branch not in self.UNRPYC_BRANCH_URLS:

            raise ValueError(
                f"Branch de unrpyc desconhecida: {branch}"
            )

        script_path = self.unrpyc_script_path(branch)

        if script_path.exists():
            return script_path

        self.logger.info(
            f"Baixando unrpyc ({branch}) automaticamente pela "
            "primeira vez, isso só acontece uma vez..."
        )

        destination_folder = self.tools_folder / f"unrpyc_{branch}"

        try:

            self._download_and_extract(
                self.UNRPYC_BRANCH_URLS[branch],
                destination_folder
            )

        except (urllib.error.URLError, OSError, TimeoutError) as error:

            self.logger.error(
                "Não foi possível baixar o unrpyc automaticamente "
                f"({branch}): {error}. Verifique a conexão com a "
                "internet, ou baixe manualmente em "
                "https://github.com/CensoredUsername/unrpyc e "
                "configure 'unrpyc_path' em Configurações."
            )

            return None

        if script_path.exists():

            self.logger.info(f"unrpyc ({branch}) pronto para uso.")

            return script_path

        self.logger.error(
            "Download concluído, mas unrpyc.py não foi encontrado "
            f"dentro do pacote baixado ({branch})."
        )

        return None

    # ---------------------------------------------------

    def _download_and_extract(self, url: str, destination_folder: Path):

        destination_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "TranslateVN"}
        )

        with urllib.request.urlopen(request, timeout=30) as response:

            data = response.read()

        self._extract_zip_flattened(data, destination_folder)

    # ---------------------------------------------------

    def _extract_zip_flattened(self, zip_bytes: bytes, destination_folder: Path):
        """O zip baixado do GitHub vem com uma pasta raiz do tipo
        'unrpyc-master/'. Extraímos num diretório temporário e
        movemos o conteúdo de dentro dessa pasta raiz direto para
        destination_folder, sem essa camada extra."""

        temp_extract = destination_folder / "_download_tmp"

        if temp_extract.exists():
            shutil.rmtree(temp_extract)

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:

            archive.extractall(temp_extract)

        root_folders = [
            item for item in temp_extract.iterdir() if item.is_dir()
        ]

        source_root = root_folders[0] if root_folders else temp_extract

        for item in source_root.iterdir():

            target = destination_folder / item.name

            if target.exists():

                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()

            shutil.move(str(item), str(target))

        shutil.rmtree(temp_extract)