# pylint: skip-file

import unittest
import numpy as np

from ExpertRep import ClimateModelOutput
from ExpertRep import ExpertModelAPI
from ExpertRep.abstract.ClimateEvalAPI import ModelOutputs
from ExpertRep.tests.constants import TEST_NC
from ExpertRep.registry.model_registry import available_models


def permute_cmo(model: ClimateModelOutput):
    """ Used to stop the unique training files condition from filtering out the test cases """
    model.numpy_arrays += np.random.normal(size=model.numpy_arrays.shape)
    return model


class TestModels(unittest.TestCase):
    def test_all_models(self):
        for model_type in available_models():
            train = [permute_cmo(ClimateModelOutput(TEST_NC)) for _ in range(10)]
            labels = [0 for _ in range(5)] + [1 for _ in range(5)]
            model = ExpertModelAPI()
            model_id = model.create_model(model_type=model_type)
            self.assertIn(model_id, model.models_that_exist)
            self.assertIn(model_id, model.open_models)
            model.close_model(model_id=model_id)
            self.assertIn(model_id, model.models_that_exist)
            self.assertNotIn(model_id, model.open_models)
            model.fit_unsupervised(model_id=model_id, data=train)
            performance = model.partial_fit(model_id=model_id, data=train, targets=labels)
            self.assertIsInstance(performance, ModelOutputs)
            predictions = np.array(model.predict(model_id=model_id, data=train))
            model.close_model(model_id=model_id)
            predictions_2 = np.array(model.predict(model_id=model_id, data=train))
            self.assertTrue(np.all(predictions == predictions_2))
            model.delete_model(model_id=model_id)



if __name__ == '__main__':
    unittest.main()
