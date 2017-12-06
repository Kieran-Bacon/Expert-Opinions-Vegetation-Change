from ExpertRep.abstract.ModelAPI import MachineLearningModel
from ExpertRep.abstract.ClimateEvalAPI import ModelInfo, ModelType,ModelOutputs
from sklearn.neighbors import KNeighborsClassifier
from ExpertRep.registry.model_registry import Registry
import numpy as np


@Registry.register_model("KNN")
class KNN(MachineLearningModel):
    def __init__(self, config):
        super(KNN, self).__init__()
        self.knn = KNeighborsClassifier(n_neighbors=config.get("k", 5))

    @property
    def model_info(self) -> ModelInfo:
        return ModelInfo(ModelType.KNN, None)

    def partial_fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        super().partial_fit(data, targets, *args, **kwargs)

    def fit(self, data: list, targets: list, *args, **kwargs) -> ModelOutputs:
        data_arrays = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        self.knn.fit(data_arrays, targets)

    def predict(self, data: list) -> list:
        data_arrays = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        return self.knn.predict(data_arrays).tolist()
