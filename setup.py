from setuptools import setup

APP = ['main.py']  # ВНИМАНИЕ: на скриншоте ваш файл называется main.py, а не mosaic_app.py
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'Minecraft Mosaic Maker',
        'CFBundleDisplayName': 'Minecraft Mosaic Maker',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.minecraft.mosaic.mac',
        'NSRequiresAquaSystemAppearance': False,
    },
    'packages': ['PIL', 'numpy'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    # Параметр setup_requires полностью удален, чтобы не было ошибки fetch_build_eggs
)
