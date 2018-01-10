from ExpertRep.abstract.ModelAPI import MachineLearningModel, ModelOutputs, ModelInfo
from abc import ABCMeta, abstractmethod


class UnsupervisedBase(metaclass=ABCMeta):
    @abstractmethod
    def fit(self, data: list) -> None:
        """
        """

    @abstractmethod
    def predict(self, data: list) -> list:
        """
        """


class SemiSupervisedModel(MachineLearningModel):
    def __init__(self, supervised, unsupervised, *args, **kwargs):
        super().__init__()
        self.supervised = supervised(*args, **kwargs)
        self.unsupervised = unsupervised()
        self.unsupervised_fitted = False

    def evaluate_and_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        data_projected = self.unsupervised.predict(data)
        return self.supervised.evaluate_and_fit(data_projected, targets, *args, **kwargs)

    def partial_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        data_projected = self.unsupervised.predict(data)
        return self.supervised.partial_fit(data_projected, targets, *args, **kwargs)

    def fit_unsupervised(self, data):
        self.unsupervised.fit(data)

    @property
    def model_info(self) -> ModelInfo:
        return self.supervised.model_info

    def score(self, test_data: list, test_targets: list) -> ModelOutputs:
        return self.supervised.score(test_data, test_targets)

    def predict(self, data: list) -> list:
        data_projected = self.unsupervised.predict(data)
        return self.supervised.predict(data_projected)

    def fit(self, data: list, targets: list, *args, **kwargs):
        self.supervised.fit(data, targets, *args, **kwargs)


def add_unsupervised(unsupervised_algo):
    def decorator(cls):
        cls.unsupervised = unsupervised_algo
        return lambda *args, **kwargs: SemiSupervisedModel(cls, unsupervised_algo, *args, **kwargs)

    return decorator
