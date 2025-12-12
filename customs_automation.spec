# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Customs Barcode Automation

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files
datas = [
    ('config.ini.sample', '.'),
    ('README.md', '.'),
    ('USER_GUIDE.md', '.'),
    ('Logo.png', '.'),  # Include logo for branding
]

# Collect hidden imports
hiddenimports = [
    'pyodbc',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome',
    'selenium.webdriver.edge',
    'selenium.webdriver.common',
    'selenium.webdriver.support',
    'requests',
    'cryptography',
    'cryptography.fernet',
    'apscheduler',
    'apscheduler.schedulers',
    'apscheduler.schedulers.background',
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'sqlite3',
    'configparser',
    'logging',
    'logging.handlers',
    'datetime',
    'xml.etree.ElementTree',
    # Barcode generation libraries - CRITICAL for PDF barcode rendering
    'barcode',
    'barcode.codex',      # Contains Code128, Code39 classes - Code39 used for ECUS style
    'barcode.base',
    'barcode.writer',
    'barcode.codabar',
    'barcode.ean',
    'barcode.isxn',
    'barcode.itf',
    'barcode.upc',
    'barcode.errors',     # Barcode error classes
    'barcode.charsets',   # Character sets for barcodes
    # ReportLab PDF generation
    'reportlab',
    'reportlab.lib',
    'reportlab.lib.colors',
    'reportlab.lib.pagesizes',
    'reportlab.lib.units',
    'reportlab.lib.styles',
    'reportlab.lib.enums',
    'reportlab.platypus',
    'reportlab.platypus.doctemplate',
    'reportlab.platypus.paragraph',
    'reportlab.platypus.tables',
    'reportlab.platypus.flowables',
    'reportlab.pdfbase',
    'reportlab.pdfbase.ttfonts',
    'reportlab.pdfbase.pdfmetrics',
    'reportlab.graphics',
    'reportlab.graphics.shapes',
    # PIL/Pillow for barcode image generation
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageOps',
    'PIL.ImageFilter',
    # IO modules for barcode buffer
    'io',
]

# Add all submodules from the application
hiddenimports += collect_submodules('config')
hiddenimports += collect_submodules('database')
hiddenimports += collect_submodules('processors')
hiddenimports += collect_submodules('web_utils')
hiddenimports += collect_submodules('file_utils')
hiddenimports += collect_submodules('scheduler')
hiddenimports += collect_submodules('models')
hiddenimports += collect_submodules('logging_system')
hiddenimports += collect_submodules('error_handling')
hiddenimports += collect_submodules('gui')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'hypothesis', 'test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CustomsAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Logo.png',  # Company logo as application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CustomsAutomation',
)
