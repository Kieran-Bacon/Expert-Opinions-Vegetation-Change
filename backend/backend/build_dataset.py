from backend.netcdf_file import NetCDFFile
import os
import numpy as np

files = os.listdir("/root/code/backend/model_outputs/")
net_cdf_files = []

for file in files:

    if not file.endswith(".nc"):
        continue
    file = NetCDFFile(os.path.join("/root/code/backend/model_outputs/", file))

    veg_layer = np.sum(file.get_numpy_arrays()[:10], axis=0)

    net_cdf_files.append(veg_layer)

net_cdf_files = np.array(net_cdf_files)

np.save("/root/code/backend/model_outputs/numpy_flat", net_cdf_files)
