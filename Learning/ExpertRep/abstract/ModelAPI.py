import logging

from abc import ABCMeta, abstractmethod

import pickle as pkl

from ExpertRep.abstract.ClimateEvalAPI import ModelInfo, ModelOutputs
from ExpertRep.tools.leave_one_out import leave_one_out

_LOG = logging.getLogger(__name__)


class MachineLearningModel(metaclass=ABCMeta):
    """
    The base class of any machine learning model to be used with this system.
    """

    def __init__(self):
        self._mock_partial_fit_buffer = [list(), list()]

    def fit_unsupervised(self, data: list):
        """
        Fits the unsupervised element of this model if available.

        Args:
            data: a list of ModelFile objects.
        Returns:
            None

        """
        _LOG.debug("Unsupervised fit is not implemented on model %s", type(self).__name__)

    def partial_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        """
        Used for online learning, otherwise this class will mock online learning by storing all
        partial fits and refitting each time.

        Args:
            data: a list of ModelFile objects
            targets: a list of targets
            *args:
            **kwargs:

        Returns:
            an instance of ModelOutputs containing the evaluation metric results.

        """
        _LOG.warning("True Partial fit is not implemented for %s, this results in a performance hit",
                     type(self).__name__)
        long_data, long_targets = self.mock_partial_fit_helper(data=data, targets=targets)

        return self.evaluate_and_fit(long_data, long_targets, *args, **kwargs)

    @abstractmethod
    def fit(self, data: list, targets: list, *args, **kwargs):
        """
        Fits the model from scratch.
        """

    def evaluate_and_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        """
        Evaluates and fits the model using leave one out validation.

        Args:
            data: a list of ModelFile objects
            targets: a list of targets
            *args:
            **kwargs:

        Returns:
            an instance of ModelOutputs containing the evaluation metric results.
        """
        return leave_one_out(data, targets, self.fit, self.score, *args, **kwargs)

    def mock_partial_fit_helper(self, *, data: list, targets: list) -> (list, list):
        """
        Helps to mock a partial fit on a model that does not support true one-shot online learning.

        Args:
            data: a list of ModelFile objects
            targets: a list of targets

        Returns:
            the full set of data to train upon.
        """
        for d, t in zip(data, targets):
            if d not in self._mock_partial_fit_buffer[0]:
                self._mock_partial_fit_buffer[0].append(d)
                self._mock_partial_fit_buffer[1].append(t)

#        self._mock_partial_fit_buffer[0] += data
#        self._mock_partial_fit_buffer[1] += targets
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
        """
        Converts the current model into bytes.

        Returns:
            the current model in bytes form.

        """
        # TODO (Ben) Add a registry system that allows models to define their own serialization mechanism??
        return pkl.dumps(self)

    @classmethod
    def deserialize(cls, serialized: bytes) -> "MachineLearningModel":
        """
        Performs the inverse opperation to serialize.

        Args:
            serialized: A bytes object that contains the output of serialize.

        Returns:
            an instance of MachineLearningModel

        """
        return pkl.loads(serialized)
