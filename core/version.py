"""
version.py

Fonte unica da versao do aplicativo. Usada pela tela "Sobre",
pelo verificador de atualizacoes (core/updater.py) e, no build,
pelo installer.iss (via build_gui.bat, que le o arquivo VERSION
na raiz do projeto e passa pro Inno Setup).

IMPORTANTE: ao publicar uma nova versao...
  1. Atualize APP_VERSION abaixo.
  2. Atualize o arquivo VERSION (raiz do projeto) com o mesmo
     numero -- e' o que o build_gui.bat usa pra gerar o
     instalador com a versao certa.
  3. Rode build_gui.bat pra gerar Output\\TranslateVN-Setup.exe.
  4. No GitHub, crie uma tag "vX.Y.Z" e uma Release com esse
     nome, anexando TranslateVN-Setup.exe como asset.
     E' exatamente esse asset que o updater embutido no app
     (core/updater.py) encontra e baixa sozinho.
"""

APP_VERSION = "1.3.0"