"""
This file represents a proposed API for the Climate Model Vegetation evaluation project.

This is set up to facilitate this API to interact with the backend implementation via a
single instance of the system run on the same server in a "package" fashion. But also to
allow easy extensibility to run on remote systems or as a cluster setup (with shared file system)
with a load balancing system.

Author: Ben Townsend
"""
from enum import Enum
import numpy as np
from abc import ABCMeta, abstractmethod
from collections import namedtuple


class NotModelFileException(Exception):
    pass


class ModelDoesNotExistException(Exception):
    pass


class ModelNotTrainedException(Exception):
    pass


class ModelFile:
    def __init__(self, netcdf_file: str):
        self.netcdf_file_path = netcdf_file

    @abstractmethod
    def get_numpy_arrays(self, layer: int = -1, resize_to: tuple = None) -> np.array:
        """

        Args:
            layer (int): Represents the [0, num_layers) netcdf layer ID of which to return
            resize_to: A tuple of the dimensions to resize the returned array to.

        Returns:
            A numpy array of rank 2 if layer is set representing the values of that layer.
                dimensions = [lat, long]
            or A numpy array of rank 3 if the layer is not set.
                dimensions = [layers, lat, long]
        """

    @abstractmethod
    def get_info(self) -> dict:
        """
        This method returns a dictionary containing the metadata about the netcdf files.

        Returns:
            A dict containing metadata fields.
        """

    @abstractmethod
    def save(self, file_path: str) -> None:
        """
        Saves the ModelFile to the specified path.
        Args:
            file_path (str): An absolute filepath to the location to save the file.

        Returns:
            None

        Raises:
            IOError: in the case of unable to save the file
        """

    @classmethod
    @abstractmethod
    def load(cls, file_path: str) -> "ModelFile":
        """
        Loads the specified ModelFile at the location.
        Returns:
            An instance of ModelFile as stored at the specified locaion.

        Raises:
            IOError: in the case of unable to load the file.
            NotModelFileException: In the case that the specified file does not contain a model file.

        """


class ModelType(Enum):
    KNN = 0
    MLP = 1
    SVM = 2
    # ...


class ModelOutputs(namedtuple("ModelOutputs", ["accuracy", "precision"])):
    pass


class ModelInfo(namedtuple("ModelInfo", ["model_type", "model_outputs_from_last_train", "TODO"])):
    pass


class VegetationMachineLearningAPI(metaclass=ABCMeta):
    @abstractmethod
    def create_model(self, *, model_type: ModelType, config: dict = None) -> str:
        """
        Given a model type this method returns a unique string identifier to the new model,
         this can be stored in a database or used however is wanted.
        Args:
            model_type (ModelType): A model type.
            config (dict): Any optional hyperparameters that are desired to be modified from the model standard.

        Returns:
            A unique string identifier of the model.
        """

    @abstractmethod
    def delete_model(self, *, model_id: str) -> None:
        """
        Given the models unique identifier this will delete the model and all of its associated data.

        Args:
            model_id (str): The models unique identifier.

        Raises:
            ModelDoesNotExistException: In the case that the model does not exist.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def close_model(self, *, model_id: str) -> None:
        """
        Tells the concrete to close the m
        Args:
            model_id:

        Returns:

        """
