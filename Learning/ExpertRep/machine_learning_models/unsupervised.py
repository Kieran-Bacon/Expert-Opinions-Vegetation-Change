"""
This module simply gives an example of an unsupervised algorithm. In this case by wrapping the
sklearn PCA implementation.
"""
import copy
import numpy as np
import pickle

from sklearn.decomposition import PCA as SK_PCA

from ExpertRep.tools.unsupervised_helper import UnsupervisedBase
from ExpertRep.abstract.ClimateEvalAPI import ModelNotTrainedException


class PCA(UnsupervisedBase):
    """
    A simple adaptor for SKlearn PCA to the ExpertRep API.
    """

    def __init__(self):
        super().__init__()
        self.pca = SK_PCA(n_components=0.95)
        self.fitted = False

    def fit(self, data: list) -> None:
        """
        See UnsupervisedBase for params
        """
        self.fitted = True
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        self.pca.fit(data_array)

    def predict(self, data: list) -> list:
        """
        See UnsupervisedBase for params
        """
        if not self.fitted:
            raise ModelNotTrainedException("Model not fitted, call fit before predict")
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        projected_data = copy.deepcopy(data)
        for i, dat in enumerate(np.split(self.pca.transform(data_array), len(data))):
            projected_data[i].numpy_arrays = dat
        return projected_data

class PCANPickle(UnsupervisedBase):
    """
    A simple adaptor for SKlearn PCA to the ExpertRep API.
    """

    def __init__(self):
        super().__init__()
        self.pca = SK_PCA(n_components=99.9)
        self.saved = False

    def fit(self, data: list) -> None:
        """
        See UnsupervisedBase for params
        """
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        self.pca.fit(data_array)
        components = self.pca.components_
        variance = self.pca.explained_variance_ratio_
        if not self.saved:
            self.saved = True
            with open("PCA_DATA.pkl", "wb") as fp:
                pickle.dump((components, variance), fp)


    def predict(self, data: list) -> list:
        """
        See UnsupervisedBase for params
        """
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        projected_data = copy.deepcopy(data)
        for i, dat in enumerate(np.split(self.pca.transform(data_array), len(data))):
            projected_data[i].numpy_arrays = dat
        return projected_data
