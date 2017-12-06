import os
from VegML.concrete.MainBackend import Backend as VegML
from VegML.concrete.MainBackend import _VEG_ML_DIR
from VegML.concrete.netcdf_file import NetCDFFile as ClimModel
os.makedirs(_VEG_ML_DIR, exist_ok=True)
