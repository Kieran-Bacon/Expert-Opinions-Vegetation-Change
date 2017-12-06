import numpy as np
import matplotlib.pyplot as plt

from sklearn import linear_model, metrics
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

names = ["logistic_regression", "Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes", "QDA"]

classifiers = [
    linear_model.LogisticRegression(),
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()
]

root = "/Users/bentownsend/Desktop/cs/4thYear/group_proj/machine-learning-and-weather/concrete/model_outputs/"
labels = "ben_labels_.npy"
features = "numpy_flat.npy"

feats = np.load(root + "/" + features)
feats = feats[:, ::-1, ::-1]
nan_mask = np.isnan(feats)
feats[nan_mask] = 0
labs = np.load(root + "/" + labels)

features, pca_train, labels, _ = train_test_split(np.reshape(feats, [feats.shape[0], -1]), labs, test_size=0.5,
                                                  random_state=0)

X_train, X_test, Y_train, Y_test = train_test_split(features, labels, test_size=0.5,
                                                    random_state=0)
pca = PCA()

pca.n_components = len(X_train[0])

pca.fit(np.concatenate((X_train, pca_train)))

for name, clf in zip(names, classifiers):
    clf.fit(X_train, Y_train)

    print("%s using raw pixel features:\n%s\n" % (name,
                                                  metrics.classification_report(
                                                      Y_test,
                                                      clf.predict(X_test))))

    clf_pca = Pipeline(steps=[('pca', pca), (name, clf)])

    clf.fit(pca.transform(X_train), Y_train)

    print("%s using pca pixel features:\n%s\n" % (name,
                                                  metrics.classification_report(
                                                      Y_test,
                                                      clf_pca.predict(X_test))))

plt.figure(figsize=(4.2, 4))
for i, comp in enumerate(pca.components_):
    plt.subplot(6, 5, i + 1)
    plt.imshow(comp.reshape(feats.shape[1:]), cmap=plt.cm.gray_r,
               interpolation='nearest')
    plt.xticks(())
    plt.yticks(())
plt.suptitle('30 components extracted by PCA', fontsize=16)
plt.subplots_adjust(0.08, 0.02, 0.92, 0.85, 0.08, 0.23)

plt.show()

plt.plot(np.cumsum(pca.explained_variance_)/sum(pca.explained_variance_))
plt.title("Cumulative explained variance")
plt.xlabel("N-components")
plt.ylabel("Fraction of explained variance")
plt.show()
