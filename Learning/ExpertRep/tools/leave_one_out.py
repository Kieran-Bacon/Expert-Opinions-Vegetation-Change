import numpy as np
from ExpertRep.abstract.ModelAPI import ModelOutputs
import warnings


def mean_model_outputs(output: list):
    try:
        model_outputs_class = output[0].__class__
    except IndexError:
        warnings.warn("Mean of empty array is undefined")

    return model_outputs_class(*[np.mean([model[i] for model in output]) for i in range(len(model_outputs_class._fields))])


def leave_one_out(data: list, target: list, fit_fn: callable, score_fn: callable, *args, **kwargs):
    model_outputs = []
    for i, _ in enumerate(target):
        data_fold = data[:i] + data[i + 1:]
        target_fold = target[:i] + target[i + 1:]
        fit_fn(data=data_fold, targets=target_fold, *args, **kwargs)
        model_outputs.append(score_fn(test_data=[data[i]], test_targets=[target[i]]))
    fit_fn(data=data, targets=target, test_data=[], test_target=[], *args, **kwargs)
    return mean_model_outputs(model_outputs)
