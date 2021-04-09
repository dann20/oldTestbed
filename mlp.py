import numpy as np
import pandas as pd
import time
from sklearn.decomposition import PCA
# from numpy import array
# from numpy import mean
# from numpy import cov
# from numpy.linalg import eig
from scipy import sparse

# def householder_reflection(a, e):
#     '''
#     Given a vector a and a unit vector e,
#     (where a is non-zero and not collinear with e)
#     returns an orthogonal matrix which maps a
#     into the line of e.
#     '''

#     assert a.ndim == 1
#     assert np.allclose(1, np.sum(e**2))

#     u = a - np.sign(a[0]) * np.linalg.norm(a) * e
#     v = u / np.linalg.norm(u)
#     H = np.eye(len(a)) - 2 * np.outer(v, v)

#     return H


# def qr_decomposition(A):
#     '''
#     Given an n x m invertable matrix A, returns the pair:
#         Q an orthogonal n x m matrix
#         R an upper triangular m x m matrix
#     such that QR = A.
#     '''

#     n, m = A.shape
#     assert n >= m

#     Q = np.eye(n)
#     R = A.copy()

#     for i in range(m - int(n==m)):
#         r = R[i:, i]

#         if np.allclose(r[1:], 0):
#             continue

#         # e is the i-th basis vector of the minor matrix.
#         e = np.zeros(n-i)
#         e[0] = 1

#         H = np.eye(n)
#         H[i:, i:] = householder_reflection(r, e)

#         Q = Q @ H.T
#         R = H @ R

#     return Q, R
# def eigen_decomposition(A, max_iter=100):
#     A_k = A
#     Q_k = np.eye( A.shape[1] )

#     for k in range(max_iter):
#         Q, R = qr_decomposition(A_k)
#         Q_k = Q_k @ Q
#         A_k = R @ Q

#     eigenvalues = np.diag(A_k)
#     eigenvectors = Q_k
#     return eigenvalues, eigenvectors
# class PCA:
#     def __init__(self, n_components=None, whiten=False):
#         self.n_components = n_components
#         self.whiten = bool(whiten)

#     def fit(self, X):
#         n, m = X.shape

#         # subtract off the mean to center the data.
#         self.mu = X.mean(axis=0)
#         X = X - self.mu

#         # whiten if necessary
#         if self.whiten:
#             self.std = X.std(axis=0)
#             X = X / self.std

#         # Eigen Decomposition of the covariance matrix
#         C = X.T @ X / (n-1)
#         self.eigenvalues, self.eigenvectors = eigen_decomposition(C)

#         # truncate the number of components if doing dimensionality reduction
#         if self.n_components is not None:
#             self.eigenvalues = self.eigenvalues[0:self.n_components]
#             self.eigenvectors = self.eigenvectors[:, 0:self.n_components]

#         # the QR algorithm tends to puts eigenvalues in descending order
#         # but is not guarenteed to. To make sure, we use argsort.
#         descending_order = np.flip(np.argsort(self.eigenvalues))
#         self.eigenvalues = self.eigenvalues[descending_order]
#         self.eigenvectors = self.eigenvectors[:, descending_order]

#         return self

#     def transform(self, X):
#         X = X - self.mu

#         if self.whiten:
#             X = X / self.std

#         return X @ self.eigenvectors

#     @property
#     def proportion_variance_explained(self):
#         return self.eigenvalues / np.sum(self.eigenvalues)


def relu(X):
   return np.maximum(0,X)

def softmax(V):
    e_V = np.exp(V - np.max(V, axis = 0, keepdims = True))
    Z = e_V / e_V.sum(axis = 0)
    return Z

def convert_labels(y, C):
    Y = sparse.coo_matrix((np.ones_like(y), (y, np.arange(len(y)))), shape = (C, len(y))).toarray()
    return Y
def cost(Y, Yhat):
    return -np.sum(Y*np.log(Yhat))/Y.shape[0]
for h in range(44, 47):
    d0 = 37
    reduced_d0 = 6
    d1 = h # size of hidden layer
    d2 = C = 11
    pca = PCA(n_components=reduced_d0, svd_solver='full')
# initialize parameters randomly
    trainset = pd.read_excel('traindata.xlsx', header=None)
    X = trainset.iloc[:, :-1].astype(np.float).to_numpy().T
    d0 = X.shape[0]
    y = trainset.iloc[:, -1].astype(np.int).to_numpy().T
    Y = convert_labels(y, C)
    pca.fit(X.T)
    XPCA = pca.transform(X.T).T
    N = XPCA.shape[1]
    W1 = 0.01*np.random.randn(reduced_d0, d1)
    print("SHAPE = ", W1.T.shape)
    print(XPCA.shape)
    print(X.shape)
# print(W1.shape)
    b1 = np.zeros((d1, 1))
    W2 = 0.01*np.random.randn(d1, d2)
# print(W2.shape)
# W1 = np.loadtxt('mlp_W1.csv', delimiter=',')
# W2 = np.loadtxt('mlp_W2.csv', delimiter=',')
    b2 = np.zeros((d2, 1))
    eta = 1 # learning rate
    time1 = time.time()
    for i in range(5000):
        ## Feedforward
        Z1 = np.dot(W1.T, XPCA) + b1
        A1 = np.maximum(Z1, 0)
        Z2 = np.dot(W2.T, A1) + b2
        Yhat = softmax(Z2)

        # print loss after each 1000 iterations
            # compute the loss: average cross-entropy loss
        loss = cost(Y, Yhat)
        print("iter %d, loss: %f" %(i, loss))

        # backpropagation
        E2 = (Yhat - Y)/N
        dW2 = np.dot(A1, E2.T)
        db2 = np.sum(E2, axis = 1, keepdims = True)
        E1 = np.dot(W2, E2)
        E1[Z1 <= 0] = 0 # gradient of ReLU
        dW1 = np.dot(XPCA, E1.T)
        db1 = np.sum(E1, axis = 1, keepdims = True)

        # Gradient Descent update
        W1 += -eta*dW1
        b1 += -eta*db1
        W2 += -eta*dW2
        b2 += -eta*db2
# W1 = np.loadtxt('mlp_W1.csv', delimiter=',')
# b1 = np.loadtxt('mlp_b1.csv', delimiter=',')
# W2 = np.loadtxt('mlp_W2.csv', delimiter=',')
# b2 = np.loadtxt('mlp_b2.csv', delimiter=',')
    testset = pd.read_excel('testdata.xlsx', header=None)
    X_test = testset.iloc[:, :-1].astype(np.float).to_numpy().T
    X_testPCA = pca.transform(X_test.T).T
    y_test = testset.iloc[:, -1].astype(np.int).to_numpy().T
    b1 = b1.reshape((b1.shape[0], 1))
    b2 = b2.reshape((b2.shape[0], 1))
    Z1 = np.dot(W1.T, X_testPCA) + b1
    A1 = np.maximum(Z1, 0)
    Z2 = np.dot(W2.T, A1) + b2
    predicted_class = np.argmax(Z2, axis = 0)
    print(np.mean(predicted_class == y_test))
    train_time = time.time() - time1
    print(train_time)
    np.savetxt('mlp_X{}.csv'.format(h), X, delimiter=',')
    np.savetxt('mlp_W1{}.csv'.format(h), W1, delimiter=',')
    np.savetxt('mlp_W2{}.csv'.format(h), W2, delimiter=',')
    np.savetxt('mlp_b1{}.csv'.format(h), b1, delimiter=',')
    np.savetxt('mlp_b2{}.csv'.format(h), b2, delimiter=',')
    with open('server_train_test_mlp.txt', 'a') as f:
        f.write(str(h) + " Train and test time : " + str(train_time) + '\n')
        f.write(str(h) + " Accuracy: " + str(np.mean(predicted_class == y_test)) + '\n')
        f.close()
