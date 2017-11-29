import numpy as np
import matplotlib.pyplot as plt

root = "/Users/bentownsend/Desktop/cs/4thYear/group_proj/machine-learning-and-weather/backend/model_outputs/"
labels = "ben_labels_.npy"
features = "numpy_not_flat.npy"

cmos = np.load(root + "/" + features)

for i in reversed(range(20)):
    plt.imshow(np.sum(cmos[0][:i], axis=0)+np.sum(cmos[0][i+1:], axis=0))
    plt.show()