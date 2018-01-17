# pylint: skip-file

import unittest
import numpy as np

from ExpertRep import ClimateModelOutput
from ExpertRep import ExpertModelAPI
from ExpertRep.abstract.ClimateEvalAPI import ModelOutputs
from ExpertRep.abstract.ClimateEvalAPI import ModelDoesNotExistException
from ExpertRep.tests.constants import TEST_NC


class TestAPI(unittest.TestCase):
    def test_initialise_create_and_train(self):
        model = ExpertModelAPI()
        model_id = model.create_model(model_type="KNN_classify")
        self.assertIn(model_id, model.models_that_exist)
        self.assertIn(model_id, model.open_models)

        model.close_model(model_id=model_id)

        self.assertIn(model_id, model.models_that_exist)
        self.assertNotIn(model_id, model.open_models)

        train = [ClimateModelOutput(TEST_NC) for _ in range(10)]
        labels = [0 for _ in range(5)] + [1 for _ in range(5)]

        performance = model.partial_fit(model_id=model_id, data=train, targets=labels)

        self.assertIsInstance(performance, ModelOutputs)
        self.assertIsInstance(performance.accuracy, float)
        self.assertTrue(0 <= performance.accuracy <= 1)

        predictions = np.array(model.predict(model_id=model_id, data=train))
        self.assertTrue(np.all(np.logical_xor(predictions == 0, predictions == 1)))

        model.close_model(model_id=model_id)
        predictions_2 = np.array(model.predict(model_id=model_id, data=train))
        self.assertTrue(np.all(predictions == predictions_2))

        model_id2 = model.create_model(model_type="KNN_classify")
        self.assertNotEqual(model_id, model_id2)

        model.delete_model(model_id=model_id)

        model = ExpertModelAPI()

        with self.assertRaisesRegex(ModelDoesNotExistException, r"The model with id: 0x[0-9]+ does not exist!!"):
            model.predict(model_id=model_id, data=train)

    def test_regress(self):
        model = ExpertModelAPI()
        model_id = model.create_model(model_type="KNN_regress")
        train = [ClimateModelOutput(TEST_NC) for _ in range(10)]
        labels = [0 for _ in range(5)] + [1 for _ in range(5)]
        performance = model.partial_fit(model_id=model_id, data=train, targets=labels)

        self.assertIsInstance(performance, ModelOutputs)
        self.assertIsInstance(performance.R2, float)
        self.assertTrue(0 <= performance.R2 <= 1)

        prediction = model.predict(model_id=model_id, data=train)[0]
        self.assertIsInstance(prediction, float)

    def test_semi_supervised(self):
        model = ExpertModelAPI()
        model_id = model.create_model(model_type="KNN_PCA")
        train = [ClimateModelOutput(TEST_NC) for _ in range(10)]

        for data in train:
            data.numpy_arrays += np.random.normal(size=data.numpy_arrays.shape)

        labels = [0 for _ in range(5)] + [1 for _ in range(5)]
        model.fit_unsupervised(model_id=model_id, data=train)

        performance = model.partial_fit(model_id=model_id, data=train, targets=labels)

        self.assertIsInstance(performance, ModelOutputs)
        self.assertIsInstance(performance.R2, float)
        self.assertTrue(0 <= performance.R2 <= 1)

        prediction = model.predict(model_id=model_id, data=train)[0]
        self.assertIsInstance(prediction, float)


if __name__ == '__main__':
    unittest.main()
