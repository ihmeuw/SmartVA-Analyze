import csv
import logging
import os
import threading

from smartva.vaprep import VaPrep
from smartva.adultpresymptom import PreSymptomPrep as AdultPreSymptomPrep
from smartva.adultsymptom import AdultSymptomPrep
from smartva.adulttariff import Tariff as AdultTariff
from smartva.childpresymptom import PreSymptomPrep as ChildPreSymptomPrep
from smartva.childsymptom import ChildSymptomPrep
from smartva.childtariff import Tariff as ChildTariff
from smartva.neonatepresymptom import PreSymptomPrep as NeonatePreSymptomPrep
from smartva.neonatesymptom import NeonateSymptomPrep
from smartva.neonatetariff import Tariff as NeonateTariff
from smartva.causegrapher import CauseGrapher
from smartva.csmfgrapher import CSMFGrapher
from smartva.loggers import warning_logger
from smartva.utils import status_notifier

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
    Note: If optional range is not present, the previous range should be used.
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
        self.output_dir = output_dir
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this

        warning_file_handler = logging.FileHandler(os.path.join(self.output_dir, 'warnings.txt'), mode='w', delay=True)
        warning_logger.addHandler(warning_file_handler)

        self.short_form = False

        self.start()

    @staticmethod
    def format_headers(source_path, dest_path):
        with open(source_path, 'Ub') as in_f:
            with open(dest_path, 'wb') as out_f:
                reader = csv.reader(in_f)
                writer = csv.writer(out_f)
                writer.writerow([col.split('-')[-1] for col in next(reader)])
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
        status_notifier.update({'progress': (0, 15), 'sub_progress': (0, 1)})

        intermediate_dir = os.path.join(self.output_dir, 'intermediate-files')
        figures_dir = os.path.join(self.output_dir, 'figures')

        self.make_dir(intermediate_dir)
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

        va_prep = VaPrep(intermediate_dir + os.sep + "cleanheaders.csv", intermediate_dir, self.short_form)
        adult_pre_symptom = AdultPreSymptomPrep(intermediate_dir + os.sep + "adult-prepped.csv", intermediate_dir, self.short_form)
        adult_symptom = AdultSymptomPrep(intermediate_dir + os.sep + "adult-presymptom.csv", intermediate_dir, self.short_form)
        adult_results = AdultTariff(intermediate_dir + os.sep + "adult-symptom.csv", self.output_dir, intermediate_dir, self.hce, self.free_text, self.malaria, self.country, self.short_form)
        child_pre_symptom = ChildPreSymptomPrep(intermediate_dir + os.sep + "child-prepped.csv", intermediate_dir, self.short_form)
        child_symptom = ChildSymptomPrep(intermediate_dir + os.sep + "child-presymptom.csv", intermediate_dir, self.short_form)
        child_results = ChildTariff(intermediate_dir + os.sep + "child-symptom.csv", self.output_dir, intermediate_dir, self.hce, self.free_text, self.malaria, self.country, self.short_form)
        neonate_pre_symptom = NeonatePreSymptomPrep(intermediate_dir + os.sep + "neonate-prepped.csv", intermediate_dir, self.short_form)
        neonate_symptom = NeonateSymptomPrep(intermediate_dir + os.sep + "neonate-presymptom.csv", intermediate_dir)
        neonate_results = NeonateTariff(intermediate_dir + os.sep + "neonate-symptom.csv", self.output_dir, intermediate_dir, self.hce, self.free_text, self.country, self.short_form)
        cause_grapher = CauseGrapher(self.output_dir + os.sep + '$module-predictions.csv', figures_dir)
        csmf_grapher = CSMFGrapher(self.output_dir + os.sep + '$module-csmf.csv', figures_dir)

        self._abort_list.extend([
            va_prep,
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
        va_prep.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # makes adult-presymptom.csv
        adult_data = adult_pre_symptom.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # makes adult-symptom.csv
        if adult_data:
            adult_symptom.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        #
        # creates adult output files
        if adult_data:
            adult_results.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # makes child-presymptom.csv
        child_data = child_pre_symptom.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # makes child-symptom.csv
        if child_data:
            child_symptom.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # creates child output files
        if child_data:
            child_results.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # makes neonate-presymptom.csv
        # TODO:  right now this is the same as child presymptom, should probably just combine into one
        neonate_data = neonate_pre_symptom.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # makes neonate-symptom.csv
        if neonate_data:
            neonate_symptom.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

        # creates neonate output files
        if neonate_data:
            neonate_results.run()
        if self._want_abort:
            self._complete(CompletionStatus.ABORT)
            return

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
        status_notifier.update({'progress': (int(not status), 1), 'sub_progress': (int(not status), 1)})
        self._completion_callback(status, message)
