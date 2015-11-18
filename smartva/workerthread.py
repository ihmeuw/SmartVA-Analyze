import csv
import logging
import os
import threading

from smartva.common_prep import CommonPrep
from smartva.adult_pre_symptom_prep import AdultPreSymptomPrep
from smartva.adult_symptom_prep import AdultSymptomPrep
from smartva.adult_tariff import AdultTariff
from smartva.child_pre_symptom_prep import ChildPreSymptomPrep
from smartva.child_symptom_prep import ChildSymptomPrep
from smartva.child_tariff import ChildTariff
from smartva.neonate_pre_symptom_prep import NeonatePreSymptomPrep
from smartva.neonate_symptom_prep import NeonateSymptomPrep
from smartva.neonate_tariff import NeonateTariff
from smartva.cause_grapher import CauseGrapher
from smartva.csmf_grapher import CSMFGrapher
from smartva.loggers import status_logger, warning_logger
from smartva.utils import find_dupes, status_notifier, intermediate_dir_path

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

    def __init__(self, input_file, hce, output_dir, free_text, malaria, country, completion_callback):
        """
        Init Worker Thread Class.
        :type input_file: str
        :type hce: bool
        :type output_dir: str
        :type free_text: bool
        :type malaria: bool
        :type country: str
        :type completion_callback: callable
        """
        threading.Thread.__init__(self)
        self._completion_callback = completion_callback
        self._want_abort = False
        self._abort_list = []

        self.hce = hce
        self.free_text = free_text
        self.malaria = malaria
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
        return header.split('-')[-1]

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
    def short_form_test(file_path):
        with open(file_path, 'Ub') as f:
            return SHORT_FORM_HEADER in next(csv.reader(f))

    @staticmethod
    def make_dir(*args):
        path = os.path.join(*args)
        if not os.path.exists(path):
            os.mkdir(path)

    def run(self):
        status_logger.info('Preparing variable headers.')
        status_notifier.update({'progress': (0, 15), 'sub_progress': None})

        intermediate_dir = intermediate_dir_path(self.output_dir_path)
        figures_dir = os.path.join(self.output_dir_path, 'figures')

        self.make_dir(intermediate_dir_path(self.output_dir_path))
        self.make_dir(figures_dir)

        try:
            self.format_headers(self.input_file_path, os.path.join(intermediate_dir, CLEAN_HEADERS_FILENAME))
        except StopIteration:
            # File doesn't contain data
            message = 'Source file "{}" does not contain data.'.format(self.input_file_path)
            self._complete(CompletionStatus.FAIL, message)
            warning_logger.warning(message)
            return

        self.short_form = self.short_form_test(os.path.join(intermediate_dir, CLEAN_HEADERS_FILENAME))
        warning_logger.debug('Detected {} form'.format('short' if self.short_form else 'standard'))

        common_prep = CommonPrep(self.output_dir_path, self.short_form)
        adult_pre_symptom = AdultPreSymptomPrep(self.output_dir_path, self.short_form)
        adult_symptom = AdultSymptomPrep(self.output_dir_path, self.short_form)
        adult_results = AdultTariff(self.output_dir_path, self.short_form, self.hce, self.free_text, self.malaria, self.country)
        child_pre_symptom = ChildPreSymptomPrep(self.output_dir_path, self.short_form)
        child_symptom = ChildSymptomPrep(self.output_dir_path, self.short_form)
        child_results = ChildTariff(self.output_dir_path, self.short_form, self.hce, self.free_text, self.malaria, self.country)
        neonate_pre_symptom = NeonatePreSymptomPrep(self.output_dir_path, self.short_form)
        neonate_symptom = NeonateSymptomPrep(self.output_dir_path, self.short_form)
        neonate_results = NeonateTariff(self.output_dir_path, self.short_form, self.hce, self.free_text, self.malaria, self.country)
        cause_grapher = CauseGrapher(self.output_dir_path, figures_dir)
        csmf_grapher = CSMFGrapher(self.output_dir_path, figures_dir)

        self._abort_list.extend([
            common_prep,
            adult_pre_symptom,
            adult_symptom,
            adult_results,
            child_pre_symptom,
            child_symptom,
            child_results,
            neonate_pre_symptom,
            neonate_symptom,
            neonate_results,
            cause_grapher,
            csmf_grapher,
        ])

        # makes adult-prepped.csv, child-prepped.csv, neonate-prepped.csv
        # we have data at this point, so all of these files should have been created
        adult_data, child_data, neonate_data = common_prep.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        if adult_data:
            # makes adult-presymptom.csv
            adult_pre_symptom.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

            # makes adult-symptom.csv
            adult_symptom.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

            # creates adult output files
            adult_results.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

        if child_data:
            # makes child-presymptom.csv
            child_pre_symptom.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

            # makes child-symptom.csv
            child_symptom.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

            # creates child output files
            child_results.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

        if neonate_data:
            # makes neonate-presymptom.csv
            # TODO:  right now this is the same as child presymptom, should probably just combine into one
            neonate_pre_symptom.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

            # makes neonate-symptom.csv
            neonate_symptom.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

            # creates neonate output files
            neonate_results.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

        if adult_data or child_data or neonate_data:
            # generate all cause graphs
            cause_grapher.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

            # generate all csmf graphs
            csmf_grapher.run()
            if self._want_abort:
                self._complete(CompletionStatus.ABORT)
                return

        self._complete(CompletionStatus.DONE)
        return

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

        # The warnings file will be created on the first warning. If the file doesn't exist, no warnings.
        if os.path.exists(self._warnings_file):
            message += ('\nWarnings were generated during processing. '
                        'Please review the file "{}" for further information.'.format(self._warnings_file))
        self._completion_callback(status, message)
