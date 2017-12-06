from VegML.abstract.ModelAPI import MachineLearningModel
import logging

_LOG = logging.getLogger(__name__)

_MODELS = {}


class NotASubclassException(Exception):
    pass


class Registry:
    @staticmethod
    def register_model(name):
        def decorator(veg_ml_model, name):
            _LOG.info("Registered Model name {}".format(name))
            if not issubclass(veg_ml_model, MachineLearningModel):
                raise NotASubclassException(
                    "The class {} is not a subclass of MachineLearningModel".format(veg_ml_model.__class__))
            model_name = name or veg_ml_model.__class__
            if model_name in _MODELS:
                raise LookupError("Model %s already registered." % model_name)
            _MODELS[model_name] = veg_ml_model
            return veg_ml_model

        return lambda model_cls: decorator(model_cls, name)

    def __getitem__(self, name):
        if name not in _MODELS:
            raise LookupError("Model %s never registered." % name)
        return _MODELS[name]

    def __contains__(self, name):
        return name in _MODELS
