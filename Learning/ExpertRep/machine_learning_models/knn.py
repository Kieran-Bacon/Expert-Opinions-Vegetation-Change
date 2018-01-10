from ExpertRep.abstract.ModelAPI import MachineLearningModel
from ExpertRep.abstract.ClimateEvalAPI import ModelInfo, ModelType, ModelOutputsClassify, ModelOutputs, \
    ModelOutputsRegression
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from ExpertRep.registry.model_registry import Registry
from ExpertRep.tools.unsupervised_helper import SemiSupervisedModel
from ExpertRep.machine_learning_models.unsupervised import PCA

import numpy as np


class SKBase(MachineLearningModel):
    def partial_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        return super().partial_fit(data, targets, *args, **kwargs)

    def fit(self, data: list, targets: list, *args, **kwargs):
        data_arrays = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        self.model.fit(data_arrays, targets)

    def predict(self, data: list) -> list:
        data_arrays = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        return self.model.predict(data_arrays).tolist()



@Registry.register_model("KNN_classify")
class KNNClassify(SKBase):
    def __init__(self, config):
        super(KNNClassify, self).__init__()
        self.model = KNeighborsClassifier(n_neighbors=config.get("k", 2))

    @property
    def model_info(self) -> ModelInfo:
        return ModelInfo(ModelType.KNN, None)

    def score(self, test_data: list, test_targets: list):
        test_data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in test_data]
        return ModelOutputsClassify(accuracy=self.model.score(test_data_array, test_targets), precision=-1)


@Registry.register_model("KNN_regress")
class KNNRegress(SKBase):
    def __init__(self, config):
        super(KNNRegress, self).__init__()
        self.model = KNeighborsRegressor(n_neighbors=config.get("k", 2))

    @property
    def model_info(self) -> ModelInfo:
        return ModelInfo(ModelType.KNN, None)

    def score(self, test_data: list, test_targets: list):
        test_data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in test_data]
        return ModelOutputsRegression(R2=self.model.score(test_data_array, test_targets))


@Registry.register_model("KNN_PCA")
class KNNWithPCA(SemiSupervisedModel):
    def __init__(self, config):
        super().__init__(supervised=KNNRegress, unsupervised=PCA, config=config)
