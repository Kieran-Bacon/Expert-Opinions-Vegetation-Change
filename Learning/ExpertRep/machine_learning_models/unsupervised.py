from ExpertRep.tools.unsupervised_helper import UnsupervisedBase

from sklearn.decomposition import PCA as Sklearn_PCA
import numpy as np
import copy


class PCA(UnsupervisedBase):
    def __init__(self):
        super().__init__()
        self.pca = Sklearn_PCA(n_components=10)

    def fit(self, data: list) -> None:
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        self.pca.fit(data_array)

    def predict(self, data: list):
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        projected_data = copy.deepcopy(data)
        for i, dat in enumerate(np.split(self.pca.transform(data_array), len(data))):
            projected_data[i].numpy_arrays = dat
        return projected_data
