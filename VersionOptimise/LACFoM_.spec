# -*- mode: python -*-
from kivy.deps import sdl2, glew
block_cipher = None


a = Analysis(['C:\\Users\\laeti\\Documents\\2020\\LACFoM\\VersionOptimise\\main_gui.py'],
             pathex=['C:\\Users\\laeti\\Documents\\2020\\LACFoM\\VersionOptimise'],
             binaries=None,
             datas=[('C:\\Users\\laeti\\Documents\\2020\\LACFoM\\VersionOptimise\\*.py', '.'),],
             hiddenimports=['win32timezone','pkg_resources.py2_warn','textract.parsers.pptx_parser','textract.parsers.docx_parser'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='LACFoM',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='C:\\Users\\laeti\\Documents\\2020\\LACFoM\\VersionOptimise\\logo.ico')
coll = COLLECT(exe,
               Tree('C:\\Users\\laeti\\Documents\\2020\\LACFoM\\VersionOptimise\\data\\'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='LACFoM')
