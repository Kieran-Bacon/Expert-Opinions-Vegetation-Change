"""
Contains a nice wrapper for plug and play use of SKlearn Models with the ClimateLearning API.
"""
from abc import ABCMeta, abstractmethod

import numpy as np
from sklearn.base import is_classifier, is_regressor

from ExpertRep.abstract.ModelAPI import MachineLearningModel
from ExpertRep.abstract.ClimateEvalAPI import ModelOutputsClassify, ModelOutputsRegression


class SKBase(MachineLearningModel, metaclass=ABCMeta):
    """
    A class that given an instance of an sklearn model fills some of the functionality required to interface between an
     SKLearn supervised algorithm and the MachineLearningModel API.
    """

    def __init__(self, model):
        super().__init__()
        self.model = model

    def fit(self, data: list, targets: list, *args, **kwargs):
        """ See superclass docstring """
        data_arrays = self._reshape_to_2d(data)
        self.model.fit(data_arrays, targets)

    @abstractmethod
    def model_info(self):
        """ """

    def predict(self, data: list) -> list:
        """ See superclass docstring """
        data_arrays = self._reshape_to_2d(data)
        return self.model.predict(data_arrays).tolist()

    @staticmethod
    def _reshape_to_2d(data):
        """ See superclass docstring """
        return [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]

    def score(self, test_data: list, test_targets: list):
        """ See superclass docstring """
        test_data_array = self._reshape_to_2d(test_data)
        if is_classifier(self.model):
            return ModelOutputsClassify(accuracy=self.model.score(test_data_array, test_targets), precision=-1)
        elif is_regressor(self.model):
            return ModelOutputsRegression(R2=self.model.score(test_data_array, test_targets))
        else:
            raise Exception(
                "Not able to determine whether the model is classifier or regressor please override score method.")
