import PyInstaller.__main__ as m
m.run([
    r'--onefile', r'--name', r'unrpyc_master',
    r'tools\unrpyc_master\unrpyc.py',
])
