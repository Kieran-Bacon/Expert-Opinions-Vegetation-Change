"""
Contains a nice wrapper for plug and play use of SKlearn Models with the ClimateLearning API.
"""
from abc import ABCMeta, abstractmethod

import numpy as np
import logging

from sklearn.base import is_classifier, is_regressor

from ExpertRep.abstract.ModelAPI import MachineLearningModel
from sklearn.metrics import precision_score as calculate_precision
from ExpertRep.abstract.ClimateEvalAPI import ModelOutputsGeneric

_LOGGER = logging.getLogger(__name__)


class SKBase(MachineLearningModel, metaclass=ABCMeta):
    """
    A class that given an instance of an sklearn model fills some of the functionality required to interface between an
     SKLearn supervised algorithm and the MachineLearningModel API.
    """

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.buckets = None

    def fit(self, data: list, targets: list, *args, **kwargs):
        """ See superclass docstring """
        data_arrays = self._reshape_to_2d(data)
        if is_classifier(self.model):
            targets = self._bucket_targets(targets, train=True)
        else:
            # Fit the buckets anyway for evaluation
            self._bucket_targets(targets, train=True)
        self.model.fit(data_arrays, targets)

    @abstractmethod
    def model_info(self):
        """ """

    def num_buckets(self):
        return 6

    def predict(self, data: list) -> list:
        """ See superclass docstring """
        data_arrays = self._reshape_to_2d(data)
        model_output = self.model.predict(data_arrays).tolist()
        if is_classifier(self.model):
            model_output = self._unbucket_model_output(model_output)
        return model_output

    @staticmethod
    def _reshape_to_2d(data):
        """ See superclass docstring """
        return [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]

    def _unbucket_model_output(self, model_out):
        bucket_middle = np.mean(self.buckets, axis=1)
        return bucket_middle[model_out]

    def _bucket_targets(self, targets, train):
        try:
            num_buckets = self.num_buckets()
            if train:
                mini, maxi = np.min(targets), np.max(targets)
                bucket_size = (maxi - mini) / num_buckets
                self.buckets = np.array(
                    [[mini + i * bucket_size, mini + (i + 1) * bucket_size] for i in range(num_buckets)])
        except ValueError:
            self.buckets = None

        if self.buckets is None:
            _LOGGER.warning("Unable to bucket targets, attempting with continuous values")
            return targets
        targets = np.array(targets)
        targets = targets[:, None]

        return np.argmax(np.logical_and(targets > self.buckets[:, 0][None,], targets < self.buckets[:, 1][None,]),
                         axis=1)

    def score(self, test_data: list, test_targets: list):
        """ See superclass docstring """
        predictions = self.predict(test_data)
        L1_loss = np.mean(np.abs(np.array(test_targets) - predictions))
        bucketed_targets = self._bucket_targets(targets=test_targets, train=False)
        bucketed_output = self._bucket_targets(targets=predictions, train=False)
        # print(bucketed_output, bucketed_targets)
        precision = -1  # calculate_precision(bucketed_targets, bucketed_output)
        accuracy = np.mean(bucketed_targets == bucketed_output)

        return ModelOutputsGeneric(accuracy=accuracy, precision=precision, L1_loss=L1_loss)
