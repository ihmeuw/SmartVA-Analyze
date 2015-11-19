import abc
import os

from smartva.data_prep import Prep, AbortException


class GrapherPrep(Prep):
    __metaclass__ = abc.ABCMeta

    def __init__(self, working_dir_path):
        super(GrapherPrep, self).__init__(working_dir_path)
        self.output_dir_path = os.path.join(self.input_dir_path, 'figures')

    def run(self):
        self._update_status()

        try:
            graph_data = self._read_graph_data()

            self._make_graphs(graph_data)

        except AbortException:
            return

    @abc.abstractmethod
    def _update_status(self):
        pass

    @abc.abstractmethod
    def _read_graph_data(self):
        pass

    @abc.abstractmethod
    def _make_graphs(self, graph_data):
        pass
