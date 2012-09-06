python pyinstaller.py -w ~/workspace/ihme-va/src/vaUI.py

edit ~/Desktop/pyinstaller-2.0/vaUI/vaUI.spec file to say:

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               [('res/logo.png', '/Users/carlhartung/workspace/ihme-va/src/res/logo.png', 'DATA')],
               [('pkl/Adult_causelist_noHCE.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Adult_causelist_noHCE.pkl', 'DATA')],
               [('pkl/Adult_causelist.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Adult_causelist.pkl', 'DATA')],
               [('pkl/Adult_symptomlist_noHCE.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Adult_symptomlist_noHCE.pkl', 'DATA')],
               [('pkl/Adult_symptomlist.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Adult_symptomlist.pkl', 'DATA')],
               [('pkl/Child_causelist_noHCE.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Child_causelist_noHCE.pkl', 'DATA')],
               [('pkl/Child_causelist.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Child_causelist.pkl', 'DATA')],
               [('pkl/Child_symptomlist_noHCE.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Child_symptomlist_noHCE.pkl', 'DATA')],
               [('pkl/Child_symptomlist.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Child_symptomlist.pkl', 'DATA')],
               [('pkl/Neonate_causelist_noHCE.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Neonate_causelist_noHCE.pkl', 'DATA')],
               [('pkl/Neonate_causelist.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Neonate_causelist.pkl', 'DATA')],
               [('pkl/Neonate_rf.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Neonate_rf.pkl', 'DATA')],
               [('pkl/Neonate_symptomlist_noHCE.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Neonate_symptomlist_noHCE.pkl', 'DATA')],
               [('pkl/Neonate_symptomlist.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Neonate_symptomlist.pkl', 'DATA')],
               [('pkl/Neonate_tariff.pkl', '/Users/carlhartung/workspace/ihme-va/src/pkl/Neonate_tariff.pkl', 'DATA')],
               [('pkl/Child_available_symptoms.csv', '/Users/carlhartung/workspace/ihme-va/src/pkl/Child_available_symptoms.csv', 'DATA')],
               [('pkl/Adult_available_symptoms.csv', '/Users/carlhartung/workspace/ihme-va/src/pkl/Adult_available_symptoms.csv', 'DATA')],
               [('pkl/Neonate_available_symptoms.csv', '/Users/carlhartung/workspace/ihme-va/src/pkl/Neonate_available_symptoms.csv', 'DATA')],
               strip=None,
               upx=True,
               name=os.path.join('dist', 'vaUI'))

python pyinstaller.py -w ~/Desktop/pyinstaller-2.0/vaUI/vaUI.spec


