from ClimateEvalAPI import VegetationMachineLearningAPI, ModelType, ModelFile, ModelOutputs, ModelInfo, \
    ModelDoesNotExistException
from sklearn.neighbors import KNeighborsClassifier
import warnings
import numpy as np


class Backend(VegetationMachineLearningAPI):
    MODEL_TYPE_TO_CLASS = {
        ModelType.KNN: KNeighborsClassifier
    }

    def __init__(self):
        self.open_models = dict()
        self.models_that_exist = []

    def _check_and_load_if_not_loaded(self, *, model_id: str):
        if model_id in self.open_models:
            return True
        if model_id in self.models_that_exist:
            # TODO Load the model from file here.
            raise NotImplemented("This functionality is currently not implemented")
            return True
        return False

    def _generate_id(self) -> str:
        """
        Finds the smallest unused ID in hex.
        """
        identifier = 0
        while identifier not in self.models_that_exist:
            identifier += 1
        self.models_that_exist.append(identifier)
        return hex(identifier)

    def create_model(self, model_type: ModelType, config: dict = None) -> str:
        """
        Given a model type this method returns a unique string identifier to the new model,
         this can be stored in a database or used however is wanted.
        Args:
            model_type (ModelType): A model type.
            config (dict): Any optional hyperparameters that are desired to be modified from the model standard.

        Returns:
            A unique string identifier of the model.
        """
        identifier = self._generate_id()
        config = config or {}
        model_instance = self.MODEL_TYPE_TO_CLASS[model_type](**config)
        self.open_models[identifier] = model_instance

    def delete_model(self, model_id: str) -> None:
        """
        Given the models unique identifier this will delete the model and all of its associated data.

        Args:
            model_id (str): The models unique identifier.

        Raises:
            ModelDoesNotExistException: In the case that the model does not exist.
        """

    def partial_fit(self, model_id: str, data: list, targets: list) -> ModelOutputs:  # Django style forward referencing
        """
        Fits the chosen model on the given data. This method is responsible for performing any kind of
        X-validation and will return the values of this self-evaluation.
        Args:
            model_id (str): The unique model idenfitier to be trained.
            data : A list of ModelFile objects OR a list of strings where ModelFile objects can be found.
            targets: A list of score values in the interval [0, 5) for the model. Can be int or float.

        Returns:
            An instance of ModelOutputs object containing the training results, eg, final accuracy or precision ect?

        Raises:
            ModelDoesNotExistException
        """

        warnings.warn("Partial fit is not fully implemented, results may be undesirable")

        if not self._check_and_load_if_not_loaded(model_id=model_id):
            raise ModelDoesNotExistException("The model with id: {} does not exist!!".format(model_id))

        train, test = (data[:len(data) // 2], data[:len(data) // 2]), (data[len(data) // 2:], data[len(data) // 2:])
        self.open_models[model_id].fit(*train)
        predicted = self.open_models[model_id].predict(test[0])
        return ModelOutputs(accuracy=np.mean(predicted == test[1]), precision=None)

    def predict(self, model_id: str, data: list) -> list:
        """
        Runs prediction on the model with the specified ID.

        Args:
            model_id (str): The unique model identifier to be predicted on.
            data : A list of ModelFile objects OR a list of strings where ModelFile objects can be found.

        Returns:
            targets: A list of score values in the interval [0, 5) for the model. Can be int or float.

        Raises:
            ModelNotTrainedException
            ModelDoesNotExistException
        """
        if not self._check_and_load_if_not_loaded(model_id=model_id):
            raise ModelDoesNotExistException("The model with id: {} does not exist!!".format(model_id))

        return self.open_models[model_id].predict(data)

    def get_model_info(self, model_id: str) -> ModelInfo:
        """
        Gets the info that the backend knows about the model in the form of a ModelInfo object.

        Args:
            model_id (str): The unique model identifier for which info is requested.

        Returns:
            ModelInfo object containing information about the model.

        Raises:
            ModelDoesNotExistException
        """
        if not self._check_and_load_if_not_loaded(model_id=model_id):
            raise ModelDoesNotExistException("The model with id: {} does not exist!!".format(model_id))

        raise NotImplemented("This functionality is currently not implemented")

    def close_model(self, model_id: str) -> None:
        """
        Tells the backend to close the m
        Args:
            model_id:

        Returns:

        """
        warnings.warn("Currently, this closes the models for good as persistence has not been yet implemented, sorry!!")
        del self.open_models[model_id]
