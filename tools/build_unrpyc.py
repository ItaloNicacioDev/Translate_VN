"""
build_unrpyc.py

Script de BUILD (roda só na sua máquina de desenvolvimento, uma vez
-- ou toda vez que quiser atualizar o unrpyc). NÃO faz parte do
app final e não é executado pelo usuário final.

O que ele faz:
1. Baixa o código-fonte do unrpyc (branches 'master' e 'legacy') do
   GitHub.
2. Compila cada um com o PyInstaller num executável standalone
   (.exe no Windows), sem depender de Python/pip/venv em tempo de
   execução.
3. Coloca o resultado em tools/unrpyc_master/ e tools/unrpyc_legacy/
   dentro do projeto -- exatamente onde o ToolManager (em
   core/tool_manager.py) procura por eles em runtime.

Depois de rodar isso, quando você compilar o Translate_VN com
PyInstaller, distribua a pasta 'tools' (com as duas subpastas
unrpyc_master/ e unrpyc_legacy/) JUNTO do .exe principal, na mesma
pasta. O app vai usá-los diretamente, sem baixar nada e sem precisar
de Python instalado na máquina do usuário final.

Uso:
    python tools/build_unrpyc.py

Requisitos (só na sua máquina de dev):
    pip install pyinstaller
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
import io


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

BRANCH_URLS = {
    "master": (
        "https://github.com/CensoredUsername/unrpyc/"
        "archive/refs/heads/master.zip"
    ),
    "legacy": (
        "https://github.com/CensoredUsername/unrpyc/"
        "archive/refs/heads/legacy.zip"
    ),
}


def download_source(branch: str, destination: Path):

    print(f"[{branch}] Baixando código-fonte do unrpyc...")

    request = urllib.request.Request(
        BRANCH_URLS[branch],
        headers={"User-Agent": "TranslateVN-Build"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        archive.extractall(destination)

    root_folders = [item for item in destination.iterdir() if item.is_dir()]

    if not root_folders:
        raise RuntimeError(f"Download do unrpyc ({branch}) veio vazio.")

    return root_folders[0]


def build_executable(branch: str, source_folder: Path):

    print(f"[{branch}] Compilando com PyInstaller...")

    exe_name = f"unrpyc_{branch}"

    build_work_dir = source_folder / "_pyinstaller_build"
    dist_dir = source_folder / "_pyinstaller_dist"

    result = subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", exe_name,
            "--distpath", str(dist_dir),
            "--workpath", str(build_work_dir),
            "--specpath", str(build_work_dir),
            str(source_folder / "unrpyc.py"),
        ],
        cwd=str(source_folder),
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Falha ao compilar unrpyc ({branch}) com PyInstaller."
        )

    produced = dist_dir / exe_name
    produced_exe = dist_dir / f"{exe_name}.exe"

    if produced_exe.exists():
        return produced_exe

    if produced.exists():
        return produced

    raise RuntimeError(
        f"PyInstaller rodou mas não encontrei o executável gerado "
        f"para '{branch}' em {dist_dir}."
    )


def install_into_tools_dir(branch: str, built_exe: Path):

    target_dir = TOOLS_DIR / f"unrpyc_{branch}"

    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / built_exe.name

    shutil.copy2(built_exe, target_path)

    print(f"[{branch}] OK -> {target_path}")


def main():

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print(
            "PyInstaller não está instalado neste ambiente. "
            "Rode: pip install pyinstaller"
        )
        sys.exit(1)

    with tempfile.TemporaryDirectory(prefix="unrpyc_build_") as tmp:

        tmp_path = Path(tmp)

        for branch in BRANCH_URLS:

            branch_tmp = tmp_path / branch
            branch_tmp.mkdir()

            source_folder = download_source(branch, branch_tmp)
            built_exe = build_executable(branch, source_folder)
            install_into_tools_dir(branch, built_exe)

    print(
        "\nPronto! Agora, ao compilar o Translate_VN com PyInstaller, "
        "distribua a pasta 'tools' (com unrpyc_master/ e "
        "unrpyc_legacy/) na mesma pasta do .exe final."
    )


if __name__ == "__main__":
    main()