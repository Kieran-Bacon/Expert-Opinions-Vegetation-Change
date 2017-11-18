import numpy as np
import matplotlib.pyplot as plt

file = "/Users/bentownsend/Desktop/cs/4thYear/group_proj/machine-learning-and-weather/backend/model_outputs/numpy_flat.npy"

cmos = np.load(file)
cmos = cmos[:, ::-1, ::-1]
labels = []
plt.ion()
try:
    for i in range(10000):
        nan_mask = np.isnan(cmos[i])
        cmos[i][nan_mask] = -1
        plt.imshow(cmos[i])

        plt.pause(0.05)
        labels.append(input(">>"))
except KeyboardInterrupt:
    pass
finally:
    save = None
    while save not in ["y", "n"]:
        save = input("Would you like to save these labels, y/n: ")
    if save == "y":
        labels = [label == "1" for label in labels]
        np.save(
            "/Users/bentownsend/Desktop/cs/4thYear/group_proj/machine-learning-and-weather/backend/model_outputs/hugo_labels",
            np.array(labels))
