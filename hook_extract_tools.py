"""
hook_extract_tools.py

Runtime hook do PyInstaller (NAO faz parte do projeto original,
NAO precisa colar isso em nenhum arquivo existente).

O que faz: quando o .exe congelado inicia, verifica se os binarios
do unrpyc (embutidos dentro do proprio .exe via --add-binary) ja
foram copiados para "tools/" do lado do executavel. Se nao foram
(primeira execucao), copia agora. Isso e' exatamente onde
core/tool_manager.py (bundled_unrpyc_path) ja espera encontra-los:

    <pasta do exe>/tools/unrpyc_<branch>/unrpyc_<branch>.exe

Versao 2: nao depende mais do binario embutido ter exatamente o
nome "unrpyc_<branch>.exe" -- pega qualquer executavel encontrado
dentro da pasta bundled correspondente e copia/renomeia para o
nome que o tool_manager.py espera. Isso evita quebrar de novo caso
o nome do arquivo de origem mude no processo de build.

Runtime hooks do PyInstaller rodam ANTES do script principal
(main.py) ser importado, entao isso acontece de forma transparente,
sem precisar mudar nada no main.py nem no resto do codigo.
"""

import sys
import os
import shutil


def _is_executable_candidate(filename: str) -> bool:

    if os.name == "nt":
        return filename.lower().endswith(".exe")

    # Em sistemas tipo Unix nao ha extensao .exe: qualquer arquivo
    # ali dentro da pasta bundled e' candidato.
    return True


def _extract_bundled_tools():

    # So faz sentido em build congelada (.exe). Em modo dev
    # (python main.py) isso nem roda, pois o hook so existe dentro
    # do .exe gerado.
    if not getattr(sys, "frozen", False):
        return

    meipass = getattr(sys, "_MEIPASS", None)

    if not meipass:
        return

    app_dir = os.path.dirname(os.path.abspath(sys.executable))

    for branch in ("master", "legacy"):

        exe_name = (
            f"unrpyc_{branch}.exe" if os.name == "nt" else f"unrpyc_{branch}"
        )

        bundled_dir = os.path.join(meipass, "tools", f"unrpyc_{branch}")

        target_dir = os.path.join(app_dir, "tools", f"unrpyc_{branch}")
        target_path = os.path.join(target_dir, exe_name)

        # Ja extraido em execucao anterior - nao refaz o trabalho
        # toda vez que o app abre.
        if os.path.exists(target_path):
            continue

        if not os.path.isdir(bundled_dir):
            # Essa branch nao foi embutida neste build - sem
            # problema, so' nao ha nada pra extrair.
            continue

        candidate = None

        try:
            for filename in os.listdir(bundled_dir):

                full = os.path.join(bundled_dir, filename)

                if not os.path.isfile(full):
                    continue

                if _is_executable_candidate(filename):
                    candidate = full
                    break

        except Exception:
            continue

        if candidate is None:
            continue

        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(candidate, target_path)

            if os.name != "nt":
                os.chmod(target_path, 0o755)

        except Exception:
            # Falha silenciosa aqui: se der errado, o tool_manager.py
            # original vai simplesmente nao encontrar o binario e
            # mostrar o aviso normal dele (ja' tratado no codigo
            # existente). Nao queremos que o app trave por causa
            # do bootstrap.
            pass


_extract_bundled_tools()
