from __future__ import print_function
import os
import pickle

from smartva.child_tariff_data import (
    HCE_DROP_LIST,
    SHORT_FORM_DROP_LIST,
    FREQUENCIES,
    CAUSE_CONDITIONS,
    CAUSE_REDUCTION,
    CAUSES
)
from smartva.freetext_vars import CHILD_FREE_TEXT as FREE_TEXT
from smartva.loggers import status_logger
from smartva.tariff_prep import TariffPrep, TARIFF_CAUSE_NUM_KEY


class ChildTariff(TariffPrep):
    def __init__(self, input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form):
        super(ChildTariff, self).__init__(input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form)

        self.AGE_GROUP = 'child'

    def run(self):
        super(ChildTariff, self).run()

        # Headers are being dropped only from tariff matrix now because of the way we are iterating over the pruned
        # tariff data. It is unnecessary to drop headers from other matrices.
        drop_headers = {TARIFF_CAUSE_NUM_KEY}
        if not self.hce:
            drop_headers.update(HCE_DROP_LIST)
        if not self.free_text:
            drop_headers.update(FREE_TEXT)
        if self.short_form:
            drop_headers.update(SHORT_FORM_DROP_LIST)

        cause46_names = self.get_cause46_names()

        undetermined_matrix = self.get_undetermined_matrix()

        cause40s = self.get_cause40s(drop_headers)
        self.cause_list = sorted(cause40s.keys())

        # """
        status_logger.info('{:s} :: Generating validated VA cause list.'.format(self.AGE_GROUP.capitalize()))
        va_validated_cause_list = self.get_va_cause_list(self.va_validated_filename, cause40s)

        with open(os.path.join(self.intermediate_dir, 'validated-{:s}.pickle'.format(self.AGE_GROUP)), 'wb') as f:
            pickle.dump(va_validated_cause_list, f)
        """
        with open(os.path.join(self.intermediate_dir, 'validated-{:s}.pickle'.format(self.AGE_GROUP)), 'rb') as f:
            va_validated_cause_list = pickle.load(f)
        # """

        uniform_list = self.generate_uniform_list(va_validated_cause_list, FREQUENCIES)

        status_logger.debug('{:s} :: Generating cutoffs'.format(self.AGE_GROUP.capitalize()))
        cutoffs = self.generate_cutoffs(uniform_list, 0.95)

        # """
        status_logger.info('{:s} :: Generating VA cause list.'.format(self.AGE_GROUP.capitalize()))
        va_cause_list = self.get_va_cause_list(self.input_file_path, cause40s)

        status_logger.info('{:s} :: Generating cause rankings.'.format(self.AGE_GROUP.capitalize()))
        self.generate_cause_rankings(va_cause_list, uniform_list)

        with open(os.path.join(self.intermediate_dir, 'rank_list-{:s}.pickle'.format(self.AGE_GROUP)), 'wb') as f:
            pickle.dump(va_cause_list, f)
        """
        with open(os.path.join(self.intermediate_dir, 'rank_list-{:s}.pickle'.format(self.AGE_GROUP)), 'rb') as f:
            va_cause_list = pickle.load(f)
        # """

        self.write_external_ranks(va_cause_list)

        lowest_rank = len(uniform_list)

        self.identify_lowest_ranked_causes(va_cause_list, uniform_list, cutoffs, CAUSE_CONDITIONS, lowest_rank, 0.18, 6.0)

        cause_counts = self.write_predictions(va_cause_list, undetermined_matrix, lowest_rank, CAUSE_REDUCTION, CAUSES, cause46_names)

        self.write_csmf(cause_counts)

        self.write_tariff_ranks(va_cause_list)

        self.write_tariff_scores(va_cause_list)

        return True

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = map(float, [va.age, u_row['age']])

        return ((u_age == 0.0 and va_age < 1.0) or
                (u_age == 1.0 and 1.0 <= va_age < 5.0) or
                (u_age == 5.0 and 5.0 <= va_age < 9.0) or
                (u_age == 10.0 and 10.0 <= va_age < 15.0))
