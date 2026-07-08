; installer.iss
;
; Script do Inno Setup para o Translate VN (versao GUI).
; Empacota a pasta gerada pelo PyInstaller (--onedir) num unico
; instalador (Setup.exe), com atalhos de Area de Trabalho e Menu
; Iniciar usando o icone correto, e desinstalador.
;
; Requer Inno Setup 6 instalado: https://jrsoftware.org/isdl.php
; Compilar com: ISCC.exe installer.iss  (o build_gui.bat ja faz isso)

#define MyAppName "Translate VN"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "Translate VN"
#define MyAppExeName "TranslateVN-GUI.exe"

[Setup]
AppId={{B7B2C9A0-6C7B-4E9F-9C2F-6E6F1B7B0A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
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
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
