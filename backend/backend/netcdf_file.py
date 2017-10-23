from netCDF4 import Dataset
import numpy as np
from ClimateEvalAPI import ModelFile


class NetCDFFile(ModelFile):
    def __init__(self, netcdf_file: str, initialise=True):
        super(NetCDFFile, self).__init__(netcdf_file=netcdf_file)
        if initialise:
            dataset = Dataset(netcdf_file, "r", format="NETCDF4")
            self.numpy_arrays = np.array(dataset.variables['frac'])
            dataset.close()

    def get_numpy_arrays(self, layer: int = -1, resize_to: tuple = None) -> np.array:
        if resize_to is not None:
            raise NotImplemented("Not yet implemented")
        if layer == -1:
            return self.numpy_arrays
        else:
            return self.numpy_arrays[layer]

    def get_info(self) -> dict:
        raise NotImplemented("Not yet implemented")

    def save(self, file_path: str) -> None:
        with open(file_path, "wb") as f:
            np.save(f, np.array([self.netcdf_file_path]))
            np.save(f, self.numpy_arrays)

    @classmethod
    def load(cls, file_path: str) -> "ModelFile":
        with open(file_path, "rb") as f:
            str_array = np.load(f)
            numpy_arrays = np.load(f)
            instance = cls(str(str_array[0]), initialise=False)
            instance.numpy_arrays = numpy_arrays
            return instance

