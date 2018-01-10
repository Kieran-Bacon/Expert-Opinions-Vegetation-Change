import numpy as np
from ExpertRep.abstract.ModelAPI import ModelOutputs


def mean_model_outputs(output: list):
    return ModelOutputs(*[np.mean([model[i] for model in output]) for i in range(len(ModelOutputs._fields))])


def leave_one_out(data: list, target: list, fit_fn: callable, score_fn: callable):
    model_outputs = []
    for i, _ in enumerate(target):
        data_fold = data[:i] + data[i + 1:]
        target_fold = target[:i] + target[i + 1:]
        model_outputs.append(fit_fn(data=data_fold, target=target_fold, test_data=[data[i]], test_target=[target[i]]))
    fit_fn(data=data, target=target, test_data=[], test_target=[])
    return mean_model_outputs(model_outputs)
