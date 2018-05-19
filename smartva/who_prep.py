from itertools import product

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import safe_int
from smartva.data import who_data

# Hackishly overwrite input to CommonPrep if necessary
INPUT_FILENAME_TEMPLATE = 'cleanheaders.csv'
OUTPUT_FILENAME_TEMPLATE = 'cleanheaders.csv'


class WHOPrep(DataPrep):

    def __init__(self, working_dir_path):
        super(WHOPrep, self).__init__(working_dir_path, True)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self.data_module = who_data

    def run(self):
        super(WHOPrep, self).run()

        status_logger.info('Mapping WHO Questionnaire')
        status_notifier.update({'progress': 1})

        headers = set(self.data_module.ADDITIONAL_HEADERS)
        headers.update(self.data_module.YES_NO_QUESTIONS)
        headers.update([h for h, _ in self.data_module.RECODE_QUESTIONS])
        headers.update(self.data_module.RENAME_QUESTIONS)
        headers.update(self.data_module.REVERSE_ONE_HOT_MULTISELECT)
        headers.update([h for h, _ in self.data_module.RECODE_MULTISELECT])
        headers.update(self.data_module.ONE_HOT_FROM_MULTISELECT)
        headers.update(self.data_module.UNIT_IF_AMOUNT)
        for unit_col, value_col, _ in self.data_module.DURATION_CONVERSIONS:
            headers.update([unit_col, value_col])

        _, matrix = DataPrep.read_input_file(self.input_file_path())

        status_notifier.update({'sub_progress': (0, len(matrix))})

        for index, row in enumerate(matrix):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            self.determine_consent(row)
            self.calculate_age(row)
            self.recode_yes_no_questions(row)
            self.recode_categoricals(row)
            self.rename_questions(row)
            self.reverse_one_hot_multiselect(row)
            self.recode_multiselects(row)
            self.encode_one_hot_from_multiselect(row)
            self.map_units_from_values(row)
            self.convert_durations(row)
            self.map_adult_chest_pain_duration(row)
            self.map_child_illness_duration(row)
            self.map_neonate_first_cry(row)
            self.map_child_unconsciousness_start(row)
            self.map_neonate_delivery_type(row)
            self.map_child_birth_size(row)
            self.map_redundant_child_age_data(row)

        status_notifier.update({'sub_progress': None})

        DataPrep.write_output_file(sorted(headers), matrix,
                                   self.output_file_path(None))

    def determine_consent(self, row):
        """Determine if the row gave consent.

        Unlike other mappings for the WHO, we're not going to fill in a header
        with a missing value for consent. The CommonPrep stage has special
        handling which considers a missing header different from a missing or
        invalid valid. Only map the column if it is present to defer missing
        handling to downstream code.
        """
        consent_col = 'Id10013'
        if consent_col in row:
            row['gen_3_1'] = int(row[consent_col] == 'yes')

    def calculate_age(self, row):
        # We're not going to attempt to parse date strings because we can't
        # guarantee the reliable format and don't want to design a generic
        # sniffer. This means we're stuck using primarily calculated values
        # and hoping they exist.
        unit_col = 'gen_5_4'

        for col in ('ageInYears', 'age_adult', 'age_child_years'):
            age_in_years = safe_int(row.get(col))
            if age_in_years >= 1:
                row[unit_col] = 1
                row['gen_5_4a'] = age_in_years
                row['agedays'] = age_in_years * 365
                return

        for col in ('ageInMonths', 'age_child_months'):
            age_in_months = safe_int(row.get(col))
            if age_in_months >= 1:
                if age_in_months < 12:
                    row[unit_col] = 2
                    row['gen_5_4b'] = age_in_months
                else:
                    row[unit_col] = 1
                    row['gen_5_4a'] = int(age_in_months / 12)

                row['agedays'] = age_in_months * 30
                return

        # We don't want to fill columns with zero. Zero is a valid age and
        # column might not be the "final" age. As such we can't use safe_int
        # here, because it would return zero on a ValueError
        age_day_cols = ('ageInDays', 'ageInDaysNeonate', 'age_neonate_days',
                        'age_child_days')
        for col in age_day_cols:
            try:
                age_in_days = int(row[col])
            except (ValueError, TypeError, KeyError):
                pass
            else:
                if age_in_days <= 30:
                    row[unit_col] = 4
                    row['gen_5_4c'] = age_in_days
                elif age_in_days < 365:
                    row[unit_col] = 2
                    row['gen_5_4b'] = int(age_in_days / 30)
                else:
                    row[unit_col] = 1
                    row['gen_5_4a'] = int(age_in_days / 365)

                row['agedays'] = age_in_days
                return

        # This is the "give-up" section. Look for age group only.
        # Loop over suffixes first since these are order from most trusted
        # to least trusted. We want to search one set of suffixes for all
        # age groups (just in case)
        age_group_cols = product(
            ('', 1, 2), {'Adult': 3, 'Child': 2, 'Neonate': 1}.items())
        for suffix, (module, value) in age_group_cols:
            if safe_int(row.get('is{}{}'.format(module, suffix))):
                row['gen_5_4d'] = value
                break
        else:
            row['gen_5_4d'] = 9
        row['agedays'] = ''

    def recode_yes_no_questions(self, row):
        mapping = {'yes': 1, 'no': 0, 'ref': 8, 'dk': 9}
        for dest, src in self.data_module.YES_NO_QUESTIONS.items():
            try:
                value = int(mapping[row[src]])
            except (TypeError, KeyError):
                value = ''
            row[dest] = value

    def recode_categoricals(self, row):
        for (dest, src), mapping in self.data_module.RECODE_QUESTIONS.items():
            try:
                value = int(mapping[row[src]])
            except (TypeError, KeyError):
                value = ''
            row[dest] = value

    def rename_questions(self, row):
        for dest, src in self.data_module.RENAME_QUESTIONS.items():
            row[dest] = row.get(src, '')

    def reverse_one_hot_multiselect(self, row):
        """Recode a series of dummy variables into a multiselect"""
        for dest, mapping in self.data_module.REVERSE_ONE_HOT_MULTISELECT.items():
            endorsement = set()
            for src, value in mapping.items():
                if row.get(src) == 'yes':
                    endorsement.add(value)
            row[dest] = ' '.join(map(str, sorted(endorsement)))

    def recode_multiselects(self, row):
        for (dest, src), mapping in self.data_module.RECODE_MULTISELECT.items():
            row[dest] = ' '.join(map(str, sorted(filter(None, [
                mapping.get(x, '') for x in row.get(src, '').split()]))))

    def encode_one_hot_from_multiselect(self, row):
        for dest, (src, choice) in self.data_module.ONE_HOT_FROM_MULTISELECT.items():
            try:
                value = int(choice in row[src].split())
            except (KeyError, ValueError, TypeError):
                value = ''
            row[dest] = value

    def map_units_from_values(self, row):
        for dest, unit_data in self.data_module.UNIT_IF_AMOUNT.items():
            try:
                for src, unit in unit_data.items():
                    if safe_int(row.get(src)) > 0:
                        row[dest] = unit
                        break
                else:
                    row[dest] = ''
            except AttributeError:  # not a dict
                src, unit = unit_data
                row[dest] = unit if safe_int(row.get(src)) > 0 else ''

    def convert_durations(self, row):
        for x in self.data_module.DURATION_CONVERSIONS.items():
            (unit_col, value_col, unit), mapping = x
            for src, scalar in mapping.items():
                value = safe_int(row.get(src)) * scalar
                if value > 0:
                    row[unit_col] = unit
                    row[value_col] = value
                    break
            else:
                row[unit_col] = ''
                row[value_col] = ''

    def map_adult_chest_pain_duration(self, row):
        """Custom mapping for adult_2_44: chest pain duration."""
        key = 'adult_2_44'

        try:
            dur_in_minutes = int(row['Id10178'])
        except (KeyError, TypeError, ValueError):
            pass
        else:
            if 0 <= dur_in_minutes < 30:
                row[key] = 1
                return
            elif 30 <= dur_in_minutes < 24 * 60:
                row[key] = 2
                return

        try:
            dur_in_hours = int(row['Id10179'])
        except (KeyError, TypeError, ValueError):
            pass
        else:
            if 0 < dur_in_hours < 24:
                row[key] = 2
                return
            elif dur_in_hours >= 24:
                row[key] = 3
                return

        try:
            dur_in_days = int(row['Id10179_1'])
        except (KeyError, TypeError, ValueError):
            pass
        else:
            if dur_in_days > 0:
                row[key] = 3
                return

        row[key] = ''

    def map_redundant_child_age_data(self, row):
        age_group_key = 'child_1_26'
        unit_key = 'child_1_25'
        age_days = row.get('agedays')  # must be called after calculate_age
        if age_days == '' or age_days is None:
            age_group = row['gen_5_4d']
            row[age_group_key] = age_group if age_group in (1, 2) else ''
            row[unit_key] = ''
            return
        else:
            try:
                age_days = int(age_days)
            except (ValueError, TypeError):
                return

        if age_days <= 28:
            row[age_group_key] = 1
        elif 28 < age_days < 12 * 365:
            row[age_group_key] = 2
        else:
            row[age_group_key] = ''

        if age_days <= 30:
            row[unit_key] = 4
            row['{}a'.format(unit_key)] = age_days
        elif age_days < 365:
            row[unit_key] = 2
            row['{}b'.format(unit_key)] = int(age_days / 30.4)
        elif age_days >= 365:
            row[unit_key] = 1
            row['{}c'.format(unit_key)] = int(age_days / 365)

    def map_child_illness_duration(self, row):
        key = 'child_1_21'
        try:
            row['{}a'.format(key)] = int(row['Id10120_1'])
        except (KeyError, TypeError, ValueError):
            pass
        else:
            row[key] = 4
            return

        try:
            row['{}b'.format(key)] = int(row['Id10121'])
        except (KeyError, TypeError, ValueError):
            pass
        else:
            row[key] = 2
            return

        try:
            row['{}c'.format(key)] = int(row['Id10122']) * 12
        except (KeyError, TypeError, ValueError):
            pass
        else:
            row[key] = 2
            return

    def map_neonate_first_cry(self, row):
        key = 'child_3_8'
        try:
            dur_in_minutes = int(row['Id10106'])
        except (KeyError, TypeError, ValueError):
            row[key] = 4 if row.get('Id10105') == 'yes' else ''
        else:
            if 0 <= dur_in_minutes <= 5:
                row[key] = 1
            elif 6 <= dur_in_minutes <= 30:
                row[key] = 2
            elif dur_in_minutes > 30:
                row[key] = 3
            else:
                row[key] = ''

    def map_child_unconsciousness_start(self, row):
        key = 'child_4_27'
        who_key = 'Id10216'

        try:
            dur_in_hours = int(row['{}_a'.format(who_key)])
        except (KeyError, TypeError, ValueError):
            dur_in_hours = None

        dur_in_days = safe_int(row.get('{}_b'.format(who_key)))

        if dur_in_hours is None:
            row[key] = 3 if dur_in_days >= 1 else ''
            return

        if dur_in_hours >= 24:
            row[key] = 3
        elif 0 <= dur_in_hours <= 5:
            row[key] = 1
        elif 6 <= dur_in_hours <= 23:
            row[key] = 2
        else:
            row[key] = ''

    def map_neonate_delivery_type(self, row):
        key = 'child_2_17'
        if row.get('Id10342') == 'yes':
            row[key] = 2
        elif row.get('Id10343') == 'yes':
            row[key] = 1
        elif row.get('Id10344') == 'yes':
            row[key] = 4
        elif (row.get('Id10342') == 'dk' and row.get('Id0343') == 'dk' and
              row.get('Id10344') in ('no', 'dk')):
            row[key] = 3
        else:
            row[key] = ''

    def map_child_birth_size(self, row):
        key = 'child_1_7'
        if row.get('Id10364') == 'yes':
            row[key] = 1
        elif row.get('Id10363') == 'yes':
            row[key] = 2
        elif row.get('Id10365') == 'yes':
            row[key] = 4
        elif all([row.get(k) == 'no'
                  for k in ('Id10363', 'Id10364', 'Id10365')]):
            row[key] = 3
        else:
            row[key] = ''
