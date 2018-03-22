import os
from .concrete.MainBackend import Backend as ExpertModelAPI
from .concrete.MainBackend import _VEG_ML_DIR
from .concrete.netcdf_file import NetCDFFile as ClimateModelOutput
from .registry.model_registry import available_models as available_models
os.makedirs(_VEG_ML_DIR, exist_ok=True)
