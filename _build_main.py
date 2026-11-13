import PyInstaller.__main__ as m
m.run([
    r'--onedir', r'--windowed', r'--name', r'TranslateVN-GUI',
    r'--icon', r'app_icon.ico',
    r'--add-binary', r'unrpyc_master.exe;tools\unrpyc_master',
    r'--add-data', r'ui;ui',
    r'--add-data', r'core;core',
    r'--add-data', r'engine;engine',
    r'--add-data', r'VERSION;.',
    r'--runtime-hook', r'hook_extract_tools.py',
    r'gui_main.py',
])
