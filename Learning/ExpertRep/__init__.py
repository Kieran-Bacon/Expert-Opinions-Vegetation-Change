import os
from ExpertRep.concrete.MainBackend import Backend as ExpertModelAPI
from ExpertRep.concrete.MainBackend import _VEG_ML_DIR
from ExpertRep.concrete.netcdf_file import NetCDFFile as ClimateModelOutput
from ExpertRep.registry.model_registry import available_models as available_models
os.makedirs(_VEG_ML_DIR, exist_ok=True)
