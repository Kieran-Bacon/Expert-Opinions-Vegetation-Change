"""
A module containing some simple KNN implementations for demonstration of the Machine Learning API.
"""
from sklearn.neural_network.multilayer_perceptron import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor

from ExpertRep.abstract.ClimateEvalAPI import ModelInfo, ModelType
from ExpertRep.registry.model_registry import Registry
from ExpertRep.tools.unsupervised_helper import SemiSupervisedModel
from ExpertRep.machine_learning_models.unsupervised import PCA, PCANPickle
from ExpertRep.tools.skbase_model import SKBase
from sklearn.gaussian_process import GaussianProcessRegressor


@Registry.register_model("MLP_regress")
class MLPRegress(SKBase):
    """
    A MLP regression implementation.
    """

    def __init__(self, config):
        super().__init__(MLPRegressor)

    @property
    def model_info(self) -> ModelInfo:
        """ See superclass docstring """
        return ModelInfo(ModelType.KNN, None)


@Registry.register_model("MLP_regress_PCA")
class MLPRegressWithPCA(SemiSupervisedModel):
    """                                                                                                                                                                              
    An implementation of KNN regression with an added PCA feature learning step.                                                                                                     
    """

    def __init__(self, config):
        super().__init__(supervised=MLPRegress, unsupervised=PCA, config=config)


@Registry.register_model("RF_regress")
class RFRegress(SKBase):
    """
    A Random Forrest regression implementation.
    """

    def __init__(self, config):
        super().__init__(RandomForestRegressor)

    @property
    def model_info(self) -> ModelInfo:
        """ See superclass docstring """
        return ModelInfo(ModelType.KNN, None)


@Registry.register_model("RF_regress_PCA")
class RFRegressWithPCA(SemiSupervisedModel):
    """
    A implementation of Random forrest regression with an added PCA feature learning step.
    """

    def __init__(self, config):
        super().__init__(supervised=RFRegress, unsupervised=PCA, config=config)


@Registry.register_model("GBT_regress")
class GBTRegress(SKBase):
    """
    A gradient boosted treest regression implementation.
    """

    def __init__(self, config):
        super().__init__(GradientBoostingRegressor)

    @property
    def model_info(self) -> ModelInfo:
        """ See superclass docstring """
        return ModelInfo(ModelType.KNN, None)


@Registry.register_model("GBT_regress_PCA")
class GBTRegressWithPCA(SemiSupervisedModel):
    """
    A implementation of gradient boosted trees regression with an added PCA feature learning step.
    """

    def __init__(self, config):
        super().__init__(supervised=GBTRegress, unsupervised=PCA, config=config)


@Registry.register_model("GP_regress")
class GPRegress(SKBase):
    """
    A gradient boosted treest regression implementation.
    """

    def __init__(self, config):
        super().__init__(GaussianProcessRegressor)

    @property
    def model_info(self) -> ModelInfo:
        """ See superclass docstring """
        return ModelInfo(ModelType.KNN, None)


@Registry.register_model("GP_regress_PCA")
class GPRegressWithPCA(SemiSupervisedModel):
    """
    A implementation of gradient boosted trees regression with an added PCA feature learning step.
    """

    def __init__(self, config):
        super().__init__(supervised=GPRegress, unsupervised=PCA, config=config)


@Registry.register_model("MeanBaseline")
class MeanBaseline(SKBase):
    def __init__(self, config):
        super().__init__(lambda: None)
        self.mean = None

    def fit(self, data, targets, *args, **kwargs):
        self.mean = sum(targets) / len(targets)

    def predict(self, data):
        return [self.mean for _ in data]

    @property
    def model_info(self) -> ModelInfo:
        """ See superclass docstring """
        return ModelInfo(ModelType.KNN, None)


@Registry.register_model("DummyModelSavePC")
class DummyModelSavePC(SemiSupervisedModel):
    def __init__(self, config):
        super().__init__(supervised=MeanBaseline, unsupervised=PCANPickle, config=config)
