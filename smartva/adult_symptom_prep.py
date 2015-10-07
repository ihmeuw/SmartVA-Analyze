import csv
import os

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier
from smartva.adult_symptom_data import (
    GENERATED_HEADERS,
    ADULT_CONVERSION_VARIABLES,
    COPY_VARIABLES,
    AGE_QUARTILE_BINARY_VARIABLES,
    GENDER_ASSIGNMENT_CONVERSION_VARIABLES,
    DURATION_CUTOFF_DATA,
    INJURY_VARIABLES,
    BINARY_VARIABLES,
    FREE_TEXT_VARIABLES,
    DROP_LIST,
)
from smartva.utils.conversion_utils import additional_headers_and_values

FILENAME_TEMPLATE = '{:s}-symptom.csv'


class AdultSymptomPrep(DataPrep):
    AGE_GROUP = 'adult'

    def run(self):
        status_logger.info('Adult :: Processing Adult symptom data')
        status_notifier.update({'progress': (3,)})

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb', buffering=0) as fo:
            writer = csv.writer(fo)

            with open(self.input_file_path, 'rb') as fi:
                reader = csv.reader(fi)

                headers = next(reader)

                additional_headers_data = GENERATED_HEADERS
                additional_headers, additional_values = additional_headers_and_values(headers, additional_headers_data)

                headers.extend(additional_headers)

                self.rename_headers(headers, ADULT_CONVERSION_VARIABLES)

                not_drop_list = ADULT_CONVERSION_VARIABLES.values() + FREE_TEXT_VARIABLES + additional_headers

                drop_index_list = set([i for i, header in enumerate(headers) if header not in not_drop_list])
                drop_index_list.update([headers.index(header) for header in DROP_LIST])

                writer.writerow(self.drop_from_list(headers, drop_index_list))

                for row in reader:
                    new_row = row + additional_values

                    for read_header, write_header in COPY_VARIABLES.items():
                        new_row[headers.index(write_header)] = new_row[headers.index(read_header)]

                    # Compute age quartiles.
                    for read_header, conversion_data in AGE_QUARTILE_BINARY_VARIABLES.items():
                        for value, write_header in conversion_data:
                            if int(new_row[headers.index(read_header)]) > value:
                                new_row[headers.index(write_header)] = 1
                                break

                    # Change sex from female = 2, male = 1 to female = 1, male = 0
                    # If unknown sex will default to 0 so it does not factor into analysis
                    for read_header, conversion_data in GENDER_ASSIGNMENT_CONVERSION_VARIABLES.items():
                        new_row[headers.index(read_header)] = conversion_data.get(int(new_row[headers.index(read_header)]), 0)

                    for sym, data in DURATION_CUTOFF_DATA.items():
                        index = headers.index(sym)
                        # replace the duration with 1000 if it is over 1000 and not missing
                        if new_row[index] == '':
                            new_row[index] = 0
                        elif float(new_row[index]) > 1000:
                            new_row[index] = 1000
                        # use cutoffs to determine if they will be replaced with a 1 (were above or equal to the cutoff)
                        if float(new_row[index]) >= DURATION_CUTOFF_DATA[sym] and new_row[index] != str(0):
                            new_row[index] = 1
                        else:
                            new_row[index] = 0
    
                        # The "var list" variables in the loop below are all indicators for different questions about
                        # injuries (road traffic, fall, fires) We only want to give a VA a "1"/yes response for that
                        # question if the injury occurred within 30 days of death (i.e. s163<=30) Otherwise, we could
                        # have people who responded that they were in a car accident 20 years prior to death be assigned
                        # to road traffic deaths
    
                        if not self.short_form:
                            for injury in INJURY_VARIABLES:
                                index = headers.index(injury)
                            injury_cut_index = headers.index('s163')
                            # 30 is the injury cutoff
                            if float(new_row[injury_cut_index]) > 30:
                                new_row[index] = 0
    
                    # dichotomize!
                    index1 = headers.index('s36991')
                    index2 = headers.index('s36992')
                    val = new_row[headers.index('s36')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1:
                        new_row[index1] = 1
                    elif val == 2 or val == 3:
                        new_row[index2] = 1
    
                    index1 = headers.index('s18991')
                    index2 = headers.index('s18992')
                    val = new_row[headers.index('s18')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1:
                        new_row[index1] = 1
                    elif val == 2 or val == 3:
                        new_row[index2] = 1
    
                    index1 = headers.index('s19991')
                    index2 = headers.index('s19992')
                    val = new_row[headers.index('s19')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1:
                        new_row[index1] = 1
                    elif val == 2:
                        new_row[index2] = 1
    
                    index1 = headers.index('s23991')
                    index2 = headers.index('s23992')
                    index3 = headers.index('s23993')
                    index4 = headers.index('s23994')
                    s23val = new_row[headers.index('s23')]
                    s25val = new_row[headers.index('s25')]
                    if s23val == '':
                        s23val = 0
                    else:
                        s23val = int(s23val)
                    if s25val == '':
                        s25val = 0
                    else:
                        s25val = int(s25val)
                    if s23val == 1 or s25val == 1:
                        new_row[index1] = 1
                    if s23val == 2 or s25val == 2:
                        new_row[index2] = 1
                    if s23val == 3 or s25val == 3:
                        new_row[index3] = 1
                    if s23val == 4 or s25val == 4:
                        new_row[index4] = 1
    
                    # s56 can be multiple
                    index1 = headers.index('s56991')
                    index2 = headers.index('s56992')
                    index3 = headers.index('s56993')
                    index4 = headers.index('s56994')
                    val = new_row[headers.index('s56')]
                    if val == '':
                        val = ['0']
                    else:
                        val = val.split(' ')
    
                    # this one doesn't exist?
                    # val2 = new_row[headers.index('s57')]
                    #            if val2 == '':
                    #                val2 = 0
                    #            else:
                    #                val2 = int(val2)
                    # if (val == 1 or val2 == 1):
                    #                 new_row[index1] = 1
                    #             elif (val == 2 or val2 == 2):
                    #                 new_row[index2] = 1
                    #             elif (val == 3 or val2 == 3):
                    #                 new_row[index3] = 1
                    #             elif (val == 4 or val2 == 4):
                    #                 new_row[index4] = 1
    
                    if '1' in val:
                        new_row[index1] = 1
                    if '2' in val:
                        new_row[index2] = 1
                    if '3' in val:
                        new_row[index3] = 1
                    if '4' in val:
                        new_row[index4] = 1
    
                    index1 = headers.index('s55991')
                    index2 = headers.index('s55992')
                    val = new_row[headers.index('s55')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1:
                        new_row[index1] = 1
                    elif val == 2:
                        new_row[index2] = 1
    
                    val = new_row[headers.index('s62')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1 or val == 2 or val == 8 or val == 9 or val == 0:
                        new_row[headers.index('s62')] = 0
                    elif val == 3:
                        new_row[headers.index('s62')] = 1
    
                    index1 = headers.index('s64991')
                    index2 = headers.index('s64992')
                    val = new_row[headers.index('s64')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1 or val == 2:
                        new_row[index1] = 1
                    elif val == 3:
                        new_row[index2] = 1
    
                    val = new_row[headers.index('s78')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1 or val == 2 or val == 8 or val == 9 or val == 0:
                        new_row[headers.index('s78')] = 0
                    elif val == 3:
                        new_row[headers.index('s78')] = 1
    
                    index1 = headers.index('s82991')
                    val = new_row[headers.index('s82')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
    
                    # not in electronic?
                    # val2 = new_row[headers.index('s83')]
                    #             if val2 == '':
                    #                 val2 = 0
                    #             else:
                    #                 val2 = int(val2)
                    #             if (val == 2 or val2 == 2):
                    #                 new_row[index1] = 1
                    if val == 2:
                        new_row[index1] = 1
    
                    val = new_row[headers.index('s86')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1 or val == 8 or val == 9 or val == 0:
                        new_row[headers.index('s86')] = 0
                    elif val == 2:
                        new_row[headers.index('s86')] = 1
    
                    val = new_row[headers.index('s91')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 2 or val == 8 or val == 9 or val == 0:
                        new_row[headers.index('s91')] = 0
    
                    val = new_row[headers.index('s95')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 2 or val == 8 or val == 9 or val == 0:
                        new_row[headers.index('s95')] = 0
    
                    val = new_row[headers.index('s100')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 2 or val == 8 or val == 9 or val == 0:
                        new_row[headers.index('s100')] = 0
    
                    index1 = headers.index('s150991')
                    index2 = headers.index('s150992')
                    val = new_row[headers.index('s150')]
                    if val == '':
                        val = 0
                    else:
                        val = int(val)
                    if val == 1:
                        new_row[index1] = 1
                    elif val == 2 or val == 3:
                        new_row[index2] = 1
    
                    if new_row[headers.index('s107')] == str(1) or new_row[headers.index('s108')] == str(1):
                        new_row[headers.index('s107')] = 1
    
                    # ensure all binary variables actually ARE 0 or 1:
                    for var in BINARY_VARIABLES:
                        val = new_row[headers.index(var)]
                        if val == '' or int(val) != 1:
                            new_row[headers.index(var)] = 0

                    writer.writerow(self.drop_from_list(new_row, drop_index_list))

            # writer.writerows([self.drop_from_list(row, drop_index_list) for row in matrix])

        return True

    def abort(self):
        self.want_abort = True
