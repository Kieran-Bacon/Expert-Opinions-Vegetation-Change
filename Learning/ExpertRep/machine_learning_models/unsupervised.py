"""
This module simply gives an example of an unsupervised algorithm. In this case by wrapping the
sklearn PCA implementation.
"""
import copy
import numpy as np

from sklearn.decomposition import PCA as SK_PCA

from ExpertRep.tools.unsupervised_helper import UnsupervisedBase


class PCA(UnsupervisedBase):
    """
    A simple adaptor for SKlearn PCA to the ExpertRep API.
    """

    def __init__(self):
        super().__init__()
        self.pca = SK_PCA(n_components=10)

    def fit(self, data: list) -> None:
        """
        See UnsupervisedBase for params
        """
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        self.pca.fit(data_array)

    def predict(self, data: list) -> list:
        """
        See UnsupervisedBase for params
        """
        data_array = [np.reshape(d.get_numpy_arrays(), [-1]) for d in data]
        projected_data = copy.deepcopy(data)
        for i, dat in enumerate(np.split(self.pca.transform(data_array), len(data))):
            projected_data[i].numpy_arrays = dat
        return projected_data
