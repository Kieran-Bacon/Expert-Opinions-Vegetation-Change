import logging
from abc import ABCMeta, abstractmethod
from ExpertRep.abstract.ClimateEvalAPI import ModelInfo, ModelOutputs
from ExpertRep.tools.leave_one_out import leave_one_out
import pickle as pkl

_LOG = logging.getLogger(__name__)


class MachineLearningModel(metaclass=ABCMeta):
    def __init__(self):
        self._mock_partial_fit_buffer = [list(), list()]

    def fit_unsupervised(self, data: list):
        _LOG.debug("Unsupervised fit is not implemented on model %s", type(self).__name__)

    def partial_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        _LOG.warning("True Partial fit is not implemented for %s, this results in a performance hit",
                     type(self).__name__)
        long_data, long_targets = self.mock_partial_fit_helper(data=data, targets=targets)

        return self.evaluate_and_fit(long_data, long_targets, *args, **kwargs)

    @abstractmethod
    def fit(self, data: list, targets: list, *args, **kwargs):
        """
        """

    def evaluate_and_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        return leave_one_out(data, targets, self.fit, self.score, *args, **kwargs)

    def mock_partial_fit_helper(self, *, data: list, targets: list) -> (list, list):
        self._mock_partial_fit_buffer[0] += data
        self._mock_partial_fit_buffer[1] += targets
        return self._mock_partial_fit_buffer

    @property
    @abstractmethod
    def model_info(self) -> ModelInfo:
        """
        """

    @abstractmethod
    def predict(self, data: list) -> list:
        """
        """

    @abstractmethod
    def score(self, test_data: list, test_targets: list) -> ModelOutputs:
        """
        """


    def serialize(self) -> bytes:
        # TODO (Ben) Add a registry system that allows models to define their own serialization mechanism??
        return pkl.dumps(self)

    @classmethod
    def deserialize(cls, serialized) -> "MachineLearningModel":
        return pkl.loads(serialized)
