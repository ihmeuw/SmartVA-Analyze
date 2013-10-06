# -*- mode: python -*-
a = Analysis(['src/vaUI.py'],
             pathex=['Z:\\ihme-va'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
for d in a.datas:
  if 'pyconfig' in d[0]:
    a.datas.remove(d)
    break
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
    		  [('res\\logo.png', 'Z:\\ihme-va\\src\\res\\logo.png', 'DATA')],
    		  [('res\\help.html', 'Z:\\ihme-va\\src\\res\\help.html', 'DATA')],
    		  [('tariffs-adult.csv', 'Z:\\ihme-va\\src\\tariffs-adult.csv', 'DATA')],
    		  [('tariffs-child.csv', 'Z:\\ihme-va\\src\\tariffs-child.csv', 'DATA')],
    		  [('tariffs-neonate.csv', 'Z:\\ihme-va\\src\\tariffs-neonate.csv', 'DATA')],
    		  [('validated-adult.csv', 'Z:\\ihme-va\\src\\validated-adult.csv', 'DATA')],
    		  [('validated-child.csv', 'Z:\\ihme-va\\src\\validated-child.csv', 'DATA')],
    		  [('validated-neonate.csv', 'Z:\\ihme-va\\src\\validated-neonate.csv', 'DATA')],
          [('adult_undetermined_weights-hce0.csv', 'Z:\\ihme-va\\src\\adult_undetermined_weights-hce0.csv', 'DATA')],
          [('adult_undetermined_weights-hce1.csv', 'Z:\\ihme-va\\src\\adult_undetermined_weights-hce1.csv', 'DATA')],
          [('child_undetermined_weights-hce0.csv', 'Z:\\ihme-va\\src\\child_undetermined_weights-hce0.csv', 'DATA')],
          [('child_undetermined_weights-hce1.csv', 'Z:\\ihme-va\\src\\child_undetermined_weights-hce1.csv', 'DATA')],
          [('neonate_undetermined_weights-hce0.csv', 'Z:\\ihme-va\\src\\neonate_undetermined_weights-hce0.csv', 'DATA')],
          [('neonate_undetermined_weights-hce1.csv', 'Z:\\ihme-va\\src\\neonate_undetermined_weights-hce1.csv', 'DATA')],
          name='SmartVA.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False,icon='pkg\\icon.ico')
