#!/usr/bin/env python3
"""
Script para fazer upload do TranslateVN-Setup.exe para a release v1.3.3 no GitHub.
Requer: GITHUB_TOKEN environment variable com permissão para write contents em releases.
"""

import os
import sys
import requests
from pathlib import Path

# Configuração
GITHUB_OWNER = "ItaloNicacioDev"
GITHUB_REPO = "Translate_VN"
RELEASE_TAG = "v1.3.3"
INSTALLER_PATH = Path(__file__).parent / "Output" / "TranslateVN-Setup.exe"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ ERRO: GITHUB_TOKEN não configurado")
    print("   Configure via: set GITHUB_TOKEN=seu_token_aqui")
    sys.exit(1)

if not INSTALLER_PATH.exists():
    print(f"❌ ERRO: {INSTALLER_PATH} não encontrado")
    sys.exit(1)

# Headers para autenticação
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 1. Procura a release
print(f"🔍 Procurando release {RELEASE_TAG}...")
resp = requests.get(
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}",
    headers=headers
)

if resp.status_code == 404:
    print(f"❌ Release {RELEASE_TAG} não encontrada")
    sys.exit(1)
elif resp.status_code != 200:
    print(f"❌ Erro ao procurar release: {resp.status_code}")
    print(resp.text)
    sys.exit(1)

release = resp.json()
upload_url = release["upload_url"].replace("{?name,label}", "")

# 2. Verifica se asset já existe
asset_name = INSTALLER_PATH.name
existing_asset = next((a for a in release["assets"] if a["name"] == asset_name), None)

if existing_asset:
    print(f"⚠️  Asset {asset_name} já existe. Deletando...")
    resp = requests.delete(
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/assets/{existing_asset['id']}",
        headers=headers
    )
    if resp.status_code != 204:
        print(f"❌ Erro ao deletar asset: {resp.status_code}")
        sys.exit(1)

# 3. Upload do arquivo
print(f"📤 Fazendo upload de {asset_name}...")
with open(INSTALLER_PATH, "rb") as f:
    files = {"file": (asset_name, f, "application/octet-stream")}
    
    resp = requests.post(
        f"{upload_url}?name={asset_name}",
        headers={**headers, "Content-Type": "application/octet-stream"},
        data=f.read()
    )

if resp.status_code == 201:
    asset = resp.json()
    print(f"✅ Upload bem-sucedido!")
    print(f"   Asset ID: {asset['id']}")
    print(f"   URL: {asset['browser_download_url']}")
    print(f"\n✅ Release {RELEASE_TAG} pronta para usar!")
    sys.exit(0)
else:
    print(f"❌ Erro no upload: {resp.status_code}")
    print(resp.text)
    sys.exit(1)
