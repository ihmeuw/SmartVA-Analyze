# -*- mode: python -*-
a = Analysis(['smartva/va_cli.py'],
             hiddenimports=None,
             hookspath=['pkg/hooks'],
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
          [('res/logo.png', 'smartva/res/logo.png', 'DATA')],
          [('res/favicon.ico', 'smartva/res/favicon.ico', 'DATA')],
          [('res/about.html', 'smartva/res/about.html', 'DATA')],
          [('res/documentation.htm', 'smartva/res/documentation.htm', 'DATA')],
          [('res/documentation_files/filelist.xml', 'smartva/res/documentation_files/filelist.xml','DATA')],
          [('res/documentation_files/colorschememapping.xml', 'smartva/res/documentation_files/colorschememapping.xml','DATA')],
          [('res/documentation_files/themedata.thmx', 'smartva/res/documentation_files/themedata.thmx','DATA')],
          [('res/documentation_files/image001.png', 'smartva/res/documentation_files/image001.png', 'DATA')],
          [('res/documentation_files/image002.png', 'smartva/res/documentation_files/image002.png', 'DATA')],
          [('res/documentation_files/image003.png', 'smartva/res/documentation_files/image003.png', 'DATA')],
          [('res/documentation_files/image004.png', 'smartva/res/documentation_files/image004.png', 'DATA')],
          [('res/documentation_files/image005.jpg', 'smartva/res/documentation_files/image005.jpg', 'DATA')],
          [('res/documentation_files/image006.jpg', 'smartva/res/documentation_files/image006.jpg', 'DATA')],
          [('res/documentation_files/image007.png', 'smartva/res/documentation_files/image007.png', 'DATA')],
          [('res/documentation_files/image008.png', 'smartva/res/documentation_files/image008.png', 'DATA')],
          [('res/documentation_files/image009.jpg', 'smartva/res/documentation_files/image009.jpg', 'DATA')],
          [('res/documentation_files/image010.jpg', 'smartva/res/documentation_files/image010.jpg', 'DATA')],
          [('res/documentation_files/image011.png', 'smartva/res/documentation_files/image011.png', 'DATA')],
          [('res/documentation_files/image012.jpg', 'smartva/res/documentation_files/image012.jpg', 'DATA')],
          [('res/documentation_files/image013.png', 'smartva/res/documentation_files/image013.png', 'DATA')],
          [('res/documentation_files/image014.jpg', 'smartva/res/documentation_files/image014.jpg', 'DATA')],
          [('res/documentation_files/image015.png', 'smartva/res/documentation_files/image015.png', 'DATA')],
          [('res/documentation_files/image016.jpg', 'smartva/res/documentation_files/image016.jpg', 'DATA')],
          [('res/documentation_files/image017.png', 'smartva/res/documentation_files/image017.png', 'DATA')],
          [('res/documentation_files/image018.jpg', 'smartva/res/documentation_files/image018.jpg', 'DATA')],
          [('res/documentation_files/image019.png', 'smartva/res/documentation_files/image019.png', 'DATA')],
          [('res/documentation_files/image020.jpg', 'smartva/res/documentation_files/image020.jpg', 'DATA')],
          [('res/documentation_files/image021.png', 'smartva/res/documentation_files/image021.png', 'DATA')],
          [('res/documentation_files/image022.jpg', 'smartva/res/documentation_files/image022.jpg', 'DATA')],
          [('res/documentation_files/image023.png', 'smartva/res/documentation_files/image023.png', 'DATA')],
          [('res/documentation_files/image024.png', 'smartva/res/documentation_files/image024.png', 'DATA')],
          [('res/documentation_files/image025.jpg', 'smartva/res/documentation_files/image025.jpg', 'DATA')],
          [('res/documentation_files/image026.png', 'smartva/res/documentation_files/image026.png', 'DATA')],
          [('res/documentation_files/image027.png', 'smartva/res/documentation_files/image027.png', 'DATA')],
          [('res/SmartVA Analyze Output Interpretation Sheet.docx', 'smartva/res/SmartVA Analyze Output Interpretation Sheet.docx', 'DATA')],
          [('data/tariffs-adult.csv', 'smartva/data/tariffs-adult.csv', 'DATA')],
          [('data/tariffs-adult.csv', 'smartva/data/tariffs-adult.csv', 'DATA')],
          [('data/tariffs-child.csv', 'smartva/data/tariffs-child.csv', 'DATA')],
          [('data/tariffs-neonate.csv', 'smartva/data/tariffs-neonate.csv', 'DATA')],
          [('data/validated-adult.csv', 'smartva/data/validated-adult.csv', 'DATA')],
          [('data/validated-child.csv', 'smartva/data/validated-child.csv', 'DATA')],
          [('data/validated-neonate.csv', 'smartva/data/validated-neonate.csv', 'DATA')],
          [('data/chinese.json', 'smartva/data/chinese.json', 'DATA')],
          [('data/spanish.json', 'smartva/data/spanish.json', 'DATA')],
          [('data/adult_undetermined_weights.csv', 'smartva/data/adult_undetermined_weights.csv', 'DATA')],
          [('data/child_undetermined_weights.csv', 'smartva/data/child_undetermined_weights.csv', 'DATA')],
          [('data/neonate_undetermined_weights.csv', 'smartva/data/neonate_undetermined_weights.csv', 'DATA')],
          name='SmartVA-Analyze-cli.exe',
          debug=False,
          strip=None,
          upx=False,
          console=True,
          icon='pkg/icon.ico')
