from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier


class PreSymptomPrep(DataPrep):
    AGE_GROUP = 'none'
    FILENAME_TEMPLATE = '{:s}-presymptom.csv'

    def run(self):
        super(PreSymptomPrep, self).run()
        status_logger.info('{} :: Processing pre-symptom data'.format(self.AGE_GROUP.capitalize()))
        # status_notifier.update({'progress': (2,)})

    @staticmethod
    def get_drop_index_list(headers, drop_pattern):
        """
        Find and return a list of header indices that match a given pattern.

        :param headers: List of headers.
        :param drop_pattern: Regular expression of drop pattern.
        :return: List of indices.
        """
        return [headers.index(header) for header in headers if re.match(drop_pattern, header)]

    @staticmethod
    def verify_answers_for_row(headers, row, valid_range_data):
        """
        Verify answers in a row of data are valid.

        :param headers: List of headers.
        :param row: Row of data.
        :param valid_range_data: Dictionary of headers and valid ranges.
        :return: True if any values fail validation.
        """
        warnings = False
        for header, range_list in valid_range_data.items():
            try:
                value = row[headers.index(header)]
            except ValueError:
                pass  # Header not in data set.
            else:
                if value != '' and range_list:
                    try:
                        answer_array = value.split()
                    except AttributeError:
                        answer_array = [value]
                    for answer in answer_array:
                        if int(answer) not in range_list:
                            warning_logger.warning('SID: {} variable {} has an illegal value {}. '
                                                   'Please see Codebook for legal values.'
                                                   .format(row[headers.index('sid')], header, value))
                            warnings = True
        return warnings

    @staticmethod
    def consolidate_answers(headers, row, consolidation_map):
        """
        Consolidate answers from data answers into new variables.

        Consolidation map dictionary format:
            (read_header, write_header): {
                VAL: data_header
            }

        :param headers: List of headers.
        :param row: Row of data.
        :param consolidation_map: Dictionary of read/write variables and their data counterparts.
        """
        for data_headers, data_map in consolidation_map.items():
            read_header, write_header = data_headers
            try:
                value = int(row[headers.index(read_header)])
            except ValueError:
                # FIXME - This covers both the header index and the int operations.
                pass
            else:
                if value in data_map:
                    row[headers.index(write_header)] = row[headers.index(data_map[value])]
