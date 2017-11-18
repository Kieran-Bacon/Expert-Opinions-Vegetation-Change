import numpy as np
import matplotlib.pyplot as plt

from sklearn import linear_model, metrics
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

root = "/Users/bentownsend/Desktop/cs/4thYear/group_proj/machine-learning-and-weather/backend/model_outputs/"
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

logistic = linear_model.LogisticRegression()
pca = PCA()

classifier = Pipeline(steps=[('pca', pca), ('logistic', logistic)])

pca.n_components = 30

pca.fit(np.concatenate((X_train, pca_train)))

logistic.fit(pca.transform(X_train), Y_train)

logistic_classifier = linear_model.LogisticRegression()
logistic_classifier.fit(X_train, Y_train)

knn = KNeighborsClassifier(n_neighbors=2)

knn.fit(pca.transform(X_train), Y_train)

knn_pca = Pipeline(steps=[('pca', pca), ('knn', knn)])

knn_classifier = KNeighborsClassifier(n_neighbors=2)

knn_classifier.fit(X_train, Y_train)

svm = SVC()

svm.fit(pca.transform(X_train), Y_train)

svm_pca = Pipeline(steps=[('pca', pca), ('svm', svm)])

svm_classifier_linear = SVC(kernel="linear")

svm_classifier_linear.fit(X_train, Y_train)


print()
print("Logistic regression using PCA features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        classifier.predict(X_test))))

print("Logistic regression using raw pixel features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        logistic_classifier.predict(X_test))))

print("KNN using PCA features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        knn_pca.predict(X_test))))

print("KNN using raw pixel features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        knn_classifier.predict(X_test))))

print("SVM using PCA features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        svm_pca.predict(X_test))))

print("Linear SVM using raw pixel features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        svm_classifier_linear.predict(X_test))))

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
