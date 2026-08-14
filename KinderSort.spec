# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

# Collect Python packages
for pkg in ("face_recognition", "face_recognition_models", "dlib"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Explicitly include face_recognition_models model files
model_dir = r"C:\xampp\htdocs\tutorial2\KinderSort\.venv\Lib\site-packages\face_recognition_models\models"

datas += [
    (
        model_dir,
        "face_recognition_models/models",
    )
]


a = Analysis(
    ["main.py"],
    pathex=[
        r"C:\xampp\htdocs\tutorial2\KinderSort"
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="KinderSort",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)