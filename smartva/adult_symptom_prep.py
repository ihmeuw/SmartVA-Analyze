import csv
import os

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier
from smartva.adult_symptom_data import (
    ADULT_CONVERSION_VARIABLES,
    BINARY_VARIABLES,
    DURATION_CUTOFFS,
    DURATION_SYMPTOM_VARIABLES,
    GENERATED_HEADERS,
    INJURY_VARIABLES,
    FREE_TEXT_VARIABLES,
    DROP_LIST
)
from smartva.utils.conversion_utils import additional_headers_and_values

FILENAME_TEMPLATE = '{:s}-symptom.csv'


class AdultSymptomPrep(DataPrep):
    AGE_GROUP = 'adult'

    def run(self):
        status_logger.info('Adult :: Processing Adult symptom data')
        status_notifier.update({'progress': (3,)})

        matrix = []
        headers = []

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb', buffering=0) as f:
            writer = csv.writer(f)

            with open(self.input_file_path, 'rb') as f:
                reader = csv.reader(f)

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
                    matrix.append(row + additional_values)

            # age quartiles
            for row in matrix:
                index = headers.index('age')
                s8881index = headers.index('s88881')
                s8882index = headers.index('s88882')
                s8883index = headers.index('s88883')
                s8884index = headers.index('s88884')
                if 32 >= int(row[index]) > 0:
                    row[s8881index] = 1
                elif 32 < int(row[index]) <= 49:
                    row[s8882index] = 1
                elif 49 < int(row[index]) <= 65:
                    row[s8883index] = 1
                elif int(row[index]) > 65:
                    row[s8884index] = 1

                # change sex from female = 2, male = 1 to female = 1, male = 0
                # if unknown sex will default to 0 so it does not factor into analysis
                index = headers.index('sex')
                val = int(row[index])
                if val == 2:
                    row[index] = 1
                elif val == 1:
                    row[index] = 0
                elif val == 9:
                    row[index] = 0

                # make new variables to store the real age and gender, but do it after we've modified the sex vars
                # from 2, 1 to 1, 0
                age_index = headers.index('real_age')
                gender_index = headers.index('real_gender')
                row[age_index] = row[headers.index('age')]
                row[gender_index] = row[headers.index('sex')]

                for sym in DURATION_SYMPTOM_VARIABLES:
                    index = headers.index(sym)
                    # replace the duration with 1000 if it is over 1000 and not missing
                    if row[index] == '':
                        row[index] = 0
                    elif float(row[index]) > 1000:
                        row[index] = 1000
                    # use cutoffs to determine if they will be replaced with a 1 (were above or equal to the cutoff)
                    if float(row[index]) >= DURATION_CUTOFFS[sym] and row[index] != str(0):
                        row[index] = 1
                    else:
                        row[index] = 0

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
                        if float(row[injury_cut_index]) > 30:
                            row[index] = 0

                # dichotomize!
                index1 = headers.index('s36991')
                index2 = headers.index('s36992')
                val = row[headers.index('s36')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1:
                    row[index1] = 1
                elif val == 2 or val == 3:
                    row[index2] = 1

                index1 = headers.index('s18991')
                index2 = headers.index('s18992')
                val = row[headers.index('s18')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1:
                    row[index1] = 1
                elif val == 2 or val == 3:
                    row[index2] = 1

                index1 = headers.index('s19991')
                index2 = headers.index('s19992')
                val = row[headers.index('s19')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1:
                    row[index1] = 1
                elif val == 2:
                    row[index2] = 1

                index1 = headers.index('s23991')
                index2 = headers.index('s23992')
                index3 = headers.index('s23993')
                index4 = headers.index('s23994')
                s23val = row[headers.index('s23')]
                s25val = row[headers.index('s25')]
                if s23val == '':
                    s23val = 0
                else:
                    s23val = int(s23val)
                if s25val == '':
                    s25val = 0
                else:
                    s25val = int(s25val)
                if s23val == 1 or s25val == 1:
                    row[index1] = 1
                if s23val == 2 or s25val == 2:
                    row[index2] = 1
                if s23val == 3 or s25val == 3:
                    row[index3] = 1
                if s23val == 4 or s25val == 4:
                    row[index4] = 1

                # s56 can be multiple
                index1 = headers.index('s56991')
                index2 = headers.index('s56992')
                index3 = headers.index('s56993')
                index4 = headers.index('s56994')
                val = row[headers.index('s56')]
                if val == '':
                    val = ['0']
                else:
                    val = val.split(' ')

                # this one doesn't exist?
                # val2 = row[headers.index('s57')]
                #            if val2 == '':
                #                val2 = 0
                #            else:
                #                val2 = int(val2)
                # if (val == 1 or val2 == 1):
                #                 row[index1] = 1
                #             elif (val == 2 or val2 == 2):
                #                 row[index2] = 1
                #             elif (val == 3 or val2 == 3):
                #                 row[index3] = 1
                #             elif (val == 4 or val2 == 4):
                #                 row[index4] = 1

                if '1' in val:
                    row[index1] = 1
                if '2' in val:
                    row[index2] = 1
                if '3' in val:
                    row[index3] = 1
                if '4' in val:
                    row[index4] = 1

                index1 = headers.index('s55991')
                index2 = headers.index('s55992')
                val = row[headers.index('s55')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1:
                    row[index1] = 1
                elif val == 2:
                    row[index2] = 1

                val = row[headers.index('s62')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1 or val == 2 or val == 8 or val == 9 or val == 0:
                    row[headers.index('s62')] = 0
                elif val == 3:
                    row[headers.index('s62')] = 1

                index1 = headers.index('s64991')
                index2 = headers.index('s64992')
                val = row[headers.index('s64')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1 or val == 2:
                    row[index1] = 1
                elif val == 3:
                    row[index2] = 1

                val = row[headers.index('s78')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1 or val == 2 or val == 8 or val == 9 or val == 0:
                    row[headers.index('s78')] = 0
                elif val == 3:
                    row[headers.index('s78')] = 1

                index1 = headers.index('s82991')
                val = row[headers.index('s82')]
                if val == '':
                    val = 0
                else:
                    val = int(val)

                # not in electronic?
                # val2 = row[headers.index('s83')]
                #             if val2 == '':
                #                 val2 = 0
                #             else:
                #                 val2 = int(val2)
                #             if (val == 2 or val2 == 2):
                #                 row[index1] = 1
                if val == 2:
                    row[index1] = 1

                val = row[headers.index('s86')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1 or val == 8 or val == 9 or val == 0:
                    row[headers.index('s86')] = 0
                elif val == 2:
                    row[headers.index('s86')] = 1

                val = row[headers.index('s91')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 2 or val == 8 or val == 9 or val == 0:
                    row[headers.index('s91')] = 0

                val = row[headers.index('s95')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 2 or val == 8 or val == 9 or val == 0:
                    row[headers.index('s95')] = 0

                val = row[headers.index('s100')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 2 or val == 8 or val == 9 or val == 0:
                    row[headers.index('s100')] = 0

                index1 = headers.index('s150991')
                index2 = headers.index('s150992')
                val = row[headers.index('s150')]
                if val == '':
                    val = 0
                else:
                    val = int(val)
                if val == 1:
                    row[index1] = 1
                elif val == 2 or val == 3:
                    row[index2] = 1

                if row[headers.index('s107')] == str(1) or row[headers.index('s108')] == str(1):
                    row[headers.index('s107')] = 1

                # ensure all binary variables actually ARE 0 or 1:
                for var in BINARY_VARIABLES:
                    val = row[headers.index(var)]
                    if val == '' or int(val) != 1:
                        row[headers.index(var)] = 0

            writer.writerows([self.drop_from_list(row, drop_index_list) for row in matrix])

        return True

    def abort(self):
        self.want_abort = True
