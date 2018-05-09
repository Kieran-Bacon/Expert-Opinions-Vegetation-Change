"""
This module implements a simple registry for registering machine learning models for use with the API.
"""
import logging
from ExpertRep.abstract.ModelAPI import MachineLearningModel

_LOG = logging.getLogger(__name__)

_MODELS = {}


class NotASubclassException(Exception):
    pass


def available_models():
    """
    Returns a list of the available models by their string keys.

    >>> @Registry.register_model("test")
    ... class TestModel(MachineLearningModel): pass
    >>> available_models()
    {'test': 'TestModel'}
    """
    return {title: model.desc() for title, model in _MODELS.items()}


class Registry:
    """
    This registry allows for registering machine learning models for use with the API. To use it, decorate with

    >>> @Registry.register_model("test")
    ... class TestModel(MachineLearningModel): pass
    >>> "test" in Registry()
    True
    >>> Registry()["test"] is TestModel
    True
    >>> "not_a_model_" in Registry()
    False

    """

    @staticmethod
    def register_model(name: str):
        """
        The decorator used for registering the models, see above.

        Args:
            name: A string that is used to access the models via the API.

        Returns:


        """

        def decorator(veg_ml_model) -> MachineLearningModel:
            """
            Adds the model to the registry and otherwise acts as an identity function.

            Args:
                veg_ml_model: A subclass of MachineLearningModel to add to the registry.

            Returns:
                veg_ml_model

            """
            _LOG.info("Registered Model name %s", name)
            if not issubclass(veg_ml_model, MachineLearningModel):
                raise NotASubclassException(
                    "The class {} is not a subclass of MachineLearningModel".format(veg_ml_model.__class__))
            model_name = name or veg_ml_model.__class__
            _MODELS[model_name] = veg_ml_model
            return veg_ml_model

        return decorator

    def __getitem__(self, name: str) -> MachineLearningModel:
        """
        For getting a registered model by name.

        Args:
            name: The string name of the model.

        Returns:


        """
        if name not in _MODELS:
            raise LookupError("Model %s never registered." % name)
        return _MODELS[name]

    def __contains__(self, name) -> bool:
        """
        For verifying the existance of a model by name using the "in" keyword.

        Args:
            name: The string name of the model.

        Returns:
            bool. True if the model exists.

        """
        return name in _MODELS
