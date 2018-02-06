from collections import Counter, defaultdict, OrderedDict
import csv
from datetime import datetime
import logging
import os
import re
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from smartva.loggers import status_logger, warning_logger
from smartva.data_prep import DataPrep
from smartva.data.common_data import (ADULT, CHILD, NEONATE)
from smartva.tariff_prep import safe_float, safe_int
from smartva.data.icds import ICDS
from smartva.data.gbd_causes import GBD_LEVEL1_CAUSE_NAMES, GBD_LEVEL1_CAUSES
from smartva.data import codebook
from smartva.data.adult_tariff_data import CAUSES as ADULT_CAUSES
from smartva.data.child_tariff_data import CAUSES as CHILD_CAUSES
from smartva.data.neonate_tariff_data import CAUSES as NEONATE_CAUSES

FOLDER1 = '1-individual-cause-of-death'
FOLDER2 = '2-csmf'
FOLDER3 = '3-graphs-and-tables'
FOLDER4 = '4-monitoring-and-quality'

MODULES = (ADULT, CHILD, NEONATE)
SYMPTOMS_RE = re.compile('^s\d+$')

AGE_GROUPS = OrderedDict([
    ('neonate1', '0-7 days'),
    ('neonate2', '8-28 days'),
    ('child1', '29 days - <1 year'),
    ('child2', '1-4 years'),
    ('child3', '5-11 years'),
    ('adult1', '12-19 years')
])
for d in range(2, 8):
    AGE_GROUPS['adult{}'.format(d)] = '{d}0-{d}9 years'.format(d=d)
AGE_GROUPS['adult8'] = '80+'

CAUSE_NUMBERS = {
    ADULT: {v: k for k, v in ADULT_CAUSES.items()},
    CHILD: {v: k for k, v in CHILD_CAUSES.items()},
    NEONATE: {v: k for k, v in NEONATE_CAUSES.items()},
}


class OutputPrep(DataPrep):

    def __init__(self, working_dir_path, reorganize=True, keep_orig=False):
        super(OutputPrep, self).__init__(working_dir_path, None)
        self.reorganize = reorganize
        self.keep_orig = keep_orig

    def run(self):
        if self.reorganize:
            status_logger.info('Preparing output files.')
            for folder in (FOLDER1, FOLDER2, FOLDER3, FOLDER4):
                self.make_dir(self.working_dir_path, folder)

            self.organize_folder1()
            self.organize_folder2()
            self.organize_folder3()
            self.organize_folder4()
        if not self.keep_orig:
            self.clean_up()

    def predictions_file(self, module):
        return os.path.join(self.working_dir_path,
                            '{:s}-predictions.csv'.format(module))

    @staticmethod
    def make_dir(*args):
        path = os.path.join(*args)
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:
                pass

    def organize_folder1(self):
        """Folder 1: Individual cause of death

        Contains:
            - individual predictions for all records
                * extra columns for names
                * extra columns for geography
                * extra column with ICD10
                * extra columns with date of birth
                * extra columns with date of interview
            - multiple predictions for all records
                * unmodified concatenated likelihoods files
        """
        self._format_predictions_file()
        # TODO: consider saving likelihoods excel file (but only if asked to)
        self._concatenate_likelihoods_files()

    def _format_predictions_file(self):
        # Instead of hackishly carrying extra columns through each step, we're
        # going to hackishly merge the columns we want back on at the end. This
        # makes use of the fact that the row ordering in the prepped files is
        # the same as the row order in the predictions.

        predictions_file = os.path.join(self.working_dir_path, FOLDER1,
                                        'individual-cause-of-death.csv')
        headers = ['sid', 'name1', 'name2', 'name3', 'name4', 'geography1',
                   'geography2', 'geography3', 'geography4', 'geography5',
                   'cause34', 'cause list #', 'icd10', 'age', 'sex',
                   'birth_date', 'death_date', 'interview_date']
        with open(predictions_file, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for module in MODULES:
                pred_file = self.predictions_file(module)
                raw_file = os.path.join(self.intermediate_dir,
                                        '{:s}-prepped.csv'.format(module))
                if not (os.path.exists(pred_file) and os.path.exists(raw_file)):
                    continue

                with open(pred_file, 'rb') as f_pred, open(raw_file, 'rb') as f_raw:
                    raw_reader = csv.DictReader(f_raw)
                    pred_reader = csv.DictReader(f_pred)
                    try:
                        while True:
                            raw_row = next(raw_reader)
                            pred_row = next(pred_reader)
                            birth_date = [raw_row.get('gen_5_1{}'.format(x))
                                          for x in 'abc']

                            death_date = [raw_row.get('gen_5_3{}'.format(x))
                                          for x in 'abc']

                            writer.writerow([
                                pred_row.get('sid'),
                                # TODO: finalize name/geography columns
                                raw_row.get('gen_5_0a'),  # Doesn't exist
                                raw_row.get('gen_5_0a2'),  # Doesn't exist
                                raw_row.get('gen_5_0'),
                                raw_row.get('gen_5_0c'),  # Doesn't exist
                                raw_row.get('gen_5_5a'),  # Doesn't exist
                                raw_row.get('gen_5_5b'),  # Doesn't exist
                                raw_row.get('gen_5_5c'),  # Doesn't exist
                                raw_row.get('gen_5_5d'),  # Doesn't exist
                                raw_row.get('gen_5_5e'),  # Doesn't exist
                                pred_row.get('cause34'),
                                pred_row.get('cause'),
                                ICDS[module].get(pred_row.get('cause34')),
                                self.add_age_unit(pred_row.get('age')),
                                pred_row.get('sex'),
                                self.make_date(*birth_date),
                                self.make_date(*death_date),
                                raw_row.get('interviewdate'),
                            ])
                    except StopIteration:
                        pass

    @staticmethod
    def make_date(year, month, day):
        try:
            year, month, day = map(float, (year, month, day))
        except (TypeError, ValueError):
            return ''
        if (1880 <= year <= datetime.now().year and 1 <= month <= 12 and
                1 <= day <= 31):
            return '{:d}-{:02d}-{:02d}'.format(*map(int, (year, month, day)))
        else:
            return ''

    @staticmethod
    def add_age_unit(age):
        try:
            age = float(age)
        except (TypeError, ValueError):
            return
        else:
            one_month = 30. / 365
            if age >= 1:
                age_scaled, unit = age, 'year'
            elif one_month <= age < 1:
                age_scaled, unit = age * 12, 'month'
            elif 0 <= age < one_month:
                age_scaled, unit = age * 365, 'day'

        plural = 's' if age_scaled != 1 else ''
        return '{} {}{}'.format(int(age_scaled), unit, plural)

    def _concatenate_likelihoods_files(self):
        likelihoods_file = os.path.join(self.working_dir_path, FOLDER1,
                                        'possible-predictions.csv')
        with open(likelihoods_file, 'wb') as out:
            first = True
            for module in MODULES:
                filename = os.path.join(self.working_dir_path,
                                        '{:s}-likelihoods.csv'.format(module))
                if not os.path.exists(filename):
                    continue

                with open(filename, 'rb') as f:
                    for i, row in enumerate(f):
                        if i == 0:
                            if first:
                                out.write(row)
                                first = False
                        else:
                            out.write(row)

    def organize_folder2(self):
        """Folder 2: CSMF

        Contains:
            - CSMF by module
                * extra column with ICD10 code
                * extra column with cause number
                * extra columns with CSMF stratified by sex
            - CSMF at GBD level 1 across all modules
        """
        # Spec is non-specific as to column layout and names
        for module in MODULES:
            self._reformat_csmf(module)
        self._aggregate_csmf_to_gbd_level1()

    def _reformat_csmf(self, module):
        keys = {
            module: 'both',
            '-'.join([module, 'male']): 'male',
            '-'.join([module, 'female']): 'female',
        }
        csmf = defaultdict(dict)
        for key, label in keys.items():
            filename = os.path.join(self.working_dir_path,
                                    '{}-csmf.csv'.format(key))
            if not os.path.exists(filename):
                continue

            with open(filename) as f:
                for cause, value in csv.reader(f):
                    if cause != 'cause':   # skip header row
                        csmf[cause][label] = value

        table = [['cause34', 'cause list #', 'icd10', 'all', 'male', 'female']]
        for cause in sorted(csmf):
            table.append([
                cause,
                CAUSE_NUMBERS[module].get(cause),
                ICDS[module].get(cause),
                round(safe_float(csmf[cause].get('both', 0)), 3),
                round(safe_float(csmf[cause].get('male', 0)), 3),
                round(safe_float(csmf[cause].get('female', 0)), 3),
            ])

        filename = os.path.join(self.working_dir_path, FOLDER2,
                                '{}-csmf.csv'.format(module))
        with open(filename, 'wb') as f:
            csv.writer(f).writerows(table)

    def _aggregate_csmf_to_gbd_level1(self):
        gbd_counts = Counter()
        for module in MODULES:
            filename = os.path.join(self.working_dir_path,
                                    '{}-predictions.csv'.format(module))
            if not os.path.exists(filename):
                continue

            with open(filename) as f:
                gbd_counts.update([
                    GBD_LEVEL1_CAUSES[module][row['cause34']]
                    for row in csv.DictReader(f)
                ])

        # silly py2 and your integer division
        total = float(sum(gbd_counts.values()))

        table = [['cause', 'cause_name', 'CSMF']]
        table.extend([
            [cause, GBD_LEVEL1_CAUSE_NAMES[cause], round(value / total, 3)]
            for cause, value in sorted(gbd_counts.items(), key=lambda x: x[0])
        ])

        filename = os.path.join(self.working_dir_path, FOLDER2,
                                'gbd-level1-csmf.csv')
        with open(filename, 'wb') as f:
            csv.writer(f).writerows(table)
        self.gbd_csmf = table

    def organize_folder3(self):
        """Folder 3: Graphs and Tables

        Contains:
            - CSMF bar graphs by module
            - Adult CSMF bar graphs by sex
            - All-cause CSMF bar graph by age and sex
            - Undetermined bar graph by age and sex
            - GBD CSMF pie chart
            - Table of CSMF by cause, age group, and sex
        """
        self._save_graphs()
        self._write_csmf_table()
        self._graph_gbd_csmf()

    def _save_graphs(self):
        files = ['all-figure.png', 'undetermined-figure.png',
                 'adult-female-csmf-figure.png', 'adult-male-csmf-figure.png']
        for module in MODULES:
            files.append('{:s}-csmf-figure.png'.format(module))

        for f in files:
            src = os.path.join(self.working_dir_path, 'figures', f)
            if os.path.exists(src):
                shutil.copy2(src,
                             os.path.join(self.working_dir_path, FOLDER3, f))

    def _graph_gbd_csmf(self):
        data = self.gbd_csmf[1:]  # drop headers
        values = [row[2] for row in data]

        def wrap(x):
            if x.startswith('Comm'):
                return x.replace(', neo', ',\nneo')
            else:
                return x
        labels = [wrap(row[1]) for row in data]
        color_map = {
            'A': 'red',
            'B': 'blue',
            'C': 'green',
            'X': 'grey'
        }
        colors = [color_map[row[0]] for row in data]

        plt.ioff()   # turn off interactive mode
        fig, ax = plt.subplots()
        patches, texts, autotexts = ax.pie(values, labels=labels, colors=colors,
                                           autopct='%1.1f%%')
        for t in texts:
            t.set_fontsize(9)
        ax.axis('equal')   # force aspect ratio so chart is circular
        plt.subplots_adjust(left=0.3, right=0.7)
        filename = 'gbd-level1-csmf.png'
        fig.savefig(os.path.join(self.working_dir_path, FOLDER3, filename),
                    dpi=150)

        plt.close()

    def _write_csmf_table(self):
        sex_names = OrderedDict([(1, 'Male'), (2, 'Female'), (9, 'Missing')])

        counts = defaultdict(int)
        causes = defaultdict(set)
        for module in MODULES:

            filename = self.predictions_file(module)
            if not os.path.exists(filename):
                continue

            with open(filename, 'r') as f:
                for row in csv.DictReader(f):
                    age_group = self.bin_ages(module, safe_float(row['age']))
                    sex = sex_names.get(safe_int(row['sex']), 'Missing')
                    cause = row['cause34']
                    causes[module].add(cause)
                    counts[(age_group, sex, cause)] += 1

        # It's times like this where you really start to appreciate a
        # high-level dataframe abstraction. Isn't it?
        table = [['module', 'cause34', 'age', 'sex', 'counts']]
        for age_i, age_group in AGE_GROUPS.items():
            module = age_i[:-1]
            for sex in sex_names.values():
                for cause in sorted(causes[module]):
                    count = counts[(age_group, sex, cause)]
                    if count:
                        table.append([module, cause, age_group, sex, count])

        filename = os.path.join(self.working_dir_path, FOLDER3,
                                'causes-of-death.csv')
        with open(filename, 'wb') as f:
            csv.writer(f).writerows(table)
        return table

    @staticmethod
    def bin_ages(module, age):
        if module == NEONATE:
            if age < 7 / float(365):
                return AGE_GROUPS['neonate1']
            else:
                return AGE_GROUPS['neonate2']
        elif module == CHILD:
            if age < 1:
                return AGE_GROUPS['child1']
            elif 1 <= age < 5:
                return AGE_GROUPS['child2']
            elif age >= 5:
                return AGE_GROUPS['child3']
        elif module == ADULT:
            if age < 20:
                return AGE_GROUPS['adult1']
            elif age >= 80:
                return AGE_GROUPS['adult8']
            else:
                return AGE_GROUPS['adult{}'.format(int(age / 10))]

    def organize_folder4(self):
        """Folder 4: Monitoring and Quality

        Contains:
            - Report file (output from warning_logger)
            - Raw data files by module
            - Symptom files by module (unmodified)
            - Tariff scores files by module (unmodified)
            - Endorsement rates of symptoms by cause by module
        """
        shutil.copy2(
            os.path.join(self.working_dir_path, 'warnings.txt'),
            os.path.join(self.working_dir_path, FOLDER4, 'report.txt')
        )

        for module in MODULES:
            self._recode_prepped_files(module)
            self._copy_intermediate_files(module)
            self._write_endorsement_rates(module)

    def _recode_prepped_files(self, module):
        prepped_file = os.path.join(self.intermediate_dir,
                                    '{}-prepped.csv'.format(module))
        recoded_file = os.path.join(self.working_dir_path, FOLDER4,
                                    '{}-raw-data.csv'.format(module))
        if not os.path.exists(prepped_file):
            return

        with open(prepped_file, 'rb') as f_prep, open(recoded_file, 'wb') as f_rec:
            reader = csv.DictReader(f_prep)
            writer = csv.DictWriter(f_rec, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                for key, value in row.items():
                    value = safe_int(value)
                    if key in codebook.YES_NO_QUESTIONS:
                        row[key] = codebook.YES_NO_LABELS.get(value)
                    elif key in codebook.DURATION_CATEORICALS:
                        row[key] = codebook.DURATION_LABELS.get(value)
                    elif key in codebook.WORD_COLUMNS:
                        row[key] = codebook.WORD_LABELS.get(value)
                    elif key in codebook.CATEGORICAL_LABELS:
                        row[key] = codebook.CATEGORICAL_LABELS[key].get(value)
                writer.writerow(row)

    def _copy_intermediate_files(self, module):
        files = ('{:s}-symptom.csv', '{:s}-tariff-scores.csv')
        files = [f.format(module) for f in files]
        for f in files:
            src = os.path.join(self.intermediate_dir, f)
            if os.path.exists(src):
                shutil.copy2(src,
                             os.path.join(self.working_dir_path, FOLDER4, f))

    def _write_endorsement_rates(self, module):
        """Calculate endorsement rates by predicted cause for a module."""
        symptom_file = os.path.join(self.intermediate_dir,
                                    '{}-symptom.csv'.format(module))
        prediction_file = self.predictions_file(module)
        if not (os.path.exists(symptom_file) and os.path.exists(prediction_file)):
            return

        with open(symptom_file) as f_symp, open(prediction_file) as f_pred:
            symp_reader = csv.DictReader(f_symp)
            pred_reader = csv.DictReader(f_pred)
            symptoms = [header for header in symp_reader.fieldnames
                        if SYMPTOMS_RE.match(header)]

            counts = Counter()
            endorsements = defaultdict(Counter)

            # We don't guarantee that the row ID (sid) is unique
            # It's actually safer to merge positionally
            try:
                while True:
                    symp_row = next(symp_reader)
                    pred_row = next(pred_reader)

                    # We're going to use the cause strings instead of the cause
                    # numbers as headers for this file. The predictions are at
                    # the aggregated level and the numbers may be different
                    # from the column headers of the other files in this folder
                    cause = pred_row['cause34']

                    counts.update([cause])
                    for symptom in symptoms:
                        if safe_float(symp_row[symptom]):
                            endorsements[cause].update([symptom])
            except StopIteration:
                pass

        # Transpose "dataframe". This allows us to write data by row
        # We also want to preserve the order of the symptoms, just in case
        data = OrderedDict(
            (symp, {cause: endorsements[cause].get(symp, 0) / float(total)
                    for cause, total in counts.items() if total})
            for symp in symptoms
        )
        causes = sorted(counts)
        filename = os.path.join(self.working_dir_path, FOLDER4,
                                '{}-endorsement-rates.csv'.format(module))
        headers = ['symptom']
        headers.extend(causes)
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for symptom, rates in data.items():
                row = [symptom]
                # TODO: consider rounding. CSMF aren't rounded so maybe not...
                row.extend([rates[cause] * 100 for cause in causes])
                writer.writerow(row)

    def clean_up(self):
        """Remove all the original output files"""
        shutil.rmtree(os.path.join(self.working_dir_path, 'figures'),
                      ignore_errors=True)
        shutil.rmtree(self.intermediate_dir, ignore_errors=True)

        # We could glob, but let's be safe and only clean up files that we've
        # created in case the user put extra files in the output directory
        # while we weren't looking.
        files = ['warnings.txt']
        stubs = ('csmf.csv', 'likelihoods.csv', 'likelihoods.xlsx',
                 'predictions.csv', 'male-csmf.csv', 'female-csmf.csv')
        for module in MODULES:
            for stub in stubs:
                files.append('-'.join([module, stub]))

        # WindowsOS keeps a lock on the text file used as the destination
        # for the warning logger. If we try to remove the file while to
        # handler is still active, it throws an OSError which we catch and
        # ignore. Close the handler before trying to remove the log file
        for handler in warning_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

        for f in files:
            try:
                os.remove(os.path.join(self.working_dir_path, f))
            except (OSError, IOError):
                pass
