"""
Tools required to perform leave one out cross validation to achieve accurate approximations of evaluation metrics.
"""
import numpy as np
import logging
_LOG = logging.getLogger(__name__)

def mean_model_outputs(list_of_model_outs: list):
    """
    Calculates the means of a list of model outputs and returns it in the same format it was received.

    Args:
        list_of_model_outs:

    Returns:
        An instance of the same type as one element of list_of_model_outs

    """
    try:
        model_outputs_class = list_of_model_outs[0].__class__
    except IndexError:
        raise ArithmeticError("Mean of empty array is undefined")

    return model_outputs_class(*[np.mean([model[i] for model in list_of_model_outs])
                                 for i in range(len(model_outputs_class._fields))])


def leave_one_out(data: list, target: list, fit_fn: callable, score_fn: callable, *args, **kwargs) -> "ModelOutputs":
    """
    Calculates leave one out cross-validation and retrains the model on the completed dataset.

    Args:
        data: A list of data.
        target: A list of target values
        fit_fn: A fit fn with signature func(data, targets, *args, **kwargs)
        score_fn: A scoring fn with signature func(data, targets) -> ModelOutputs
        *args: Any args for the fit function
        **kwargs: any kwargs for the fit function

    Returns:
        An instance of ModelOutputs

    """
    model_outputs = []
    for i, _ in enumerate(target):
        data_fold = data[:i] + data[i + 1:]
        target_fold = target[:i] + target[i + 1:]
        fit_fn(data=data_fold, targets=target_fold, *args, **kwargs)
        model_outputs.append(score_fn(test_data=[data[i]], test_targets=[target[i]]))
        _LOG.info("Cross Val fold num {} score: {}".format(i, model_outputs[-1]))
    fit_fn(data=data, targets=target, test_data=[], test_target=[], *args, **kwargs)
    return mean_model_outputs(model_outputs)
