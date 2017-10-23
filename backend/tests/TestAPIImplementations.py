import unittest
from backend.netcdf_file import NetCDFFile
import numpy as np

# TODO import implementations and add them to the following lists

MODEL_FILE_IMPLEMENTATIONS_TO_TEST = []
API_IMPLEMENTATIONS_TO_TEST = []

class TestModelFiles(unittest.TestCase):
    def setUp(self):
        model_file_instances = []

    def test_initialise_save_and_load(self):
        f1 = NetCDFFile("/root/code/model_outputs/JULES-ES.1p6.vn4.8.spinup_50.dump_vegfrac.18800101.0.nc")
        f1.save("x.pkl")
        f2 = NetCDFFile.load("x.pkl")
        self.assertTrue(np.allclose(f1.get_numpy_arrays(), f2.get_numpy_arrays(), equal_nan=True))


if __name__ == '__main__':
    unittest.main()
