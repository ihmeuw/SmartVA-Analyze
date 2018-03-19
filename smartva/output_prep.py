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

from smartva.loggers import status_logger, warning_logger, REPORT_LOGGERS_NAMES
from smartva.data_prep import DataPrep
from smartva.data.common_data import (ADULT, CHILD, NEONATE)
from smartva.tariff_prep import safe_float, safe_int
from smartva.data.icds import ICDS
from smartva.data.gbd_causes import GBD_LEVEL1_CAUSE_NAMES, GBD_LEVEL1_CAUSES
from smartva.data import codebook
from smartva.data import (
    adult_tariff_data,
    child_tariff_data,
    neonate_tariff_data
)


FOLDER1 = '1-individual-cause-of-death'
FOLDER2 = '2-csmf'
FOLDER3 = '3-graphs-and-tables'
FOLDER4 = '4-monitoring-and-quality'
INTERMEDIATES_FOLDER = os.path.join(FOLDER4, 'intermediate-files')

MODULES = (ADULT, CHILD, NEONATE)
SYMPTOMS_RE = re.compile('^s\d+$')
INVALID_DATE_RE = re.compile('^[:.0]*$')


# The leading space in front of ages listed in days is a hack that forces the
# ASCII sort order of the strings to present values in the correct order. This
# was explicitly requested by the customer who is always right.
STILLBIRTH_AGE = ' 00 days'
AGE_GROUPS = OrderedDict([
    ('neonate0', STILLBIRTH_AGE),
    ('neonate1', ' 00-07 days'),
    ('neonate2', ' 08-28 days'),
    ('child1', ' 29 days - <1 year'),
    ('child2', '01-04 years'),
    ('child3', '05-11 years'),
    ('adult1', '12-19 years')
])
for d in range(2, 8):
    AGE_GROUPS['adult{}'.format(d)] = '{d}0-{d}9 years'.format(d=d)
AGE_GROUPS['adult8'] = '80+'

CAUSE_NUMBERS = {
    ADULT: {v: k for k, v in adult_tariff_data.CAUSES.items()},
    CHILD: {v: k for k, v in child_tariff_data.CAUSES.items()},
    NEONATE: {v: k for k, v in neonate_tariff_data.CAUSES.items()},
}

CAUSE46_NAMES = {
    ADULT: adult_tariff_data.CAUSES46,
    CHILD: child_tariff_data.CAUSES,
    NEONATE: neonate_tariff_data.CAUSES,
}

SYMPTOM_DESCRIPTIONS = {
    ADULT: adult_tariff_data.SYMPTOM_DESCRIPTIONS,
    CHILD: child_tariff_data.SYMPTOM_DESCRIPTIONS,
    NEONATE: neonate_tariff_data.SYMPTOM_DESCRIPTIONS,
}

SHORT_DROP_SYMPTOMS = {
    ADULT: adult_tariff_data.SHORT_FORM_DROP_LIST,
    CHILD: child_tariff_data.SHORT_FORM_DROP_LIST,
    NEONATE: neonate_tariff_data.SHORT_FORM_DROP_LIST,
}

HCE_DROP_SYMPTOMS = {
    ADULT: adult_tariff_data.HCE_DROP_LIST,
    CHILD: child_tariff_data.HCE_DROP_LIST,
    NEONATE: neonate_tariff_data.HCE_DROP_LIST,
}


class OutputPrep(DataPrep):

    def __init__(self, working_dir_path, reorganize=True, keep_orig=False,
                 short_form=False, free_text=True, hce=True):
        super(OutputPrep, self).__init__(working_dir_path, None)
        self.reorganize = reorganize
        self.keep_orig = keep_orig
        self.predictions = defaultdict(list)
        self.csmf = {module: defaultdict(int) for module in MODULES}
        self.short_form = short_form
        self.free_text = free_text
        self.hce = hce

    def run(self):
        if self.reorganize:
            status_logger.info('Preparing output files.')
            for folder in (FOLDER1, FOLDER2, FOLDER3, FOLDER4):
                self.make_dir(self.working_dir_path, folder)
            self.make_dir(self.working_dir_path, INTERMEDIATES_FOLDER)

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
            - module-specific predictions with the same columns
        """
        self._format_predictions_file()

    def _format_predictions_file(self):
        # Instead of hackishly carrying extra columns through each step, we're
        # going to hackishly merge the columns we want back on at the end. This
        # makes use of the fact that the row ordering in the prepped files is
        # the same as the row order in the predictions.

        predictions_file = os.path.join(self.working_dir_path, FOLDER1,
                                        'individual-cause-of-death.csv')
        headers = [
            'sid',
            'national_id',
            'name',
            'name2',
            'surname',
            'surname2',
            'geography1',
            'geography2',
            'geography3',
            'geography4',
            'geography5',
            'cause34',
            'cause list #',
            'icd10',
            'age',
            'sex',
            'birth_date',
            'death_date',
            'interview_date',
        ]
        with open(predictions_file, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for module in MODULES:
                pred_file = self.predictions_file(module)
                raw_file = os.path.join(self.intermediate_dir,
                                        '{:s}-prepped.csv'.format(module))
                if not (os.path.exists(pred_file) and os.path.exists(raw_file)):
                    continue

                module_file = os.path.join(self.working_dir_path, FOLDER1,
                                           '{}-predictions.csv'.format(module))

                with open(pred_file, 'rb') as f_pred, \
                        open(raw_file, 'rb') as f_raw, \
                        open(module_file, 'wb') as f_mod:
                    raw_reader = csv.DictReader(f_raw)
                    pred_reader = csv.DictReader(f_pred)
                    mod_writer = csv.writer(f_mod)
                    mod_writer.writerow(headers)
                    try:
                        while True:
                            raw_row = next(raw_reader)
                            pred_row = next(pred_reader)
                            self.predictions[module].append(pred_row)
                            birth_date = [raw_row.get('gen_5_1{}'.format(x))
                                          for x in 'abc']

                            death_date = [raw_row.get('gen_5_3{}'.format(x))
                                          for x in 'abc']

                            interview_date = raw_row.get('interviewdate', '')
                            # Remove any goofy dates that are all zeros
                            if INVALID_DATE_RE.match(interview_date):
                                interview_date = ''

                            row = [
                                pred_row.get('sid'),
                                raw_row.get('gen_6_7'),
                                raw_row.get('gen_5_0'),
                                raw_row.get('gen_5_0c'),  # Doesn't exist
                                raw_row.get('gen_5_0a'),  # Doesn't exist
                                raw_row.get('gen_5_0a2'),  # Doesn't exist
                                raw_row.get('gen_2_3a'),  # Doesn't exist
                                raw_row.get('gen_2_3b'),  # Doesn't exist
                                raw_row.get('gen_2_3c'),  # Doesn't exist
                                raw_row.get('gen_2_3d'),  # Doesn't exist
                                raw_row.get('gen_2_3e'),  # Doesn't exist
                                pred_row.get('cause34'),
                                pred_row.get('cause'),
                                ICDS[module].get(pred_row.get('cause34')),
                                pred_row.get('age'),
                                pred_row.get('sex'),
                                self.make_date(*birth_date),
                                self.make_date(*death_date),
                                interview_date,
                            ]
                            writer.writerow(row)
                            mod_writer.writerow(row)
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
        self._tabulate_all_age_csmf()
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
                        csmf[label][cause] = safe_float(value)

        self.csmf[module] = csmf
        table = [['cause34', 'cause list #', 'icd10', 'all', 'male', 'female']]
        for cause in sorted(csmf):
            table.append([
                cause,
                CAUSE_NUMBERS[module].get(cause),
                ICDS[module].get(cause),
                round(safe_float(csmf.get('both', {}).get(cause)), 3),
                round(safe_float(csmf.get('male', {}).get(cause)), 3),
                round(safe_float(csmf.get('female', {}).get(cause)), 3),
            ])

        filename = os.path.join(self.working_dir_path, FOLDER2,
                                '{}-csmf.csv'.format(module))
        with open(filename, 'wb') as f:
            csv.writer(f).writerows(table)

    def _tabulate_all_age_csmf(self):
        total = float(sum(len(v) for v in self.predictions.values()))
        if not total:
            return

        table = [['cause34', 'module', 'cause list #', 'icd10', 'all', 'male',
                  'female']]
        for module in MODULES:
            if module not in self.csmf:
                continue
            weight = len(self.predictions[module]) / total
            for cause in sorted(self.csmf[module]['both']):
                table.append([
                    cause,
                    module,
                    CAUSE_NUMBERS[module].get(cause),
                    ICDS[module].get(cause),
                    round(self.csmf[module].get('both', {}).get(cause, 0) * weight, 3),
                    round(self.csmf[module].get('male', {}).get(cause, 0) * weight, 3),
                    round(self.csmf[module].get('female', {}).get(cause, 0) * weight, 3),
                ])
        filename = os.path.join(self.working_dir_path, FOLDER2, 'csmf.csv')
        with open(filename, 'wb') as f:
            csv.writer(f).writerows(table)


    def _aggregate_csmf_to_gbd_level1(self):
        # silly py2 and your integer division
        total = float(sum(len(v) for v in self.predictions.values()))
        if not total:  # this wouldn't happen, would it
            self.gbd_csmf = None  # apparently it does...
            return

        module_weights = {module: len(self.predictions[module]) / total
                          for module in MODULES}
        gbd_csmf = defaultdict(float)
        for module, values in self.csmf.items():
            for cause, value in values['both'].items():
                gbd_cause = GBD_LEVEL1_CAUSES[module][cause]
                gbd_csmf[gbd_cause] += value * module_weights[module]

        table = [['cause', 'cause_name', 'CSMF']]
        table.extend([
            [cause, GBD_LEVEL1_CAUSE_NAMES[cause], round(value, 3)]
            for cause, value in sorted(gbd_csmf.items(), key=lambda x: x[0])
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
        if not self.gbd_csmf:
            return

        data = self.gbd_csmf[1:]  # drop headers
        values = [row[2] for row in data]

        def wrap(x):
            if x.startswith('Comm'):
                return x.replace(', neo', ',\nneo')
            else:
                return x
        labels = [wrap(row[1]) for row in data]
        color_map = {
            'A': '#e74c3c',
            'B': '#3498db',
            'C': '#2ecc71',
            'X': '#D3D3D3'
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
                    cause = row['cause34']
                    causes[module].add(cause)

                    if cause == 'Stillbirth':
                        age_group = STILLBIRTH_AGE
                    else:
                        age_group = self.bin_ages(module, safe_float(row['age']))
                    sex = sex_names.get(safe_int(row['sex']), 'Missing')
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
            - Tariff scores files by module with cause names as headers
            - Endorsement rates of symptoms by cause by module
            - Likelihood files by module, both CSV and XLSX (unmodified)
        """
        for module in MODULES:
            self._recode_prepped_files(module)
            self._copy_intermediate_files(module)
            self._copy_likelihood_files(module)
            self._write_endorsement_rates(module)
        self._write_report()

    def _recode_prepped_files(self, module):
        prepped_file = os.path.join(self.intermediate_dir,
                                    '{}-prepped.csv'.format(module))
        recoded_file = os.path.join(self.working_dir_path, INTERMEDIATES_FOLDER,
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
        files = ['{:s}-symptom.csv']
        files = [f.format(module) for f in files]
        for f in files:
            src = os.path.join(self.intermediate_dir, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(self.working_dir_path,
                                               INTERMEDIATES_FOLDER, f))

        causes = sorted(CAUSE46_NAMES[module].items(), key=lambda x: x[0])
        new_headers = ['sid']
        new_headers.extend([cause for _, cause in causes])

    def _copy_likelihood_files(self, module):
        for ext in ('csv', 'xlsx'):
            filename = '{:s}-likelihoods.{:s}'.format(module, ext)
            src = os.path.join(self.output_dir_path, filename)
            if os.path.exists(src):
                dest = os.path.join(self.working_dir_path, FOLDER4, filename)
                shutil.copy2(src, dest)

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

        drop = set(SHORT_DROP_SYMPTOMS[module]) if self.short_form else set()
        if not self.hce:
            drop.update(HCE_DROP_SYMPTOMS[module])
        if not self.free_text:
            drop.update([s for s in symptoms if s.startswith('s9999')])

        # Transpose "dataframe". This allows us to write data by row
        # We also want to preserve the order of the symptoms, just in case
        data = OrderedDict(
            (symp, {cause: endorsements[cause].get(symp, 0) / float(total)
                    for cause, total in counts.items() if total})
            for symp in symptoms if symp not in drop
        )
        causes = sorted(counts)
        filename = os.path.join(self.working_dir_path, INTERMEDIATES_FOLDER,
                                '{}-endorsement-rates.csv'.format(module))
        headers = ['symptom', 'description']
        headers.extend(causes)
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for symptom, rates in data.items():
                row = [symptom, SYMPTOM_DESCRIPTIONS[module].get(symptom)]
                row.extend(['{}%'.format(round(rates[cause] * 100, 1))
                             for cause in causes])
                writer.writerow(row)

    def _write_report(self):
        filename = os.path.join(self.working_dir_path, FOLDER4, 'report.txt')
        handler = logging.FileHandler(filename, mode='w')
        report_logger = logging.getLogger('report')

        log_descriptions = {
            'sids': '{} row(s) have duplicate or missing sids',
            'refused': '{} row(s) declined the interview.',
            'valid_consent': '{} row(s) did not have a valid value for consent.',
            'valid_age': ('{} row(s) did not have valid age data and could '
                          'not be analyzed.'),
            'prediction': ('{} row(s) had multiple causes predicted with equal '
                           'likelihood.')
        }

        report_logger.info('')
        report_logger.info('Quality summary:')
        for name in REPORT_LOGGERS_NAMES:
            errors = len(logging.getLogger(name).handlers[0].buffer)
            if errors:
                report_logger.info(log_descriptions[name].format(errors))

        report_logger.info('')
        report_logger.info('Details:')

        report = report_logger.handlers[0]
        report.setTarget(handler)
        report.flush()

        for name in REPORT_LOGGERS_NAMES:
            logger = logging.getLogger(name)
            store = logger.handlers[0]
            store.setTarget(handler)
            store.flush()


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
