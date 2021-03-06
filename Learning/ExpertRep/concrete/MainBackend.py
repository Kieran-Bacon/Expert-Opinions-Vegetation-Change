"""
A simple non-restful implementation of the ModelAPI class.
"""
import os
import logging

from ExpertRep.tools.locked_file import LockedFile
from ExpertRep.abstract.ClimateEvalAPI import VegetationMachineLearningAPI, ModelOutputs, ModelInfo, \
    ModelDoesNotExistException
from ExpertRep.abstract.ModelAPI import MachineLearningModel
from ExpertRep.registry.model_registry import Registry
import ExpertRep.machine_learning_models  # pylint disable=unused-import



# This previous line is required for the registry.

_MODEL_FILE_NAME = "Model_num_{}.vegml"

try:
    _veg_ml_dir = os.environ["EXPERTLOCATION"]
except:

    logging.warning("Expert location has not been set, defaulting to home directory."
    "Set EXPERTLOCATION environment variable.")
    _veg_ml_dir = "~/.ExpertClimateSystem/"

os.makedirs(_veg_ml_dir, exist_ok=True)

_MODEL_REGISTRY = "model_registry.nlsv"

_LOG = logging.getLogger(__name__)


class Backend(VegetationMachineLearningAPI):
    """ A simple backend implementation for training and evaluating Machine Learning models. """
    MODEL_TYPE_TO_CLASS = Registry()

    def __init__(self):
        self.registry_file = LockedFile(os.path.join(_veg_ml_dir, _MODEL_REGISTRY), is_binary=False)
        try:
            self.models_that_exist = self.registry_file.read().split()
        except FileNotFoundError:
            _LOG.info("Creating model_registry file")
            self.registry_file.write("")
            self.models_that_exist = []

        self.open_models = dict()

    def _check_and_load_if_not_loaded(self, *, model_id: str):
        if model_id in self.open_models:
            return True
        if model_id in self.models_that_exist:
            self._load_model(model_id=model_id)
            return True
        return False

    def _save_model(self, *, model_id: str):
        if model_id not in self.open_models:
            return  # why would we save a model that isn't open and therefore hasn't been modified
        file_name = os.path.join(_veg_ml_dir, _MODEL_FILE_NAME.format(model_id))
        locked_file = LockedFile(filename=file_name, is_binary=True)
        serialised_model = self.open_models[model_id].serialize()
        locked_file.write(serialised_model)

    def _load_model(self, *, model_id: str):
        file_name = os.path.join(_veg_ml_dir, _MODEL_FILE_NAME.format(model_id))
        locked_file = LockedFile(filename=file_name, is_binary=True)
        serialised_model = locked_file.read()
        self.open_models[model_id] = MachineLearningModel.deserialize(serialised_model)

    def _generate_id(self) -> str:
        """
        Finds the smallest unused ID in hex.
        """
        identifier = 0
        while hex(identifier) in self.models_that_exist:
            identifier += 1
        identifier = hex(identifier)
        self.models_that_exist.append(identifier)
        self.registry_file.write("{}\n".format(identifier), append=True)
        return identifier

    def create_model(self, *, model_type: str, config: dict = None) -> str:
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
        model_instance = self.MODEL_TYPE_TO_CLASS[model_type](config)
        self.open_models[identifier] = model_instance
        self._save_model(model_id=identifier)
        return identifier

    def delete_model(self, *, model_id: str) -> None:
        """
        Given the models unique identifier this will delete the model and all of its associated data.

        Args:
            model_id (str): The models unique identifier.

        Raises:
            ModelDoesNotExistException: In the case that the model does not exist.
        """
        self._check_and_load_if_not_loaded(model_id=model_id)

        def remove_from_registry(model_ids: str):
            """ Removes an item from the local models """
            mid = model_ids.split("\n")
            mid.remove(model_id)
            return "\n".join(mid)

        self.models_that_exist.remove(model_id)

        self.registry_file.read_and_write(remove_from_registry)
        os.remove(os.path.join(_veg_ml_dir, _MODEL_FILE_NAME.format(model_id)))

    def partial_fit(self, *, model_id: str, data: list, targets: list) -> ModelOutputs:
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
        if not self._check_and_load_if_not_loaded(model_id=model_id):
            raise ModelDoesNotExistException("The model with id: {} does not exist!!".format(model_id))

        model_out = self.open_models[model_id].partial_fit(data=data, targets=targets)
        self._save_model(model_id=model_id)

        return model_out

    def predict(self, *, model_id: str, data: list) -> list:
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

    def get_model_info(self, *, model_id: str) -> ModelInfo:
        """
        Gets the info that the concrete knows about the model in the form of a ModelInfo object.

        Args:
            model_id (str): The unique model identifier for which info is requested.

        Returns:
            ModelInfo object containing information about the model.

        Raises:
            ModelDoesNotExistException
        """
        if not self._check_and_load_if_not_loaded(model_id=model_id):
            raise ModelDoesNotExistException("The model with id: {} does not exist!!".format(model_id))

        return self.open_models[model_id].model_info()

    def close_model(self, *, model_id: str) -> None:
        """
        Tells the concrete to close the m
        Args:
            model_id:

        Returns:

        """
        if model_id in self.open_models:
            del self.open_models[model_id]

    def fit_unsupervised(self, *, model_id: str, data: list) -> None:
        """
        # TODO(BEN)
        Raises:
            ModelDoesNotExistException
        """

        if not self._check_and_load_if_not_loaded(model_id=model_id):
            raise ModelDoesNotExistException("The model with id: {} does not exist!!".format(model_id))
        self.open_models[model_id].fit_unsupervised(data)
        self._save_model(model_id=model_id)
