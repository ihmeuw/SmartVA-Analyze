# -*- mode: python -*-

block_cipher = None

a = Analysis(
    ['src/smartva/va_cli.py'],
    pathex=["src/"],
    cipher=block_cipher,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [('data/tariffs-adult.csv', 'src/smartva/data/tariffs-adult.csv', 'DATA')],
    [('data/tariffs-adult.csv', 'src/smartva/data/tariffs-adult.csv', 'DATA')],
    [('data/tariffs-child.csv', 'src/smartva/data/tariffs-child.csv', 'DATA')],
    [('data/tariffs-neonate.csv', 'src/smartva/data/tariffs-neonate.csv', 'DATA')],
    [('data/validated-adult.csv', 'src/smartva/data/validated-adult.csv', 'DATA')],
    [('data/validated-child.csv', 'src/smartva/data/validated-child.csv', 'DATA')],
    [('data/validated-neonate.csv', 'src/smartva/data/validated-neonate.csv', 'DATA')],
    [('data/chinese.json', 'src/smartva/data/chinese.json', 'DATA')],
    [('data/spanish.json', 'src/smartva/data/spanish.json', 'DATA')],
    [('data/adult_undetermined_weights.csv', 'src/smartva/data/adult_undetermined_weights.csv', 'DATA')],
    [('data/child_undetermined_weights.csv', 'src/smartva/data/child_undetermined_weights.csv', 'DATA')],
    [('data/neonate_undetermined_weights.csv', 'src/smartva/data/neonate_undetermined_weights.csv', 'DATA')],
    [('res/SmartVA Analyze Output Interpretation Sheet.docx', 'src/smartva/res/SmartVA Analyze Output Interpretation Sheet.docx', 'DATA')],
    name='smartva',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    icon='pkg/icon.png',
)
