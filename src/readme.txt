python pyinstaller.py -w ~/workspace/ihme-va/src/vaUI.py


c:\Documents and Settings\Administrator\Desktop\pyinstaller-2.0
python pyinstaller.py -w vaUI/vaUI.spec


edit ~/Desktop/pyinstaller-2.0/vaUI/vaUI.spec file to say:

# -*- mode: python -*-
a = Analysis(['c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\vaUI.py'],
             pathex=['C:\\Documents and Settings\\Administrator\\Desktop\\pyinstaller-2.0'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\vaUI', 'vaUI.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,

               a.binaries,
               a.zipfiles,
               a.datas,
			   [('res\\logo.png', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\res\\logo.png', 'DATA')],
               [('res\\help.html', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\res\\help.html', 'DATA')],
			   [('tariffs-adult.csv', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\tariffs-adult.csv', 'DATA')],
			   [('tariffs-child.csv', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\tariffs-child.csv', 'DATA')],
			   [('tariffs-neonate.csv', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\tariffs-neonate.csv', 'DATA')],
			   [('validated-adult.csv', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\validated-adult.csv', 'DATA')],
			   [('validated-child.csv', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\validated-child.csv', 'DATA')],
			   [('validated-neonate.csv', 'c:\\Documents and Settings\\Administrator\\Desktop\\ihme-va\\src\\validated-neonate.csv', 'DATA')],
               strip=None,
               upx=True,
               name=os.path.join('dist', 'vaUI'))
app = BUNDLE(coll,
             name=os.path.join('dist', 'vaUI.app'))
