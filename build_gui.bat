@echo off
REM =====================================================
REM build_gui.bat
REM Gera um instalador UNICO: Output\TranslateVN-Setup.exe
REM
REM Rode dentro da pasta raiz do projeto, ao lado de gui_main.py,
REM gui_api.py, app_icon.ico e installer.iss.
REM
REM Requer tambem o Inno Setup instalado (gratuito):
REM https://jrsoftware.org/isdl.php
REM =====================================================

setlocal

echo.
echo [0/7] Limpando builds antigos...
if not exist app_icon.ico (
    echo ERRO: app_icon.ico nao encontrado na raiz do projeto.
    echo Coloque o arquivo app_icon.ico ao lado deste build_gui.bat antes de continuar.
    exit /b 1
)
if not exist installer.iss (
    echo ERRO: installer.iss nao encontrado na raiz do projeto.
    echo Coloque o arquivo installer.iss ao lado deste build_gui.bat antes de continuar.
    exit /b 1
)
if exist tools\unrpyc_master\build rmdir /s /q tools\unrpyc_master\build
if exist tools\unrpyc_master\dist rmdir /s /q tools\unrpyc_master\dist
if exist tools\unrpyc_master\unrpyc_master.spec del /q tools\unrpyc_master\unrpyc_master.spec
if exist unrpyc_master.exe del /q unrpyc_master.exe
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Output rmdir /s /q Output
if exist TranslateVN-GUI.spec del /q TranslateVN-GUI.spec

echo.
echo [1/7] Criando/reaproveitando ambiente virtual de build...
if not exist build_env (
    python -m venv build_env
)
call build_env\Scripts\activate.bat

echo.
echo [2/7] Instalando dependencias (inclui pywebview)...
pip install -r requirements.txt
pip install unrpa pyinstaller pywebview

echo.
echo [3/7] Compilando unrpyc (master) -- pula se ja existir...
if not exist unrpyc_master.exe (
    pushd tools\unrpyc_master
    pyinstaller --onefile --name unrpyc_master unrpyc.py
    popd
    copy /Y tools\unrpyc_master\dist\unrpyc_master.exe unrpyc_master.exe
)

echo.
echo [4/7] Compilando o app GUI em modo pasta (--onedir)...
echo (--onedir nao tem o bug de icone que o --onefile tem em apps
echo  --windowed do PyInstaller; o instalador do Inno Setup e' quem
echo  vai entregar isso como 1 arquivo so' pro usuario final)
pyinstaller --onedir --windowed --name TranslateVN-GUI ^
  --icon "app_icon.ico" ^
  --add-binary "unrpyc_master.exe;tools\unrpyc_master" ^
  --add-data "ui;ui" ^
  --runtime-hook hook_extract_tools.py ^
  gui_main.py

if not exist "dist\TranslateVN-GUI\TranslateVN-GUI.exe" (
    echo ERRO: build do PyInstaller falhou, dist\TranslateVN-GUI\TranslateVN-GUI.exe nao existe.
    exit /b 1
)

echo.
echo [5/7] Procurando o compilador do Inno Setup (ISCC.exe)...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "E:\Documents\Inno Setup 6\ISCC.exe" set "ISCC=E:\Documents\Inno Setup 6\ISCC.exe"


if not defined ISCC (
    echo ERRO: Inno Setup nao encontrado.
    echo Baixe e instale gratuitamente em: https://jrsoftware.org/isdl.php
    echo Depois rode este build_gui.bat de novo.
    exit /b 1
)

echo Encontrado: %ISCC%

echo.
echo [6/7] Compilando o instalador com Inno Setup...
"%ISCC%" installer.iss

echo.
echo [7/7] Pronto! Instalador final em: Output\TranslateVN-Setup.exe
echo Distribua APENAS esse arquivo. Ele instala o app, cria os
echo atalhos com o icone certo e um desinstalador.
echo.

endlocal