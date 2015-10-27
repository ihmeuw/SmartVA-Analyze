import csv
import os

from smartva.symptom_prep import SymptomPrep, FILENAME_TEMPLATE
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import additional_headers_and_values
from smartva.adult_symptom_data import (
    GENERATED_VARS_DATA,
    VAR_CONVERSION_MAP,
    COPY_VARS,
    AGE_QUARTILE_BINARY_VARS,
    DURATION_CUTOFF_DATA,
    INJURY_VARS,
    BINARY_VARS,
    FREE_TEXT_VARIABLES,
    DROP_LIST,
    BINARY_CONVERSION_MAP
)


class AdultSymptomPrep(SymptomPrep):
    """
    Prepare symptom data for tariff processing.

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

    def __init__(self, input_file, output_dir, short_form):
        super(AdultSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.AGE_GROUP = 'adult'

    def run(self):
        super(AdultSymptomPrep, self).run()

        with open(self.input_file_path, 'rb') as fi:
            reader = csv.DictReader(fi)
            matrix = [row for row in reader]

        status_notifier.update({'sub_progress': (0, len(matrix))})

        headers = reader.fieldnames

        additional_data = {}
        additional_data.update(GENERATED_VARS_DATA)
        additional_headers, additional_values = additional_headers_and_values(headers, additional_data.items())

        headers.extend(additional_headers)
        self.rename_headers(headers, VAR_CONVERSION_MAP)

        # TODO - Review this and re-implement for DictWriter, if necessary.
        # Identify unneeded variables for removal, and write the new headers to the output file.
        """
        not_drop_list = VAR_CONVERSION_MAP.values() + FREE_TEXT_VARIABLES + additional_headers

        drop_index_list = set([i for i, header in enumerate(headers) if header not in not_drop_list])
        drop_index_list.update([headers.index(header) for header in DROP_LIST])
        """

        for index, row in enumerate(matrix):
            if self.want_abort:
                return False

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, dict(zip(additional_headers, additional_values)))
            self.rename_vars(row, VAR_CONVERSION_MAP)

            self.copy_variables(row, COPY_VARS)

            # Compute age quartiles.
            self.process_quartile_data(row, AGE_QUARTILE_BINARY_VARS.items())

            self.process_cutoff_data(row, DURATION_CUTOFF_DATA.items())

            self.process_injury_data(row, INJURY_VARS.items())

            # Dichotomize!
            self.process_binary_vars(row, BINARY_CONVERSION_MAP.items())

            # Ensure all binary variables actually ARE 0 or 1:
            self.post_process_binary_variables(row, BINARY_VARS)

        status_notifier.update({'sub_progress': None})

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.DictWriter(fo, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matrix)

        return True
