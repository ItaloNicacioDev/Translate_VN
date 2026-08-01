"""
updater.py

Verificador e instalador de atualizacoes via GitHub Releases,
igual ao que softwares "triple A" fazem: o app checa sozinho se
existe uma versao mais nova publicada, baixa o instalador e se
atualiza sem o usuario precisar abrir o navegador.

Fluxo:
  1. check_for_update() consulta a GitHub Releases API do
     repositorio ItaloNicacioDev/Translate_VN e compara a tag da
     release mais recente com a versao atual (core/version.py).
  2. Se houver uma versao mais nova, download_installer() baixa o
     instalador (.exe) anexado aquela release para uma pasta
     temporaria, reportando progresso incremental via callback.
  3. install_and_restart() dispara o instalador baixado em modo
     totalmente silencioso (/VERYSILENT) e devolve o processo pro
     chamador (gui_api.py), que fecha a janela atual logo em
     seguida -- e' isso que libera os arquivos que o Inno Setup
     precisa sobrescrever. O proprio instalador reabre o app
     sozinho ao terminar (ver installer.iss, secao [Run]).

Nao e' preciso nenhuma credencial: o repositorio e' publico, entao
a API do GitHub e' usada sem autenticacao (limite de 60
requisicoes/hora por IP -- de sobra pra uma checagem por sessao).
Qualquer falha de rede/API e' tratada como "sem atualizacao
disponivel" em vez de quebrar o app.
"""

import os
import re
import sys
import tempfile
import subprocess

import requests

from core.version import APP_VERSION


class UpdateError(Exception):
    pass


class Updater:

    REPO = "ItaloNicacioDev/Translate_VN"
    API_LATEST_RELEASE = f"https://api.github.com/repos/{REPO}/releases/latest"
    RELEASES_PAGE = f"https://github.com/{REPO}/releases"

    # Nome esperado do asset do instalador dentro da release --
    # e' exatamente o que build_gui.bat + installer.iss geram
    # (Output\TranslateVN-Setup.exe).
    ASSET_NAME = "TranslateVN-Setup.exe"

    REQUEST_HEADERS = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "TranslateVN-Updater",
    }

    def __init__(self):
        self._download_path = None

    # -------------------------------------------------
    # Comparacao de versao (semver simplificado, sem
    # dependencia externa: "v1.2.3" / "1.2.3" -> (1, 2, 3))
    # -------------------------------------------------

    @staticmethod
    def _parse_version(value: str):

        cleaned = (value or "").strip().lstrip("vV")
        cleaned = re.split(r"[-+]", cleaned, maxsplit=1)[0]

        parts = []
        for chunk in cleaned.split("."):
            digits = re.match(r"\d+", chunk)
            parts.append(int(digits.group()) if digits else 0)

        while len(parts) < 3:
            parts.append(0)

        return tuple(parts[:3])

    def is_newer(self, remote_version: str, local_version: str = APP_VERSION) -> bool:

        return self._parse_version(remote_version) > self._parse_version(local_version)

    # -------------------------------------------------
    # 1. Checagem
    # -------------------------------------------------

    def check_for_update(self, timeout: int = 8) -> dict:
        """Consulta a release mais recente no GitHub. Nunca
        levanta excecao por falha de rede -- devolve
        {"available": False, "error": "..."} nesse caso, pra
        checagem de update nunca travar/quebrar o app."""

        try:
            response = requests.get(
                self.API_LATEST_RELEASE,
                headers=self.REQUEST_HEADERS,
                timeout=timeout
            )
            response.raise_for_status()
            release = response.json()

        except Exception as error:
            return {
                "available": False,
                "current_version": APP_VERSION,
                "error": str(error),
            }

        remote_tag = release.get("tag_name", "") or ""
        notes = release.get("body", "") or ""
        published_at = release.get("published_at", "")

        asset = self._find_installer_asset(release.get("assets", []) or [])

        available = bool(remote_tag) and self.is_newer(remote_tag) and asset is not None

        return {
            "available": available,
            "current_version": APP_VERSION,
            "latest_version": remote_tag.lstrip("vV") if remote_tag else None,
            "notes": notes,
            "published_at": published_at,
            "download_url": asset["browser_download_url"] if asset else None,
            "asset_size": asset.get("size") if asset else None,
            "releases_url": self.RELEASES_PAGE,
        }

    def _find_installer_asset(self, assets: list):

        for asset in assets:
            if asset.get("name") == self.ASSET_NAME:
                return asset

        # fallback: qualquer .exe anexado a release, caso o nome
        # do asset mude no futuro
        for asset in assets:
            if asset.get("name", "").lower().endswith(".exe"):
                return asset

        return None

    # -------------------------------------------------
    # 2. Download
    # -------------------------------------------------

    def download_installer(self, download_url: str, progress_callback=None) -> str:
        """Baixa o instalador pra uma pasta temporaria, chamando
        progress_callback(baixado_bytes, total_bytes) a cada
        pedaco recebido. Devolve o caminho local do .exe baixado."""

        dest_dir = os.path.join(tempfile.gettempdir(), "TranslateVN_Update")
        os.makedirs(dest_dir, exist_ok=True)

        dest_path = os.path.join(dest_dir, self.ASSET_NAME)

        try:
            with requests.get(
                download_url,
                headers=self.REQUEST_HEADERS,
                stream=True,
                timeout=30
            ) as response:

                response.raise_for_status()

                total = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(dest_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=256 * 1024):

                        if not chunk:
                            continue

                        file.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback:
                            progress_callback(downloaded, total)

        except Exception as error:
            raise UpdateError(f"Falha ao baixar atualizacao: {error}")

        self._download_path = dest_path

        return dest_path

    # -------------------------------------------------
    # 3. Instalacao
    # -------------------------------------------------

    def install_and_restart(self, installer_path: str = None):
        """Dispara o instalador baixado em modo totalmente
        silencioso (sem nenhuma janela/prompt) e devolve o Popen do
        processo. Quem chamar este metodo (gui_api.py) e'
        responsavel por fechar a janela atual logo em seguida, pra
        soltar o lock dos arquivos que o Inno Setup precisa
        sobrescrever."""

        installer_path = installer_path or self._download_path

        if not installer_path or not os.path.exists(installer_path):
            raise UpdateError(
                "Instalador nao encontrado. Baixe a atualizacao novamente."
            )

        args = [
            installer_path,
            "/VERYSILENT",
            "/SUPPRESSMSGBOXES",
            "/NORESTART",
            "/CLOSEAPPLICATIONS",
            "/RESTARTAPPLICATIONS",
            "/NOCANCEL",
        ]

        popen_kwargs = {"close_fds": True}

        if sys.platform == "win32":
            popen_kwargs["creationflags"] = (
                subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
            )

        try:
            return subprocess.Popen(args, **popen_kwargs)
        except Exception as error:
            raise UpdateError(f"Falha ao iniciar o instalador: {error}")