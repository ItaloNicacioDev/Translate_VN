@echo off
REM =====================================================
REM build.bat
REM Gera UM UNICO executavel: dist\TranslateVN.exe
REM Rode este arquivo dentro da pasta raiz do projeto
REM (Translate_VN-main), com o Python instalado no PATH.
REM =====================================================

setlocal

echo.
echo [0/5] Limpando builds antigos (evita nomes/arquivos velhos)...
if exist tools\unrpyc_master\build rmdir /s /q tools\unrpyc_master\build
if exist tools\unrpyc_master\dist rmdir /s /q tools\unrpyc_master\dist
if exist tools\unrpyc_master\unrpyc_master.spec del /q tools\unrpyc_master\unrpyc_master.spec
if exist unrpyc_master.exe del /q unrpyc_master.exe
if exist unrpyc_legacy.exe del /q unrpyc_legacy.exe
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist TranslateVN.spec del /q TranslateVN.spec

echo.
echo [1/5] Criando ambiente virtual de build (se ainda nao existir)...
if not exist build_env (
    python -m venv build_env
)
call build_env\Scripts\activate.bat

echo.
echo [2/5] Instalando dependencias...
pip install -r requirements.txt
pip install unrpa pyinstaller

echo.
echo [3/5] Compilando unrpyc (master)...
pushd tools\unrpyc_master
pyinstaller --onefile --name unrpyc_master unrpyc.py
popd
REM IMPORTANTE: o arquivo copiado abaixo mantem o nome
REM "unrpyc_master.exe" -- o hook_extract_tools.py agora aceita
REM qualquer nome, mas mantemos consistente por clareza.
copy /Y tools\unrpyc_master\dist\unrpyc_master.exe unrpyc_master.exe

REM Se voce tiver tambem a branch "legacy" do unrpyc baixada em
REM tools\unrpyc_legacy\unrpyc.py, descomente as linhas abaixo:
REM pushd tools\unrpyc_legacy
REM pyinstaller --onefile --name unrpyc_legacy unrpyc.py
REM popd
REM copy /Y tools\unrpyc_legacy\dist\unrpyc_legacy.exe unrpyc_legacy.exe

echo.
echo [4/5] Compilando o app principal (com unrpyc embutido)...
pyinstaller --onefile --console --name TranslateVN ^
  --add-binary "unrpyc_master.exe;tools\unrpyc_master" ^
  --runtime-hook hook_extract_tools.py ^
  main.py

REM Se compilou o legacy tambem, use este comando no lugar do acima:
REM pyinstaller --onefile --console --name TranslateVN ^
REM   --add-binary "unrpyc_master.exe;tools\unrpyc_master" ^
REM   --add-binary "unrpyc_legacy.exe;tools\unrpyc_legacy" ^
REM   --runtime-hook hook_extract_tools.py ^
REM   main.py

echo.
echo [5/5] Pronto! Executavel final em: dist\TranslateVN.exe
echo Distribua APENAS esse arquivo. Na primeira execucao ele
echo mesmo cria a pasta "tools" do lado dele.
echo.

endlocal
