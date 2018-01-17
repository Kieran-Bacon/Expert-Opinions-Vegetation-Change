"""
This module gives functionality to easily add unsupervised feature extraction methods to the model pipeline.
"""
from abc import ABCMeta, abstractmethod
from ExpertRep.abstract.ModelAPI import MachineLearningModel, ModelOutputs, ModelInfo


class UnsupervisedBase(metaclass=ABCMeta):
    """
    A base class for an unsupervised feature learning algorithm. For use with the decorator or SemiSupervisedModel
     class below.
    """

    @abstractmethod
    def fit(self, data: list) -> None:
        """
        This method fits the unsupervised algorithm and is called by the fit_unsupervised method.

        Args:
            data (list): A list of ModelOutputs

        """

    @abstractmethod
    def predict(self, data: list) -> list:
        """
        This method transforms the data into its feature representation that is used for the supervised section of the
        algorithm.

        Args:
            data (list): A list of ModelOutputs
        Returns:
             data (list): A list of ModelOutputs that has been transformed by some transformation.
        """


class SemiSupervisedModel(MachineLearningModel):
    """
    A wrapper that simplifies the unification of supervised classifers/regressors and the unsupervised
    embedding/projection.
    """

    def __init__(self, supervised, unsupervised, *args, **kwargs):
        """
        Note:
             No arguments can be passed to the unsupervised algorithm. Any hyperparams must be preset or found via
        cross validation in the fit method.

        Args:
            supervised (subclass of MachineLearningModel): A subclass of MachineLearningModel that forms the supervised
                section of the machine learning algorithm.
            unsupervised (subclass of UnsupervisedBase): A subclass of UnsupervisedBase that forms the unsupervised
                section of the machine learning algorithm.
            args: Passed to the supervised algorithm.
            kwargs: passed to the supervised algorithm
        """
        super().__init__()
        self.supervised = supervised(*args, **kwargs)
        self.unsupervised = unsupervised()
        self.unsupervised_fitted = False

    def evaluate_and_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        """
        See parent class MachineLearningModel for params
        """
        data_projected = self.unsupervised.predict(data)
        return self.supervised.evaluate_and_fit(data_projected, targets, *args, **kwargs)

    def partial_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        """
        See parent class MachineLearningModel for params
        """
        data_projected = self.unsupervised.predict(data)
        return self.supervised.partial_fit(data_projected, targets, *args, **kwargs)

    def fit_unsupervised(self, data):
        """
        See parent class MachineLearningModel for params
        """
        self.unsupervised.fit(data)

    @property
    def model_info(self) -> ModelInfo:
        """
        See parent class MachineLearningModel for params
        """
        return self.supervised.model_info

    def score(self, test_data: list, test_targets: list) -> ModelOutputs:
        """
        See parent class MachineLearningModel for params
        """
        return self.supervised.score(test_data, test_targets)

    def predict(self, data: list) -> list:
        """
        See parent class MachineLearningModel for params
        """
        data_projected = self.unsupervised.predict(data)
        return self.supervised.predict(data_projected)

    def fit(self, data: list, targets: list, *args, **kwargs):
        """
        See parent class MachineLearningModel for params
        """
        self.supervised.fit(data, targets, *args, **kwargs)
