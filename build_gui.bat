@echo off
REM =====================================================
REM build_gui.bat
REM Gera UM UNICO executavel: dist\TranslateVN-GUI.exe
REM Rode dentro da pasta raiz do projeto, ao lado de gui_main.py
REM e gui_api.py. Requer o mesmo build_env do build.bat (ou cria
REM um novo, se ainda nao existir).
REM =====================================================

setlocal

echo.
echo [0/5] Limpando builds antigos...
if exist tools\unrpyc_master\build rmdir /s /q tools\unrpyc_master\build
if exist tools\unrpyc_master\dist rmdir /s /q tools\unrpyc_master\dist
if exist tools\unrpyc_master\unrpyc_master.spec del /q tools\unrpyc_master\unrpyc_master.spec
if exist unrpyc_master.exe del /q unrpyc_master.exe
if exist build rmdir /s /q build
if exist dist\TranslateVN-GUI.exe del /q dist\TranslateVN-GUI.exe
if exist TranslateVN-GUI.spec del /q TranslateVN-GUI.spec

echo.
echo [1/5] Criando/reaproveitando ambiente virtual de build...
if not exist build_env (
    python -m venv build_env
)
call build_env\Scripts\activate.bat

echo.
echo [2/5] Instalando dependencias (inclui pywebview)...
pip install -r requirements.txt
pip install unrpa pyinstaller pywebview

echo.
echo [3/5] Compilando unrpyc (master) -- pula se ja existir...
if not exist unrpyc_master.exe (
    pushd tools\unrpyc_master
    pyinstaller --onefile --name unrpyc_master unrpyc.py
    popd
    copy /Y tools\unrpyc_master\dist\unrpyc_master.exe unrpyc_master.exe
)

echo.
echo [4/5] Compilando o app GUI (com unrpyc + ui/ embutidos)...
pyinstaller --onefile --windowed --name TranslateVN-GUI ^
  --add-binary "unrpyc_master.exe;tools\unrpyc_master" ^
  --add-data "ui;ui" ^
  --runtime-hook hook_extract_tools.py ^
  gui_main.py

echo.
echo [5/5] Pronto! Executavel final em: dist\TranslateVN-GUI.exe
echo Distribua APENAS esse arquivo. Na primeira execucao ele
echo mesmo cria a pasta "tools" do lado dele (igual a versao CLI).
echo.

endlocal
