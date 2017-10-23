import ClimateEvalAPI


class MockModelFile(ClimateEvalAPI.ModelFile):

    def __init__(self, netcdf_file: str):
        super(MockModelFile, self).__init__(netcdf_file)
        #self.netcdf_file_path = netcdf_file


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

    @classmethod  # I dont know if this actually works having abstract class methods, but you get the idea.
    @abstractmethod
    def load(cls, file_path: str) -> ModelFile:
        """
        Loads the specified ModelFile at the location.
        Returns:
            An instance of ModelFile as stored at the specified locaion.

        Raises:
            IOError: in the case of unable to load the file.
            NotModelFileException: In the case that the specified file does not contain a model file.

        """
