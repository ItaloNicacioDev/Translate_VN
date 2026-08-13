"""
version_sync.py

Sincroniza automaticamente a versão entre o arquivo VERSION (raiz do projeto)
e core/version.py quando detecta uma discrepância. Isso garante que:

1. O arquivo VERSION é a "fonte de verdade"
2. core/version.py sempre reflete a versão no VERSION
3. O instalador (build_gui.bat -> installer.iss) pega a versão correta
4. O app sempre mostra a versão correta

Fluxo:
- Na inicialização, version_sync.sync_if_needed() compara VERSION com
  core/version.py:APP_VERSION. Se forem diferentes, atualiza core/version.py
  automaticamente.
- Isso só reescreve o arquivo uma vez e apenas se necessário.
"""

import os
import re
import sys
from pathlib import Path


def get_version_from_file(file_path: str) -> str:
    """Lê a versão de um arquivo e devolve apenas os dígitos."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        # Remove qualquer prefixo "VERSION" ou similar
        content = content.lstrip('vV').replace('VERSION', '', 1)
        # Pega apenas X.Y.Z
        match = re.match(r'^([\d.]+)', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def sync_if_needed():
    """
    Compara VERSION (raiz) com core/version.py:APP_VERSION.
    Se forem diferentes, atualiza core/version.py automaticamente.
    Funciona tanto rodando com 'python gui_main.py' quanto congelado
    em .exe pelo PyInstaller.
    """
    try:
        # Quando rodando congelado (PyInstaller --onedir), sys._MEIPASS aponta
        # para a pasta raiz do app. Quando rodando via 'python', usamos __file__.
        base_path = getattr(sys, "_MEIPASS", None)
        if base_path is None:
            script_dir = Path(__file__).parent  # core/
            base_path = script_dir.parent  # raiz do projeto
        else:
            base_path = Path(base_path)

        version_file = base_path / "VERSION"
        version_py = base_path / "core" / "version.py"

        if not version_file.exists() or not version_py.exists():
            return  # Arquivos não encontrados, pula sincronização

        # Lê a versão do arquivo VERSION
        version_from_file = get_version_from_file(str(version_file))
        if not version_from_file:
            return  # Arquivo VERSION está vazio ou inválido

        # Lê a versão atual de core/version.py
        with open(version_py, 'r', encoding='utf-8') as f:
            version_py_content = f.read()

        # Extrai APP_VERSION de core/version.py
        match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', version_py_content)
        current_version = match.group(1) if match else None

        # Se as versões são diferentes, atualiza core/version.py
        if current_version != version_from_file:
            # Substitui APP_VERSION com a nova versão
            updated_content = re.sub(
                r'(APP_VERSION\s*=\s*["\'])[^"\']+(["\'])',
                rf'\1{version_from_file}\2',
                version_py_content
            )

            # Escreve o arquivo atualizado
            with open(version_py, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            print(f"✓ Versão sincronizada: {current_version} → {version_from_file}")

    except Exception as e:
        # Silenciosamente ignora erros de sincronização
        # (não queremos quebrar o app por causa disso)
        pass


if __name__ == "__main__":
    sync_if_needed()
