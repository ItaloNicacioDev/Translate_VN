#!/usr/bin/env python3
# ===========================================================
# build.py  —  Gera o instalador do Translate VN (Windows)
# ===========================================================
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / "build_env"
VENV_PY = VENV / "Scripts" / "python.exe"
ISCC_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
    Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    Path(r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe"),
    Path(r"C:\Program Files\Inno Setup 7\ISCC.exe"),
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 7" / "ISCC.exe",
    Path("E:/Inno Setup 6/ISCC.exe"),
    Path("E:/Inno Setup 7/ISCC.exe"),
    Path("E:/eagames/Inno Setup 7/ISCC.exe"),
    Path("E:/Program Files/Inno Setup 6/ISCC.exe"),
    Path("E:/Program Files/Inno Setup 7/ISCC.exe"),
    Path("E:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
    Path("E:/Program Files (x86)/Inno Setup 7/ISCC.exe"),
]


def run(cmd, **kwargs):
    print(f"> {cmd}")
    return subprocess.run(cmd, check=True, **kwargs)


def main():
    print("=" * 60)
    print("Translate VN — Build do instalador Windows")
    print("=" * 60)

    # 0. Verificações prévias
    for f in ["app_icon.ico", "installer.iss", "gui_main.py", "hook_extract_tools.py"]:
        if not (ROOT / f).exists():
            print(f"ERRO: {f} não encontrado na raiz do projeto.")
            sys.exit(1)

    # 1. Criar venv de build se não existir
    if not VENV.exists():
        print("\n[1/6] Criando ambiente virtual de build...")
        run([sys.executable, "-m", "venv", str(VENV)])
    else:
        print("\n[1/6] Ambiente virtual de build já existe.")

    # 2. Instalar dependências no venv
    print("\n[2/6] Instalando dependências...")
    run([str(VENV_PY), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(VENV_PY), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    run([str(VENV_PY), "-m", "pip", "install", "unrpa", "pyinstaller", "pywebview"])

    # 3. Compilar unrpyc_master
    unrpyc_exe = ROOT / "unrpyc_master.exe"
    dist_unrpyc = ROOT / "dist" / "unrpyc_master.exe"
    if not unrpyc_exe.exists() and not dist_unrpyc.exists():
        print("\n[3/6] Compilando unrpyc (master)...")
        run(
            [
                str(VENV_PY),
                "-c",
                "import PyInstaller.__main__ as m; m.run(["
                "'--onefile', '--name', 'unrpyc_master', "
                "'tools/unrpyc_master/unrpyc.py'])",
            ],
            cwd=str(ROOT),
        )
    else:
        print("\n[3/6] unrpyc_master.exe já existe, pulando.")

    # Garante que o unrpyc_master.exe esteja na raiz (PyInstaller pode ter
    # colocado em dist/).
    if dist_unrpyc.exists() and not unrpyc_exe.exists():
        shutil.copy2(str(dist_unrpyc), str(unrpyc_exe))

    # 4. Compilar app principal com PyInstaller
    print("\n[4/6] Compilando app com PyInstaller (--onedir)...")
    run(
        [
            str(VENV_PY),
            "-c",
            "import PyInstaller.__main__ as m; m.run(["
            "'--onedir', '--windowed', '--name', 'TranslateVN-GUI', "
            "'--icon', 'app_icon.ico', "
            "'--add-binary', 'unrpyc_master.exe;tools/unrpyc_master', "
            "'--add-data', 'ui;ui', "
            "'--add-data', 'core;core', "
            "'--add-data', 'engine;engine', "
            "'--add-data', 'VERSION;.', "
            "'--runtime-hook', 'hook_extract_tools.py', "
            "'gui_main.py'])",
        ],
        cwd=str(ROOT),
    )

    exe = ROOT / "dist" / "TranslateVN-GUI" / "TranslateVN-GUI.exe"
    if not exe.exists():
        print("ERRO: PyInstaller não gerou o executável.")
        sys.exit(1)

    # 5. Encontrar o Inno Setup
    iscc = None
    for cand in ISCC_CANDIDATES:
        if cand.exists():
            iscc = str(cand)
            break
    if not iscc:
        print("ERRO: Inno Setup (ISCC.exe) não encontrado.")
        print("Instale em: https://jrsoftware.org/isdl.php")
        sys.exit(1)
    print(f"\n[5/6] Inno Setup encontrado: {iscc}")

    # 6. Ler versão
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    print(f"[6/6] Versão: {version}")
    print("Compilando instalador com Inno Setup...")
    run([iscc, f"/DMyAppVersion={version}", "installer.iss"], cwd=str(ROOT))

    installer = ROOT / "Output" / "TranslateVN-Setup.exe"
    if not installer.exists():
        # Inno Setup pode ter colocado em outro lugar
        for cand in [
            ROOT / "TranslateVN-Setup.exe",
            Path(os.environ.get("TEMP", "")) / "TranslateVN-Setup-Build" / "TranslateVN-Setup.exe",
        ]:
            if cand.exists():
                installer = cand
                break
    if not installer.exists():
        print("ERRO: Instalador não encontrado após a compilação.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"Pronto! Instalador: {installer}")
    print("=" * 60)


if __name__ == "__main__":
    main()
