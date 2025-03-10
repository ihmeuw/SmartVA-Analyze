import re

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import additional_headers_and_values, \
    safe_int, safe_float


INPUT_FILENAME_TEMPLATE = '{:s}-logic-rules.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-symptom.csv'


class SymptomPrep(DataPrep):
    """Prepare symptom data for tariff processing.

    The main goal of this step is to complete the conversion of symptom answers to binary data.

    Notes:
        Change sex from female = 2, male = 1 to female = 1, male = 0
        Unknown sex will default to 0 so it contributes nothing to the tariff score as calculated in the
        tariff 2.0 algorithm.

        For all indicators for different questions about injuries (road traffic, fall, fires) We only want
        to give a VA a 1 (yes) response for that question if the injury occurred within 30 days of death
        (i.e. s163<=30) Otherwise, we could have people who responded that they were in a car accident 20
        years prior to death be assigned to road traffic deaths.
    """

    def __init__(self, data_module, working_dir_path, short_form, who_2016):
        super(SymptomPrep, self).__init__(working_dir_path, short_form, who_2016)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self.data_module = data_module
        self.AGE_GROUP = data_module.AGE_GROUP

    def run(self):
        super(SymptomPrep, self).run()

        status_logger.info('{} :: Processing symptom data'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

        headers, matrix = DataPrep.read_input_file(self.input_file_path())

        status_notifier.update({'sub_progress': (0, len(matrix))})

        additional_data = {}
        additional_data.update(self.data_module.GENERATED_VARS_DATA)
        additional_headers, additional_values = additional_headers_and_values(headers, list(additional_data.items()))

        headers.extend(additional_headers)
        self.rename_headers(headers, self.data_module.VAR_CONVERSION_MAP)

        keep_list = [header for header in headers if re.match(self.data_module.KEEP_PATTERN, header)]
        drop_list = self.data_module.DROP_LIST

        headers = sorted([header for header in headers if header in keep_list and header not in drop_list],
                         key=lambda t: (t != 'sid', t[1].isdigit(), t))

        for index, row in enumerate(matrix):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, dict(list(zip(additional_headers, additional_values))))
            self.rename_vars(row, self.data_module.VAR_CONVERSION_MAP)

            self.copy_variables(row, self.data_module.COPY_VARS)

            # Compute age quartiles.
            self.process_progressive_value_data(row, list(self.data_module.AGE_QUARTILE_BINARY_VARS.items()))

            self.process_cutoff_data(row, list(self.data_module.DURATION_CUTOFF_DATA.items()))

            self.process_injury_data(row, list(self.data_module.INJURY_VARS.items()))

            # Dichotomize!
            self.process_binary_vars(row, list(self.data_module.BINARY_CONVERSION_MAP.items()))

            # Ensure all binary variables actually ARE 0 or 1:
            self.post_process_binary_variables(row, self.data_module.BINARY_VARS)

            self.censor_causes(row, self.data_module.CENSORED_MAP)

            self.require_symptoms(row, self.data_module.REQUIRED_MAP)

        status_notifier.update({'sub_progress': None})

        DataPrep.write_output_file(headers, matrix, self.output_file_path())

        return matrix

    def copy_variables(self, row, copy_variables_map):
        """Copy data from one variable to another.

        Copy Variables Map Format:
            {
                'read variable': 'write variable'
            }

        Args:
            row (dict): Row of VA data.
            copy_variables_map (dict): Read and write answer variables.
        """
        for read_header, write_header in list(copy_variables_map.items()):
            try:
                row[write_header] = row[read_header]
            except KeyError as e:
                warning_logger.debug('SID: {} variable \'{}\' does not exist. copy_variables'
                                     .format(row['sid'], str(e)))

    def process_cutoff_data(self, row, cutoff_data_map):
        """Change read variable to 1/0 if value is greater/less or equal to cutoff, respectively.

        Cutoff data map Format:
            {
                'read variable': cutoff value
            }

        Args:
            row (dict): Row of VA data.
            cutoff_data_map (dict): Cutoff data in specified format.
        """
        for read_header, cutoff_data in cutoff_data_map:
            try:
                row[read_header] = int(float(row[read_header]) >= cutoff_data)
            except ValueError:
                row[read_header] = 0
            except KeyError as e:
                warning_logger.debug('SID: {} variable \'{}\' does not exist. process_cutoff_data'
                                     .format(row['sid'], str(e)))

    def process_injury_data(self, row, injury_variable_map):
        """Cut off injuries occurring more than 30 days from death, set variable to 0.

        Injury variable map Format:
            {
                'read variable': [quoted list of injury variables]
            }

        Args:
            row (dict): Row of VA data.
            injury_variable_map (dict): Map of injury variables in specified format.
        """
        for read_data, injury_list in injury_variable_map:
            read_header, cutoff = read_data
            injury_period = safe_float(row.get(read_header))
            if injury_period <= cutoff:
                continue

            # Injury duration definitely greater than the threshold
            # so we 0 out related variables
            for injury in injury_list:
                row[injury] = 0

    def post_process_binary_variables(self, row, binary_variables):
        """Ensure all binary variables are actually 1 or 0.

        Binary variables Format:
            [list of binary variables]

        Args:
            row (dict): Row of VA data.
            binary_variables (list): Binary variable list.
        """
        for read_header in binary_variables:
            try:
                value = int(row[read_header])
            except ValueError:
                value = 0
            except KeyError as e:
                # Variable does not exist.
                warning_logger.debug('SID: {} variable \'{}\' does not exist. post_process_binary_variables'
                                     .format(row['sid'], str(e)))
                continue
            row[read_header] = int(value == 1)

    def censor_causes(self, row, cause_conditions):
        """Mark causes which should be ranked as lowest based on symptom endorsement

        Args:
            row (dict): Row of VA data.
            cause_condtions (dict): cause -> list of symptoms
        """
        restricted = set()
        for cause, symptoms in list(cause_conditions.items()):
            if any([safe_int(row.get(symp, 0)) for symp in symptoms]):
                restricted.add(cause)
        row['restricted'] = ' '.join(map(str, sorted(restricted)))

    def require_symptoms(self, row, cause_conditions):
        """Mark causes which should be ranked as lowested based on the lack
        of symptom endorsement

        Args:
            row (dict): Row of VA data.
            cause_conditions (dict): cause -> list of symptoms
        """
        restricted = set(map(int, row.get('restricted', '').split()))
        for cause, symptoms in list(cause_conditions.items()):
            if not all([int(row.get(symp, 0)) for symp in symptoms]):
                restricted.add(cause)
        row['restricted'] = ' '.join(map(str, sorted(restricted)))
