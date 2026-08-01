; installer.iss
;
; Script do Inno Setup para o Translate VN (versao GUI).
; Empacota a pasta gerada pelo PyInstaller (--onedir) num unico
; instalador (Setup.exe), com atalhos de Area de Trabalho e Menu
; Iniciar usando o icone correto, e desinstalador.
;
; Requer Inno Setup 6 instalado: https://jrsoftware.org/isdl.php
; Compilar com: ISCC.exe installer.iss  (o build_gui.bat ja faz isso)

; MyAppVersion pode vir de fora via "ISCC.exe /DMyAppVersion=1.2.3
; installer.iss" -- e' o que build_gui.bat faz automaticamente,
; lendo o arquivo VERSION da raiz do projeto (fonte unica junto
; com core/version.py). O valor abaixo so' e' usado se ISCC.exe
; for chamado sem esse parametro.
#ifndef MyAppVersion
  #define MyAppVersion "0.3.0"
#endif
#define MyAppName "Translate VN"
#define MyAppPublisher "Translate VN"
#define MyAppExeName "TranslateVN-GUI.exe"
; Precisa bater com o nome do mutex criado em gui_main.py
; (_register_app_mutex) -- e' assim que o Inno Setup consegue
; detectar e fechar/reabrir o app sozinho durante uma atualizacao
; silenciosa (CloseApplications/RestartApplications abaixo).
#define MyAppMutex "TranslateVNAppMutex"

[Setup]
AppId={{B7B2C9A0-6C7B-4E9F-9C2F-6E6F1B7B0A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppMutex={#MyAppMutex}
; Fecha o Translate VN sozinho se ele estiver aberto durante a
; instalacao (update in-place) e reabre ele no final -- e' o que o
; updater interno do app usa (junto com os parametros de linha de
; comando /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS em
; core/updater.py) pra se auto-atualizar sem o usuario precisar
; fechar o programa manualmente.
CloseApplications=yes
RestartApplications=yes
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=TranslateVN-Setup
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\TranslateVN-GUI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Instalacao manual/interativa: oferece o checkbox normal "abrir
; o programa" no fim do wizard (pulado automaticamente se rodar
; silencioso, por causa de "skipifsilent").
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
; Auto-atualizacao silenciosa (disparada de dentro do proprio app,
; ver core/updater.py): reabre o Translate VN sozinho ao terminar,
; sem precisar de nenhum clique -- so' roda quando o Setup for
; executado com /VERYSILENT (WizardSilent = True).
Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall; Check: WizardSilent
