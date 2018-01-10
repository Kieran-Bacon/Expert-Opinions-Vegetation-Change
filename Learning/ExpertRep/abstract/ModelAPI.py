import logging
from abc import ABCMeta, abstractmethod
from ExpertRep.abstract.ClimateEvalAPI import ModelInfo, ModelOutputs
import pickle as pkl

_LOG = logging.getLogger(__name__)


class MachineLearningModel(metaclass=ABCMeta):
    def __init__(self):
        self._mock_partial_fit_buffer = [list(), list()]

    def fit_unsupervised(self):
        _LOG.debug("Unsupervised fit is not implemented on model %s", type(self).__name__)

    def partial_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        _LOG.warning("True Partial fit is not implemented for %s, this results in a performance hit",
                     type(self).__name__)
        long_data, long_targets = self.mock_partial_fit_helper(data=data, targets=targets)
        return self.fit(long_data, long_targets, *args, **kwargs)

    @abstractmethod
    def fit(self, data: list, targets: list, test_data: list, test_targets: list, *args, **kwargs) -> ModelOutputs:
        """
        """

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

    def serialize(self) -> bytes:
        # TODO (Ben) Add a registry system that allows models to define their own serialization mechanism??
        return pkl.dumps(self)

    @classmethod
    def deserialize(cls, serialized) -> "MachineLearningModel":
        return pkl.loads(serialized)
