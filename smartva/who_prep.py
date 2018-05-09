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

        _, matrix = DataPrep.read_input_file(self.input_file_path())

        status_notifier.update({'sub_progress': (0, len(matrix))})

        for index, row in enumerate(matrix):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            self.determine_consent(row)
            self.calculate_age(row)

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
