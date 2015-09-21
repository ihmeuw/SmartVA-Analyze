import csv
import re
import string
import os

from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from vaprep_data import ADDITIONAL_HEADERS, SHORT_FORM_ADDITIONAL_HEADERS_DATA

NEONATE_PREPPED_FILENAME = 'neonate-prepped.csv'
CHILD_PREPPED_FILENAME = 'child-prepped.csv'
ADULT_PREPPED_FILENAME = 'adult-prepped.csv'

WORD_SUBS = {'abdomin': 'abdomen', 'abdominal': 'abdomen', 'accidentally': 'accident',
             'accidental': 'accident', 'accidently': 'accident', 'acute myocardial infarction': 'ami',
             'aids': 'hiv', 'anaemia': 'anemia', 'anemic': 'anemia', 'baby\'s': 'babi', 'babies': 'babi',
             'baby': 'babi', 'bit': 'bite', 'bitten': 'bite', 'bleed': 'blood', 'bleeding': 'blood',
             'blood pressure': 'hypertension', 'burn': 'fire', 'burns': 'fire', 'burnt': 'fire',
             'burned': 'fire', 'burning': 'fire', 'burnings': 'fire', 'c section': 'csection',
             'caesarean': 'cesarean', 'caesarian': 'cesarean', 'cancerous': 'cancer', 'carcinoma': 'cancer',
             'cardiac': 'cardio', 'cardiogenic': 'cardio', 'cerebrovascular': 'cerebral', 'cervical': 'cervix',
             'cesarian': 'cesarean', 'comatose': 'coma', 'convulsions': 'convulsion', 'death': 'dead',
             'dehydrated': 'dehydrate', 'dehydration': 'dehydrate', 'delivered': 'deliver',
             'deliveries': 'deliver', 'delivery': 'deliver', 'diarrheal': 'diarrhea',
             'difficult breath': 'dyspnea', 'difficult breathing': 'dyspnea', 'difficulty ': 'difficult',
             'digestion': 'digest', 'digestive': 'digest', 'dog bite': 'dogbite', 'drank': 'drink',
             'drawn': 'drown', 'drowned': 'drown', 'drowning': 'drown', 'drunk': 'drink',
             'dysentary': 'diarrhea', 'dyspneic': 'dyspnea', 'eclaupsia': 'eclampsia', 'edemata': 'edema',
             'edematous': 'edema', 'edoema': 'edema', 'ekg': 'ecg', 'esophageal': 'esophag',
             'esophagus': 'esophag', 'fallen': 'fall', 'falling': 'fall', 'feet': 'foot', 'fell': 'fall',
             'heart attack': 'ami', 'herniation': 'hernia', 'hypertensive': 'hypertension',
             'incubator': 'incubate', 'infected': 'infect', 'infectious': 'infect', 'injured': 'injury',
             'injures': 'injury', 'injuries': 'injury', 'ischemic': 'ischemia', 'labour': 'labor',
             'maternity': 'maternal', 'msb': 'stillbirth', 'oxygenated': 'oxygen', 'paralysis': 'paralyze',
             'poisoning': 'poison', 'poisonous': 'poison', 'pregnant': 'pregnancy', 'premature': 'preterm',
             'prematurity': 'preterm', 'septic': 'sepsis', 'septicaemia': 'sepsis',
             'septicemia': 'sepsis', 'smoker': 'smoke', 'stroked': 'stroke', 'swollen': 'swell', 'tb': 'tb',
             't.b': 'tb', 't.b.': 'tb', 'transfussed': 'transfuse', 'transfussion': 'transfuse',
             'tuberculosis': 'tb', 'urinary': 'urine', 'venomous': 'venom', 'violent': 'violence',
             'vomits': 'vomit', 'vomitting': 'vomit', 'yellowish': 'yellow'}

FREE_TEXT = ['adult_5_2a', 'adult_6_8', 'adult_6_11', 'adult_6_12', 'adult_6_13', 'adult_6_14', 'adult_6_15',
             'adult_7_c', 'child_5_9', 'child_5_12', 'child_5_13', 'child_5_14', 'child_5_15', 'child_5_16',
             'child_6_c']


class VaPrep(object):
    """
    This file cleans up input and converts from ODK collected data to VA variables.
    """

    def __init__(self, input_file, output_dir, short_form):
        self.input_file_path = input_file
        self.output_dir = output_dir
        self.want_abort = 0
        self.short_form = short_form

    @staticmethod
    def additional_headers_and_values(headers):
        additional_headers = ADDITIONAL_HEADERS
        additional_values = ['0'] * len(ADDITIONAL_HEADERS)
        for k, v in SHORT_FORM_ADDITIONAL_HEADERS_DATA:
            if k not in headers:
                additional_headers.append(k)
                additional_values.append(v)

        return additional_headers, additional_values

    def run(self):
        status_notifier.update({'progress': (1,)})

        status_logger.debug('Initial data prep')

        # matrix is a list of lists containing all of our data
        matrix = list()

        with open(self.input_file_path, 'rU') as f:
            reader = csv.reader(f)

            # Read headers and check for free text columns
            headers = next(reader)

            # Extend the headers with additional headers and read the remaining data into the matrix
            additional_headers, additional_values = self.additional_headers_and_values(headers)
            headers.extend(additional_headers)

            for row in reader:
                matrix.extend([row + additional_values])

        # column header renaming
        # rename adult_2_87 adult287
        index = headers.index('adult_2_87')
        headers[index] = 'orgadult287'

        # rename adult_5_2 adult52
        index = headers.index('adult_5_2')
        headers[index] = 'orgadult52'

        # rename child_4_48 orgchild448
        index = headers.index('child_4_48')
        headers[index] = 'orgchild448'

        # rename child_1_19 to child119
        index = headers.index('child_1_19')
        headers[index] = 'child119'

        # rename child_1_19a to child119a
        index = headers.index('child_1_19a')
        headers[index] = 'child119a'

        # rename child_3_3 child33
        index = headers.index('child_3_3')
        headers[index] = 'orgchild33'

        # rename child_2_1 child21
        index = headers.index('child_2_1')
        headers[index] = 'orgchild21'

        # rename child_5_2 child52
        index = headers.index('child_5_2')
        headers[index] = 'child52'

        # loop through each row, updating values (mostly additionalHeaders), based on user's answers
        for row in matrix:
            # fill in blank values for age
            index = headers.index('gen_5_4a')
            if row[index] == '':
                row[index] = 0
            index = headers.index('gen_5_4b')
            if row[index] == '':
                row[index] = 0
            index = headers.index('gen_5_4c')
            if row[index] == '':
                row[index] = 0

            # set paralysis variables based on multiple choice question
            index = headers.index('orgadult287')
            val = row[index].split(' ')
            if '1' in val:
                sub_index = headers.index('adultparalysis1')
                row[sub_index] = 1
            if '2' in val:
                sub_index = headers.index('adultparalysis2')
                row[sub_index] = 1
            if '3' in val:
                sub_index = headers.index('adultparalysis3')
                row[sub_index] = 1
            if '4' in val:
                sub_index = headers.index('adultparalysis4')
                row[sub_index] = 1
            if '5' in val:
                sub_index = headers.index('adultparalysis5')
                row[sub_index] = 1
            if '6' in val:
                sub_index = headers.index('adultparalysis6')
                row[sub_index] = 1
            if '7' in val:
                sub_index = headers.index('adultparalysis7')
                row[sub_index] = 1
            if '8' in val:
                sub_index = headers.index('adultparalysis8')
                row[sub_index] = 1
            if '9' in val:
                sub_index = headers.index('adultparalysis9')
                row[sub_index] = '1'
            if '11' in val:
                sub_index = headers.index('adultparalysis10')
                row[sub_index] = 1

            # set adultinjury variables based on multiple choice question
            index = headers.index('orgadult52')
            val = row[index].split(' ')
            if '1' in val:
                sub_index = headers.index('adultinjury1')
                row[sub_index] = 1
            if '2' in val:
                sub_index = headers.index('adultinjury2')
                row[sub_index] = 1
            if '3' in val:
                sub_index = headers.index('adultinjury3')
                row[sub_index] = 1
            if '4' in val:
                sub_index = headers.index('adultinjury4')
                row[sub_index] = 1
            if '5' in val:
                sub_index = headers.index('adultinjury5')
                row[sub_index] = 1
            if '6' in val:
                sub_index = headers.index('adultinjury6')
                row[sub_index] = 1
            if '7' in val:
                sub_index = headers.index('adultinjury7')
                row[sub_index] = 1
            if '11' in val:
                sub_index = headers.index('adultinjury8')
                row[sub_index] = 1

            # set childinjury variables based on multiple choice question
            index = headers.index('orgchild448')
            val = row[index].split(' ')
            if '1' in val:
                sub_index = headers.index('childinjury1')
                row[sub_index] = 1
            if '2' in val:
                sub_index = headers.index('childinjury2')
                row[sub_index] = 1
            if '3' in val:
                sub_index = headers.index('childinjury3')
                row[sub_index] = 1
            if '4' in val:
                sub_index = headers.index('childinjury4')
                row[sub_index] = 1
            if '5' in val:
                sub_index = headers.index('childinjury5')
                row[sub_index] = 1
            if '6' in val:
                sub_index = headers.index('childinjury6')
                row[sub_index] = 1
            if '7' in val:
                sub_index = headers.index('childinjury7')
                row[sub_index] = 1
            if '11' in val:
                sub_index = headers.index('childinjury8')
                row[sub_index] = 1
            if '8' in val:
                sub_index = headers.index('childinjury9')
                row[sub_index] = 1
            if '9' in val:
                sub_index = headers.index('childinjury10')
                row[sub_index] = 1

            # set adultrash variables based on multiple choice question
            index = headers.index('adult_2_9')
            val = row[index].split(' ')
            adultrash1index = headers.index('adultrash1')
            adultrash2index = headers.index('adultrash2')
            adultrash3index = headers.index('adultrash3')

            # if 1, 2, and 3 are selected, then change the value to 4 (all)
            if '1' in val and '2' in val and '3' in val:
                # first see if anything else is selected
                row[index] = 4
                row[adultrash1index] = 4
            else:
                # otherwise set adultrash to the other selected values
                words = row[index].split(' ')
                if len(words) == 1:
                    row[adultrash1index] = words[0]
                if len(words) == 2:
                    row[adultrash1index] = words[0]
                    row[adultrash2index] = words[1]
                if len(words) == 3:
                    row[adultrash1index] = words[0]
                    row[adultrash2index] = words[1]
                    row[adultrash3index] = words[2]

            # set child abnormality values
            index = headers.index('child119')
            first = row[index].split(' ')
            index = headers.index('child119a')
            second = row[index].split(' ')

            if '1' in first or '1' in second:
                sub_index = headers.index('childabnorm1')
                row[sub_index] = 1
            if '2' in first or '2' in second:
                sub_index = headers.index('childabnorm2')
                row[sub_index] = 1
            if '3' in first or '3' in second:
                sub_index = headers.index('childabnorm3')
                row[sub_index] = 1
            if '11' in first or '11' in second:
                sub_index = headers.index('childabnorm4')
                row[sub_index] = 1
            if '8' in first or '8' in second:
                sub_index = headers.index('childabnorm5')
                row[sub_index] = 1

            # set child abnormality values
            index = headers.index('orgchild33')
            val = row[index].split(' ')
            if '1' in val:
                sub_index = headers.index('childabnorm31')
                row[sub_index] = 1
            if '2' in val:
                sub_index = headers.index('childabnorm32')
                row[sub_index] = 1
            if '3' in val:
                sub_index = headers.index('childabnorm33')
                row[sub_index] = 1
            if '11' in val:
                sub_index = headers.index('childabnorm34')
                row[sub_index] = 1
            if '8' in val:
                sub_index = headers.index('childabnorm35')
                row[sub_index] = 1

            # set complications values
            index = headers.index('orgchild21')
            val = row[index].split(' ')
            if '1' in val:
                sub_index = headers.index('complications1')
                row[sub_index] = 1
            if '2' in val:
                sub_index = headers.index('complications2')
                row[sub_index] = 1
            if '3' in val:
                sub_index = headers.index('complications3')
                row[sub_index] = 1
            if '4' in val:
                sub_index = headers.index('complications4')
                row[sub_index] = 1
            if '5' in val:
                sub_index = headers.index('complications5')
                row[sub_index] = 1
            if '6' in val:
                sub_index = headers.index('complications6')
                row[sub_index] = 1
            if '7' in val:
                sub_index = headers.index('complications7')
                row[sub_index] = 1
            if '8' in val:
                sub_index = headers.index('complications8')
                row[sub_index] = 1
            if '9' in val:
                sub_index = headers.index('complications9')
                row[sub_index] = 1
            if '10' in val:
                sub_index = headers.index('complications10')
                row[sub_index] = 1
            if '88' in val:
                sub_index = headers.index('complications11')
                row[sub_index] = 1
            if '99' in val:
                sub_index = headers.index('complications12')
                row[sub_index] = 1

            # set provider values
            index = headers.index('child52')
            val = row[index].split(' ')
            if '1' in val:
                sub_index = headers.index('provider1')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider1')
                row[sub_index] = 0
            if '2' in val:
                sub_index = headers.index('provider2')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider2')
                row[sub_index] = 0
            if '3' in val:
                sub_index = headers.index('provider3')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider3')
                row[sub_index] = 0
            if '4' in val:
                sub_index = headers.index('provider4')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider4')
                row[sub_index] = 0
            if '5' in val:
                sub_index = headers.index('provider5')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider5')
                row[sub_index] = 0
            if '6' in val:
                sub_index = headers.index('provider6')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider6')
                row[sub_index] = 0
            if '7' in val:
                sub_index = headers.index('provider7')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider7')
                row[sub_index] = 0
            if '8' in val:
                sub_index = headers.index('provider8')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider8')
                row[sub_index] = 0
            if '9' in val:
                sub_index = headers.index('provider9')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider9')
                row[sub_index] = 0
            if '10' in val:
                sub_index = headers.index('provider10')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider10')
                row[sub_index] = 0
            if '11' in val:
                sub_index = headers.index('provider11')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider11')
                row[sub_index] = 0
            if '12' in val:
                sub_index = headers.index('provider12')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider12')
                row[sub_index] = 0
            if '88' in val:
                sub_index = headers.index('provider13')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider13')
                row[sub_index] = 0
            if '99' in val:
                sub_index = headers.index('provider14')
                row[sub_index] = 1
            else:
                sub_index = headers.index('provider14')
                row[sub_index] = 0

            # weights
            index = headers.index('child_1_8')
            val = row[index]
            index18a = headers.index('child_1_8a')
            index18b = headers.index('child_1_8b')
            if val == '2':
                row[index18a] = float(row[index18b]) * 1000
                row[index] = 1

            index = headers.index('child_5_6e')
            val = row[index]
            if val == '2':
                index56f = headers.index('child_5_6f')
                index56g = headers.index('child_5_6g')
                row[index56f] = float(row[index56g]) * 1000
                row[index] = 1

            index = headers.index('child_5_7e')
            val = row[index]
            if val == '2':
                index57f = headers.index('child_5_7f')
                index57g = headers.index('child_5_7g')
                row[index57f] = float(row[index57g]) * 1000
                row[index] = 1

        status_logger.debug('Text substitution')

        # this just does a substitution of words in the above list (mostly misspellings, etc..)
        for question in FREE_TEXT:
            try:
                index = headers.index(question)
            except ValueError:
                warning_logger.debug('Free text column "{}" does not exist.'.format(question))
            else:
                for row in matrix:
                    answer = row[index]
                    new_answer = re.sub('[^a-z ]', '', answer.lower())

                    # TODO - Fix this. It replaces partial words (e.g. bit and bite) and can cause errors.
                    # check to see if any of the keys exist in the freetext (keys can be multiple words like 'dog bite')
                    for key in WORD_SUBS.keys():
                        if key in new_answer:
                            # if it exists, replace it with the word(s) from the dictionary
                            new_answer = string.replace(new_answer, key, WORD_SUBS[key])

                    # now make sure we get rid of all extra whitespace
                    newanswerarray = new_answer.split(' ')
                    for i, word in enumerate(newanswerarray):
                        newanswerarray[i] = word.strip()
                    row[index] = ' '.join(newanswerarray)

        # going forward, now all of the answers are lowercase, without numbers or punctuation,
        # and whitespace has been eliminated, so it's just a list of words separated by spaces

        self.write_data(headers, matrix)

        return 1

    def write_data(self, headers, matrix):
        status_logger.debug('Writing adult, child, neonate prepped.csv files')

        adult_file = open(os.path.join(self.output_dir, ADULT_PREPPED_FILENAME), 'wb', buffering=0)
        child_file = open(os.path.join(self.output_dir, CHILD_PREPPED_FILENAME), 'wb', buffering=0)
        neonate_file = open(os.path.join(self.output_dir, NEONATE_PREPPED_FILENAME), 'wb', buffering=0)

        adult_writer = csv.writer(adult_file)
        child_writer = csv.writer(child_file)
        neonate_writer = csv.writer(neonate_file)

        # write out header files
        adult_writer.writerow(headers)
        child_writer.writerow(headers)
        neonate_writer.writerow(headers)

        # write out data by row into appropriate age range (adult, child, neonate)
        # blank values have already been replaced with 0 (int) here
        for a in matrix:
            age = int(a[headers.index('gen_5_4a')])
            days = int(a[headers.index('gen_5_4c')])
            months = int(a[headers.index('gen_5_4b')])
            # print 'for SID :: %s ' % (aaa)

            if age == 0 and days == 0 and months == 0:
                module = a[headers.index('gen_5_4d')]
                if module == '1':
                    # print 'neonate because gen_5_4d == 1'
                    neonate_writer.writerow(a)
                elif module == '2':
                    # print 'child because gen_5_4d == 2'
                    child_writer.writerow(a)
                elif module == '3':
                    # print 'adult because gen_5_4d == 3'
                    adult_writer.writerow(a)
                else:
                    # print 'neonate because no value for age'
                    updatestr = 'SID: %s has no values for age, defaulting to neonate' % a[headers.index('sid')]
                    warning_logger.warning(updatestr)
                    neonate_writer.writerow(a)
            else:
                if age >= 12:
                    # print 'adult because age >= 12'
                    adult_writer.writerow(a)
                else:
                    if days <= 28 and months == 0 and age == 0:
                        # print 'neonage because age <= 28'
                        neonate_writer.writerow(a)
                    else:
                        # print 'child because nothing else'
                        child_writer.writerow(a)

        adult_file.close()
        child_file.close()
        neonate_file.close()

    def abort(self):
        self.want_abort = 1
