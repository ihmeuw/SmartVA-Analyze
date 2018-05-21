import csv
import logging
import os
import re
import threading
import traceback
from data_prep import AbortException

from smartva.who_prep import WHOPrep
from smartva.common_prep import CommonPrep
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.symptom_prep import SymptomPrep
from smartva.rules_prep import RulesPrep, ADULT_RULES, CHILD_RULES, NEONATE_RULES
from smartva.tariff_prep import TariffPrep
from smartva.cause_grapher import CauseGrapher
from smartva.csmf_grapher import CSMFGrapher
from smartva.output_prep import OutputPrep
from smartva.loggers import status_logger, warning_logger, report_logger
from smartva.utils import find_dupes, status_notifier, intermediate_dir_path
from smartva.data import (
    common_data,
    adult_pre_symptom_data,
    child_pre_symptom_data,
    neonate_pre_symptom_data,
    adult_symptom_data,
    child_symptom_data,
    neonate_symptom_data,
    adult_tariff_data,
    child_tariff_data,
    neonate_tariff_data,
)

SHORT_FORM_HEADER = 'adult_7_11'
CLEAN_HEADERS_FILENAME = 'cleanheaders.csv'


class CompletionStatus(object):
    DONE = 0
    ABORT = 1
    FAIL = 2


# Thread class that executes processing
class WorkerThread(threading.Thread):
    """
    Worker Thread Class.

    For status notifier updates, the following key: value pairs are supplied:
        progress: (value, [range]) - Update value of progress bar
        sub_progress: (value, [range]) - Update value of sub progress bar
        message: (text, [style]) - Display a message with an optional style (default: information)
            Defined styles: exclamation, error, question, warning, information
    Note: If optional range is not present, the previous range will be used. Specify `None` to indicate progress
          completion and to reset the progress bar..
    """

    def __init__(self, input_file, output_dir, options, country, completion_callback):
        """
        Init Worker Thread Class.

        :param options: Dictionary of application options.
                        Must contain:
                            'hce': (bool),
                            'free_text': (bool),
                            'hiv': (bool),
                            'malaria': (bool)

        :type input_file: str
        :type output_dir: str
        :type options: dict
        :type country: str
        :type completion_callback: callable
        """
        threading.Thread.__init__(self)
        self._completion_callback = completion_callback
        self._want_abort = False
        self._abort_list = []

        self.options = options
        self.country = country

        self.input_file_path = input_file
        self.output_dir_path = output_dir
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this

        self._warnings_file = os.path.join(self.output_dir_path, 'warnings.txt')
        warning_file_handler = logging.FileHandler(self._warnings_file, mode='w', delay=True)
        warning_logger.addHandler(warning_file_handler)

        self.short_form = False

        self.start()

    @classmethod
    def _format_header(cls, header):
        # ODK aggregate uses colons as column delimiters, briefcase
        # uses dashes
        header_wo_colon = header.replace(':','-')  

        # SmartVA-Analyze only uses "name" from survey page of xls
        # file run through XLSForms
        header_list = header_wo_colon.split('-')
        return header_list[-1]  

    @classmethod
    def format_headers(cls, source_path, dest_path):
        with open(source_path, 'Ub') as in_f:
            with open(dest_path, 'wb') as out_f:
                reader = csv.reader(in_f)
                writer = csv.writer(out_f)

                headers = list(map(cls._format_header, next(reader)))
                dupes = find_dupes(headers)
                if dupes:
                    warning_logger.warning(
                        'Duplicate headers found: {}. Please review the input file for conflicts.'.format(dupes))

                writer.writerow(headers)
                writer.writerow(next(reader))
                writer.writerows(reader)

    @staticmethod
    def who_questionaire_test(file_path):
        with open(file_path, 'Ub') as f:
            headers = next(csv.reader(f))

        # Now we have two problems
        # case insensitive `id####` possibly with a tag, such as `Id####_a` or
        # `Id####_check`, or begins with `age` or `is`
        pattern = re.compile(r'^[Ii]d\d+(_\w+)?$|^age|^is')
        matches = sum(bool(pattern.match(h)) for h in headers)

        threshold = 0.80
        return matches / float(len(headers)) > threshold

    @staticmethod
    def short_form_test(file_path):
        with open(file_path, 'Ub') as f:
            return SHORT_FORM_HEADER in next(csv.reader(f))

    @staticmethod
    def make_dir(*args):
        path = os.path.join(*args)
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:
                warning_logger.warning('Could not create directory {}'.format(path))

    def run(self):
        status_logger.info('Preparing variable headers.')
        status_notifier.update({'progress': (0, 15), 'sub_progress': None})

        intermediate_dir = intermediate_dir_path(self.output_dir_path)
        figures_dir = os.path.join(self.output_dir_path, 'figures')

        self.make_dir(intermediate_dir_path(self.output_dir_path))

        try:
            self.format_headers(self.input_file_path, os.path.join(intermediate_dir, CLEAN_HEADERS_FILENAME))
        except StopIteration:
            # File doesn't contain data
            message = 'Source file "{}" does not contain data.'.format(self.input_file_path)
            self._complete(CompletionStatus.FAIL, message)
            warning_logger.warning(message)
            return

        report_logger.info('Analysis parameters:')
        report_logger.info('- Input file: {}'.format(self.input_file_path))
        report_logger.info('- Output folder: {}'.format(self.output_dir_path))
        report_logger.info('- Country: {}'.format(self.options.get('country')))
        report_logger.info('- HIV Region: {}'.format(self.options.get('hiv', True)))
        report_logger.info('- Malaria Region: {}'.format(self.options.get('malaria', True)))
        report_logger.info('')

        file_path = os.path.join(intermediate_dir, CLEAN_HEADERS_FILENAME)
        who_questionnaire = self.who_questionaire_test(file_path)

        if who_questionnaire:
            self.short_form = True
            form_name = 'WHO 2016 Questionnaire'

        else:
            self.short_form = self.short_form_test(file_path)
            warning_logger.debug('Detected {} form'.format(
                'short' if self.short_form else 'standard'))
            if self.short_form:
                form_name = 'PHMRC Shortened Questionnaire'
            else:
                form_name = 'PHMRC Full Questionnaire'
        report_logger.info('Detected {}'.format(form_name))

        who_prep = WHOPrep(self.output_dir_path)
        common_prep = CommonPrep(self.output_dir_path, self.short_form)
        adult_pre_symptom = PreSymptomPrep(adult_pre_symptom_data, self.output_dir_path, self.short_form)
        adult_rules = RulesPrep(self.output_dir_path, self.short_form, common_data.ADULT, ADULT_RULES)
        adult_symptom = SymptomPrep(adult_symptom_data, self.output_dir_path, self.short_form)
        adult_results = TariffPrep(adult_tariff_data, self.output_dir_path, self.short_form, self.options, self.country)
        child_pre_symptom = PreSymptomPrep(child_pre_symptom_data, self.output_dir_path, self.short_form)
        child_rules = RulesPrep(self.output_dir_path, self.short_form, common_data.CHILD, CHILD_RULES)
        child_symptom = SymptomPrep(child_symptom_data, self.output_dir_path, self.short_form)
        child_results = TariffPrep(child_tariff_data, self.output_dir_path, self.short_form, self.options, self.country)
        neonate_pre_symptom = PreSymptomPrep(neonate_pre_symptom_data, self.output_dir_path, self.short_form)
        neonate_rules = RulesPrep(self.output_dir_path, self.short_form, common_data.NEONATE, NEONATE_RULES)
        neonate_symptom = SymptomPrep(neonate_symptom_data, self.output_dir_path, self.short_form)
        neonate_results = TariffPrep(neonate_tariff_data, self.output_dir_path, self.short_form, self.options, self.country)
        legacy = self.options.get('legacy_format', False)
        output = OutputPrep(self.output_dir_path, reorganize=not legacy,
                            keep_orig=legacy, short_form=self.short_form,
                            free_text=self.options.get('free_text', True),
                            hce=self.options.get('hce', True))
        cause_grapher = CauseGrapher(self.output_dir_path)
        csmf_grapher = CSMFGrapher(self.output_dir_path)

        self._abort_list.extend([
            who_prep,
            common_prep,
            adult_pre_symptom,
            adult_rules,
            adult_symptom,
            adult_results,
            child_pre_symptom,
            child_rules,
            child_symptom,
            child_results,
            neonate_pre_symptom,
            neonate_rules,
            neonate_symptom,
            neonate_results,
            cause_grapher,
            csmf_grapher,
        ])

        try:
            if who_questionnaire:
                who_prep.run()

            # makes adult-prepped.csv, child-prepped.csv, neonate-prepped.csv
            adult_data, child_data, neonate_data = common_prep.run()

            if adult_data:
                # makes adult-presymptom.csv
                adult_pre_symptom.run()
                # makes adult-logic-rules.csv
                adult_rules.run()
                # makes adult-symptom.csv
                adult_symptom.run()
                # creates adult output files
                adult_results.run()

            if child_data:
                # makes child-presymptom.csv
                child_pre_symptom.run()
                # makes child-logic-rules.csv
                child_rules.run()
                # makes child-symptom.csv
                child_symptom.run()
                # creates child output files
                child_results.run()

            if neonate_data:
                # makes neonate-presymptom.csv
                neonate_pre_symptom.run()
                # makes neonate-logic-rules.csv
                neonate_rules.run()
                # makes neonate-symptom.csv
                neonate_symptom.run()
                # creates neonate output files
                neonate_results.run()

            if self.options.get('figures') and (adult_data or child_data or neonate_data):
                self.make_dir(figures_dir)
                # generate all cause graphs
                cause_grapher.run()
                # generate all csmf graphs
                csmf_grapher.run()

            output.run()

        except AbortException:
            self._complete(CompletionStatus.ABORT)
        except Exception:
            traceback.print_exc()
            self._complete(CompletionStatus.FAIL)
        else:
            self._complete(CompletionStatus.DONE)

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = True
        for item in self._abort_list:
            item.abort()

    def _complete(self, status, message=''):
        for handler in warning_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

        for handler in logging.getLogger('report').handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

        # The warnings file will be created on the first warning. If the file doesn't exist, no warnings.
        if os.path.exists(self._warnings_file):
            message += ('\nWarnings were generated during processing. '
                        'Please review the file "{}" for further information.'.format(self._warnings_file))
        self.completion_status = status
        self._completion_callback(status, message)
