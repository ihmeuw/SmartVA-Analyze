from __future__ import print_function
import os
import itertools
import sys
import warnings

import pandas as pd


warnings.simplefilter('ignore', pd.io.common.DtypeWarning)


def diff(path1, path2):
    """
    Pass the output directory of two SmartVA runs and verify either cell
    in all files are identical.
    """
    modules = ['adult', 'child', 'neonate']
    main_files = ['csmf', 'predictions']
    for module, f in itertools.product(modules, main_files):
        filename = '{}-{}.csv'.format(module, f)
        p1 = os.path.join(path1, filename)
        p2 = os.path.join(path2, filename)
        if os.path.exists(p1) or os.path.exists(p2):
            print('Checking {}..'.format(filename), end=' ')
            df1 = pd.read_csv(p1)
            df2 = pd.read_csv(p2)
            if f == 'predictions':
                assert (df1.fillna('') == df2.fillna('')).all().all()
            if f == 'csmf':
                # CSMF order is not guaranteed. 
                csmf1 = dict(zip(df1.cause, df1.CSMF))
                csmf2 = dict(zip(df2.cause, df2.CSMF))
                assert csmf1 == csmf2
            print('Good.')

    for module in modules:
        cutoffs_file1 = os.path.join(path1, 'intermediate-files',
                                     '{}-cutoffs.txt'.format(module))
        cutoffs_file2 = os.path.join(path2, 'intermediate-files',
                                     '{}-cutoffs.txt'.format(module))
        if os.path.exists(cutoffs_file1) or os.path.exists(cutoffs_file2):
            print('Checking {} cutoffs..'.format(module), end=' ')
            with open(cutoffs_file1) as f:
                cutoffs1 = dict([line.split(' : ') for line in f])
            with open(cutoffs_file2) as f:
                cutoffs2 = dict([line.split(' : ') for line in f])
            assert cutoffs1 == cutoffs2
            print('Good.')

    intermediate_files = [
        'prepped',
        'presymptom',
        'logic-rules',
        'symptom',
        'tariff-scores',
        'external-ranks',
        'tariff-ranks',
    ]
    for module, f in itertools.product(modules, intermediate_files):
        filename = '{}-{}.csv'.format(module, f)
        p1 = os.path.join(path1, 'intermediate-files', filename)
        p2 = os.path.join(path2, 'intermediate-files', filename)
        if os.path.exists(p1) or os.path.exists(p2):
            print('Checking {}..'.format(filename), end=' ')
            df1 = pd.read_csv(p1)
            df2 = pd.read_csv(p2)
            assert (df1.fillna('') == df2.fillna('')).all().all()
            print('Good.')

    print('No differences.')


if __name__ == '__main__':
    diff(sys.argv[1], sys.argv[2])
