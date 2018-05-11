# pylint: skip-file
import os
import unittest
import numpy as np

from ExpertRep import ClimateModelOutput
from ExpertRep.tests.constants import TEST_NC, TEST_FOLDER

TEST_FILE = os.path.join(TEST_FOLDER, "x.pkl")


class TestModelFiles(unittest.TestCase):
    def test_KML_load(self):  # pylint: disable=no-self-use
        ClimateModelOutput(TEST_NC)

    def test_initialise_save_and_load(self):
        f1 = ClimateModelOutput(TEST_NC)
        print(f1.numpy_arrays.shape)
        f1.save(TEST_FILE)
        f2 = ClimateModelOutput.load(TEST_FILE)
        self.assertEqual(f1, f2)

    def test_equal(self):
        f1 = ClimateModelOutput(TEST_NC)
        f1.save(TEST_FILE)
        f2 = ClimateModelOutput.load(TEST_FILE)
        self.assertEqual(f1, f2)

        f2.lat[0] += 1
        self.assertNotEqual(f1, f2)

        f2 = ClimateModelOutput.load(TEST_FILE)
        f2.lon[0] += 1
        self.assertNotEqual(f1, f2)

        f2 = ClimateModelOutput.load(TEST_FILE)
        f2.numpy_arrays = np.zeros_like(f2.numpy_arrays)
        self.assertNotEqual(f1, f2)

        f2 = ClimateModelOutput.load(TEST_FILE)
        f2.sparse = "Some thing other than None"
        self.assertNotEqual(f1.sparse, f2.sparse)
        # But this should not affect equality
        self.assertEqual(f1, f2)

    def test_hash(self):
        f1 = ClimateModelOutput(TEST_NC)
        f1.save(TEST_FILE)
        hash_f1 = hash(f1)
        f2 = ClimateModelOutput.load(TEST_FILE)
        self.assertEqual(hash_f1, hash(f2))

        f2.lat[0] += 1
        self.assertNotEqual(hash_f1, hash(f2))

        dict_of_clim_mod = dict()
        dict_of_clim_mod[f1] = "a"
        dict_of_clim_mod[f2] = "b"
        self.assertEqual(dict_of_clim_mod[f1], "a")
        self.assertEqual(dict_of_clim_mod[f2], "b")

        f2 = ClimateModelOutput.load(TEST_FILE)
        f2.lon[0] += 1
        self.assertNotEqual(hash_f1, hash(f2))

        f2 = ClimateModelOutput.load(TEST_FILE)
        f2.numpy_arrays = np.zeros_like(f2.numpy_arrays)
        self.assertNotEqual(hash_f1, hash(f2))

        f2 = ClimateModelOutput.load(TEST_FILE)
        f2.sparse = "Some thing other than None"
        self.assertNotEqual(f1.sparse, f2.sparse)
        # But this should not affect equality
        self.assertEqual(hash_f1, hash(f2))

    def test_geojson(self):  # pylint: disable=no-self-use
        ClimateModelOutput(TEST_NC).get_geojson(0)
