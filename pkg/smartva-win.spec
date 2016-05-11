# -*- mode: python -*-

a = Analysis(['src/vaUI.py'],
	hiddenimports=None,
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
          [('res/logo.png', 'src/res/logo.png', 'DATA')],
          [('res/about.html', 'src/res/about.html', 'DATA')],
          [('res/documentation.htm', 'src/res/documentation.htm', 'DATA')],
          [('res/documentation_files/image001.png', 'src/res/documentation_files/image001.png', 'DATA')],
          [('res/documentation_files/image002.png', 'src/res/documentation_files/image002.png', 'DATA')],
          [('res/documentation_files/image003.jpg', 'src/res/documentation_files/image003.jpg', 'DATA')],
          [('res/documentation_files/image004.png', 'src/res/documentation_files/image004.png', 'DATA')],
          [('res/documentation_files/image005.jpg', 'src/res/documentation_files/image005.jpg', 'DATA')],
          [('res/documentation_files/image006.jpg', 'src/res/documentation_files/image006.jpg', 'DATA')],
          [('res/documentation_files/image007.jpg', 'src/res/documentation_files/image007.jpg', 'DATA')],
          [('res/documentation_files/image008.jpg', 'src/res/documentation_files/image008.jpg', 'DATA')],
          [('res/documentation_files/image009.jpg', 'src/res/documentation_files/image009.jpg', 'DATA')],
          [('res/documentation_files/image010.png', 'src/res/documentation_files/image010.png', 'DATA')],
          [('res/documentation_files/image011.jpg', 'src/res/documentation_files/image011.jpg', 'DATA')],
          [('res/documentation_files/image012.png', 'src/res/documentation_files/image012.png', 'DATA')],
          [('tariffs-adult.csv', 'src/tariffs-adult.csv', 'DATA')],
          [('tariffs-child.csv', 'src/tariffs-child.csv', 'DATA')],
          [('tariffs-neonate.csv', 'src/tariffs-neonate.csv', 'DATA')],
          [('validated-adult.csv', 'src/validated-adult.csv', 'DATA')],
          [('validated-child.csv', 'src/validated-child.csv', 'DATA')],
          [('validated-neonate.csv', 'src/validated-neonate.csv', 'DATA')],
          [('adult_undetermined_weights-hce0.csv', 'src/adult_undetermined_weights-hce0.csv', 'DATA')],
          [('adult_undetermined_weights-hce1.csv', 'src/adult_undetermined_weights-hce1.csv', 'DATA')],
          [('child_undetermined_weights-hce0.csv', 'src/child_undetermined_weights-hce0.csv', 'DATA')],
          [('child_undetermined_weights-hce1.csv', 'src/child_undetermined_weights-hce1.csv', 'DATA')],
          [('neonate_undetermined_weights-hce0.csv', 'src/neonate_undetermined_weights-hce0.csv', 'DATA')],
          [('neonate_undetermined_weights-hce1.csv', 'src/neonate_undetermined_weights-hce1.csv', 'DATA')],
          name='SmartVA.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False,icon='pkg/icon.ico')
