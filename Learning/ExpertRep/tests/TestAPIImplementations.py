import unittest
from VegML import ClimModel
from VegML import VegML
from VegML.abstract.ModelAPI import ModelOutputs
import numpy as np

TEST_NC = "/root/code/VegML/test_model_outputs/JULES-ES.1p6.vn4.8.spinup_50.dump_vegfrac.18800101.0.nc"


class TestModelFiles(unittest.TestCase):
    def test_initialise_save_and_load(self):
        f1 = ClimModel(TEST_NC)
        f1.save("~/x.pkl")
        f2 = ClimModel.load("~/x.pkl")
        self.assertTrue(np.allclose(f1.get_numpy_arrays(), f2.get_numpy_arrays(), equal_nan=True))


class TestAPI(unittest.TestCase):
    def test_initialise_create_and_train(self):
        model = VegML()
        model_id = model.create_model(model_type="KNN")
        self.assertIn(model_id, model.models_that_exist)
        self.assertIn(model_id, model.open_models)

        model.close_model(model_id=model_id)

        self.assertIn(model_id, model.models_that_exist)
        self.assertNotIn(model_id, model.open_models)

        train = [ClimModel(TEST_NC) for _ in range(10)]
        labels = [0 for _ in range(5)] + [1 for _ in range(5)]

        performance = model.partial_fit(model_id=model_id, data=train, targets=labels)

        self.assertIsInstance(performance, ModelOutputs)
        self.assertIsInstance(performance.accuracy, float)
        # random sample of the data is taken for test so no tighter guarantees as to the percentage it can get.
        self.assertTrue(0 <= performance.accuracy <= 1)

        predictions = np.array(model.predict(model_id=model_id, data=train))
        self.assertTrue(np.all(np.logical_xor(predictions == 0, predictions == 1)))

        model.close_model(model_id=model_id)
        predictions_2 = np.array(model.predict(model_id=model_id, data=train))
        self.assertTrue(np.all(predictions == predictions_2))

        model_id2 = model.create_model(model_type="KNN")
        self.assertNotEqual(model_id, model_id2)

        model.delete_model(model_id=model_id)
        model.predict(model_id=model_id, data=train)


if __name__ == '__main__':
    unittest.main()
