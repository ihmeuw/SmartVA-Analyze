from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier

FILENAME_TEMPLATE = '{:s}-symptom.csv'


class SymptomPrep(DataPrep):
    def run(self):
        super(SymptomPrep, self).run()
        status_logger.info('{} :: Processing symptom data'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

    @staticmethod
    def copy_variables(row, copy_variables_map):
        """
        Copy data from one variable to another.
        {
            'read variable': 'write variable'
        }

        :param row: Row of data.
        :param copy_variables_map: Dict of read header and write header.
        """
        for read_header, write_header in copy_variables_map.items():
            row[write_header] = row[read_header]

    @staticmethod
    def process_quartile_data(row, quartile_data):
        """
        Populate quartile variables from input data.
        Format:
        {
            'read variable': [
                (upper, variable),
                (median, variable),
                (lower, variable),
                (0, variable)
            ]
        }

        :param row: Row of data.
        :param quartile_data: Quartile ranges in specified format.
        """
        for read_header, conversion_data in quartile_data:
            for value, write_header in conversion_data:
                if float(row[read_header]) > value:
                    row[write_header] = 1
                    break

    @staticmethod
    def process_cutoff_data(row, cutoff_data_map):
        """
        Change read variable to 1/0 if value is greater/less or equal to cutoff, respectively.
        Format:
        {
            variable: cutoff
        }

        :param row:
        :param cutoff_data_map: Dict in specified format.
        """
        for read_header, cutoff_data in cutoff_data_map:
            try:
                row[read_header] = int(float(row[read_header]) >= cutoff_data)
            except ValueError:
                row[read_header] = 0

    @staticmethod
    def process_injury_data(row, injury_variable_map):
        """
        If injury occurred more than 30 days from death, set variable to 0.
        Format:
        {
            'read variable': [list of injury variables]
        }

        :param row: Row of data.
        :param injury_variable_map: Dict in specified format.
        """
        for read_header, injury_list in injury_variable_map:
            if float(row[read_header]) > 30:
                for injury in injury_list:
                    row[injury] = 0

    @staticmethod
    def post_process_binary_variables(row, binary_variables):
        """
        Ensure all binary variables are actually 1 or 0.
        Format:
            [list of binary variables]

        :param row: Row of data.
        :param binary_variables: List in specified format.
        """
        for read_header in binary_variables:
            try:
                value = int(row[read_header])
            except ValueError:
                value = 0
            row[read_header] = int(value == 1)
