"""
A module containing some simple KNN implementations for demonstration of the Machine Learning API.
"""
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

from ExpertRep.abstract.ClimateEvalAPI import ModelInfo, ModelType
from ExpertRep.registry.model_registry import Registry
from ExpertRep.tools.unsupervised_helper import SemiSupervisedModel
from ExpertRep.machine_learning_models.unsupervised import PCA
from ExpertRep.tools.skbase_model import SKBase


@Registry.register_model("KNN_classify")
class KNNClassify(SKBase):
    """ A KNN classification implementation.  """

    def __init__(self, config):
        super().__init__(lambda: KNeighborsClassifier(n_neighbors=config.get("k", 2)))

    @classmethod
    def desc(cls):
        return "KNN classifier"

    @property
    def model_info(self) -> ModelInfo:
        """ See superclass docstring """
        return ModelInfo(ModelType.KNN, None)


@Registry.register_model("KNN_classify_binary")
class KNNClassifyBinary(KNNClassify):
    """ A binary bucketed KNN """

    @classmethod
    def desc(cls):
        return "Binary KNN"

    @staticmethod
    def num_buckets():
        return 2


@Registry.register_model("KNN_regress")
class KNNRegress(SKBase):
    """
    A KNN regression implementation.
    """

    def __init__(self, config):
        super().__init__(lambda: KNeighborsRegressor(n_neighbors=config.get("k", 2)))

    @classmethod
    def desc(cls):
        return "KNN regressor"

    @property
    def model_info(self) -> ModelInfo:
        """ See superclass docstring """
        return ModelInfo(ModelType.KNN, None)


@Registry.register_model("BINARY_KNN_PCA")
class BinaryKNNWithPCA(SemiSupervisedModel):
    """                                                                                                                                                                              
    An implementation of KNN regression with an added PCA feature learning step.                                                                                                     
    """

    def __init__(self, config):
        super().__init__(supervised=KNNClassifyBinary, unsupervised=PCA, config=config)

    @classmethod
    def desc(cls):
        return "Binary KNN with PCA"


@Registry.register_model("KNN_PCA")
class KNNWithPCA(SemiSupervisedModel):
    """
    An implementation of KNN regression with an added PCA feature learning step.
    """

    def __init__(self, config):
        super().__init__(supervised=KNNRegress, unsupervised=PCA, config=config)

    @classmethod
    def desc(cls):
        return "KNN with principal component analysis"
