# thanks. I realise I forgot to cache the kml files which isn't a big deal but 
# can you put a #TODO in there plz


from netCDF4 import Dataset
import numpy as np
from ExpertRep.abstract.ClimateEvalAPI import ModelFile
from ExpertRep.tools.KML_gen import dict_to_KML


class NetCDFFile(ModelFile):
    def __init__(self, netcdf_file: str, initialise=True):
        super(NetCDFFile, self).__init__(netcdf_file=netcdf_file)
        if initialise:
            dataset = Dataset(netcdf_file, "r", format="NETCDF4")
            self.numpy_arrays = np.array(dataset.variables['frac'])
            self.lat = np.array(dataset.variables['latitude'])
            self.lon = np.array(dataset.variables["longitude"])
            dataset.close()

    def get_numpy_arrays(self, layer: int = -1, resize_to: tuple = None, remove_nan=True) -> np.array:
        if resize_to is not None:
            raise NotImplemented("Not yet implemented")
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
        raise NotImplemented("Not yet implemented")

    def get_kml(self):
        sparse = [dict() for _ in range(self.numpy_arrays.shape[0])]
        vals = np.where(np.logical_and(np.logical_not(np.isnan(self.numpy_arrays)), self.numpy_arrays > 1e-5))
        for layer, i, j in zip(*vals):
            sparse[layer][(self.lat[i], self.lon[j])] = self.numpy_arrays[layer, i, j]
        return list(map(dict_to_KML, sparse))

    def save(self, file_path: str) -> None:
        with open(file_path, "wb") as f:
            np.save(f, np.array([self.netcdf_file_path]))
            np.save(f, self.numpy_arrays)
            np.save(f, self.lat)
            np.save(f, self.lon)

    def __hash__(self):
        return hash(self.numpy_arrays.data.tobytes())

    @classmethod
    def load(cls, file_path: str) -> "ModelFile":
        with open(file_path, "rb") as f:
            str_array = np.load(f)
            numpy_arrays = np.load(f)
            instance = cls(str(str_array[0]), initialise=False)
            instance.numpy_arrays = numpy_arrays
            instance.lat = np.load(f)
            instance.lon = np.load(f)
            return instance
