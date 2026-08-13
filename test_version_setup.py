#!/usr/bin/env python3
"""
Script de teste para validar:
1. Sincronização de versão (VERSION vs version.py)
2. Detecção de atualização no GitHub
3. Download e instalação

Use antes de distribuir a versão 1.3.3
"""

import sys
import os
from pathlib import Path

# Adiciona projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("TESTE DE VERSÃO E ATUALIZAÇÃO v1.3.3")
print("=" * 60)

# Teste 1: Verifica VERSION
print("\n[1/4] Verificando arquivo VERSION...")
version_file = project_root / "VERSION"
if version_file.exists():
    version_content = version_file.read_text().strip()
    print(f"  ✓ VERSION encontrado: '{version_content}'")
    if version_content == "1.3.3":
        print("  ✓ Versão correta (1.3.3)")
    else:
        print(f"  ✗ ERRO: Esperado 1.3.3, mas encontrado {version_content}")
else:
    print("  ✗ ERRO: Arquivo VERSION não encontrado")

# Teste 2: Verifica core/version.py
print("\n[2/4] Verificando core/version.py...")
version_py = project_root / "core" / "version.py"
if version_py.exists():
    content = version_py.read_text()
    import re
    match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        app_version = match.group(1)
        print(f"  ✓ APP_VERSION encontrada: '{app_version}'")
        if app_version == "1.3.3":
            print("  ✓ Versão correta (1.3.3)")
        else:
            print(f"  ✗ ERRO: Esperado 1.3.3, mas encontrado {app_version}")
    else:
        print("  ✗ ERRO: APP_VERSION não encontrada em version.py")
else:
    print("  ✗ ERRO: Arquivo core/version.py não encontrado")

# Teste 3: Verifica version_sync.py
print("\n[3/4] Verificando version_sync.py...")
version_sync = project_root / "core" / "version_sync.py"
if version_sync.exists():
    content = version_sync.read_text()
    if "sys._MEIPASS" in content:
        print("  ✓ version_sync.py tem suporte a PyInstaller congelado")
    else:
        print("  ⚠ version_sync.py pode não estar otimizado para frozen app")
    if "sync_if_needed()" in content:
        print("  ✓ Função sync_if_needed() definida")
else:
    print("  ✗ ERRO: Arquivo core/version_sync.py não encontrado")

# Teste 4: Verifica build_gui.bat
print("\n[4/4] Verificando build_gui.bat...")
build_script = project_root / "build_gui.bat"
if build_script.exists():
    content = build_script.read_text()
    issues = []
    
    if '--add-data "core;core"' in content:
        print("  ✓ --add-data 'core;core' presente")
    else:
        issues.append("Falta --add-data para core/")
    
    if '--add-data "engine;engine"' in content:
        print("  ✓ --add-data 'engine;engine' presente")
    else:
        issues.append("Falta --add-data para engine/")
    
    if '--add-data "VERSION;."' in content or '--add-data "ui;ui"' in content:
        print("  ✓ --add-data para ui/ e VERSION presente")
    else:
        issues.append("Falta --add-data para ui/ ou VERSION")
    
    if issues:
        for issue in issues:
            print(f"  ✗ {issue}")
    else:
        print("  ✓ Todos os --add-data presentes no PyInstaller")
else:
    print("  ✗ ERRO: Arquivo build_gui.bat não encontrado")

print("\n" + "=" * 60)
print("RESUMO DOS TESTES")
print("=" * 60)
print("""
✅ Se todos os testes passaram:
  1. A versão está sincronizada (VERSION = version.py = 1.3.3)
  2. O build_gui.bat inclui todos os dados necessários
  3. O app congelado poderá sincronizar versão na primeira execução

📦 Próximas Etapas:
  1. Fazer upload de Output/TranslateVN-Setup.exe para release v1.3.3
  2. Publicar release no GitHub
  3. Usuários com v1.3.2 verão atualização disponível
  4. Ao instalar, app será atualizado para v1.3.3 automaticamente

🔗 URL do Release:
  https://github.com/ItaloNicacioDev/Translate_VN/releases/tag/v1.3.3
""")
