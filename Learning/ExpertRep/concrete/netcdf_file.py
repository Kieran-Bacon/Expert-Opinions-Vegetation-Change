"""
Implements the ModelFile class for use with NetCDF files.
"""
import warnings
import numpy as np

from netCDF4 import Dataset

from ExpertRep.abstract.ClimateEvalAPI import ModelFile
from ExpertRep.tools.geojson_gen import dict_to_geojson


class NetCDFFile(ModelFile):
    def __init__(self, netcdf_file: str, initialise=True):
        super(NetCDFFile, self).__init__(netcdf_file=netcdf_file)
        if initialise:
            dataset = Dataset(netcdf_file, "r", format="NETCDF4")
            self.numpy_arrays = np.array(dataset.variables['frac'])
            self.lat = np.array(dataset.variables['latitude'])
            self.lon = np.array(dataset.variables["longitude"])
            dataset.close()
        else:
            self.numpy_arrays = None
            self.lat = None
            self.lon = None
        self.sparse = None

    def get_numpy_arrays(self, layer: int = -1, resize_to: tuple = None, remove_nan=True) -> np.array:
        if resize_to is not None:
            raise NotImplementedError("Not yet implemented")
        if layer == -1:
            arrays = self.numpy_arrays
        else:
            arrays = self.numpy_arrays[layer]

        if remove_nan:
            nan_mask = np.isnan(arrays)
            arrays = np.array(arrays, copy=True)
            arrays[nan_mask] = 0

        return arrays

    def get_info(self) -> dict:
        raise NotImplementedError("Not yet implemented")

    def get_geojson(self, layer_id: int) -> str:
        if True: #TODO(BEN) WTF this caching thing is broken. shuld be self.sparse is None
            self.sparse = [dict() for _ in range(self.numpy_arrays.shape[0])]
            with warnings.catch_warnings():
                # The warning produced by undefined behaviour on self.numpy_arrays > 1e-5
                # for NAN values is dealt with by the previous clause.
                warnings.filterwarnings("ignore", category=RuntimeWarning)

                vals = np.where(np.logical_and(np.logical_not(np.isnan(self.numpy_arrays)), self.numpy_arrays > 1e-5))
            for layer, i, j in zip(*vals):
                self.sparse[layer][(self.lat[i], self.lon[j])] = self.numpy_arrays[layer, i, j]
        return list(map(dict_to_geojson, self.sparse))[layer_id]

    def save(self, file_path: str) -> None:
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, np.array([self.netcdf_file_path]))
            np.save(file_obj, self.sparse)
            np.save(file_obj, self.numpy_arrays)
            np.save(file_obj, self.lat)
            np.save(file_obj, self.lon)

    def __hash__(self):
        return hash((self.numpy_arrays.data.tobytes(), self.lat.tobytes(), self.lon.tobytes()))

    def __eq__(self, other):
        return (np.allclose(self.get_numpy_arrays(), other.get_numpy_arrays(), equal_nan=True) and
                np.allclose(self.lat, other.lat, equal_nan=True) and
                np.allclose(self.lon, other.lon, equal_nan=True))

    @classmethod
    def load(cls, file_path: str) -> "ModelFile":
        with open(file_path, "rb") as file_obj:
            str_array = np.load(file_obj)
            instance = cls(str(str_array[0]), initialise=False)
            instance.sparse = np.load(file_obj)
            numpy_arrays = np.load(file_obj)
            instance.numpy_arrays = numpy_arrays
            instance.lat = np.load(file_obj)
            instance.lon = np.load(file_obj)
            return instance
