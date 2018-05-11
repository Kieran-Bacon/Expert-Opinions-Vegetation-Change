import os
from ExpertRep.concrete.MainBackend import Backend as ExpertModelAPI
from ExpertRep.concrete.MainBackend import _veg_ml_dir
from ExpertRep.concrete.netcdf_file import NetCDFFile as ClimateModelOutput
from ExpertRep.registry.model_registry import available_models as available_models
from ExpertRep.abstract.ClimateEvalAPI import ModelNotTrainedException