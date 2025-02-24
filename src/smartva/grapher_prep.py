import abc
import os

from smartva.data_prep import Prep


class GrapherPrep(Prep, metaclass=abc.ABCMeta):
    def __init__(self, working_dir_path):
        super(GrapherPrep, self).__init__(working_dir_path)
        self.output_dir_path = os.path.join(self.input_dir_path, 'figures')

    def run(self):
        super(GrapherPrep, self).run()

        self._update_status()

        graph_data = self._read_graph_data()

        self._make_graphs(graph_data)


    @abc.abstractmethod
    def _update_status(self):
        pass

    @abc.abstractmethod
    def _read_graph_data(self):
        pass

    @abc.abstractmethod
    def _make_graphs(self, graph_data):
        pass
