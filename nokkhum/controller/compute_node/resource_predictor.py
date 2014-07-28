'''
Created on Apr 25, 2013

@author: boatkrap
'''

'''
Created on Mar 25, 2013

@author: boatkrap
'''

from numpy.linalg import inv, det
from numpy import dot, sum, tile, array, diag, eye, zeros, log, pi, exp
# import pylab

from nokkhum import models


class KalmanPredictor:

    def __init__(self):
        # time step of mobile movement
        self.dt = 0.1
        self.v_x = []
        self.X_x = []

    def kf_predict(self, X, P, A, Q, B, U):
        X = dot(A, X) + dot(B, U)
        P = dot(A, dot(P, A.T)) + Q
        return(X, P)

    def kf_update(self, X, P, Y, H, R):
        IM = dot(H, X)
        IS = R + dot(H, dot(P, H.T))
        K = dot(P, dot(H.T, inv(IS)))
        X = X + dot(K, (Y - IM))
        P = P - dot(K, dot(IS, K.T))
        LH = self.gauss_pdf(Y, IM, IS)
        return (X, P, K, IM, IS, LH)

    def gauss_pdf(self, X, M, S):
        if M.shape[1] == 1:
            DX = X - tile(M, X.shape[1])
            E = 0.5 * sum(DX * (dot(inv(S), DX)), axis=0)
            E = E + 0.5 * M.shape[0] * log(2 * pi) + 0.5 * log(det(S))
            P = exp(-E)
        elif X.shape()[1] == 1:
            DX = tile(X, M.shape[1]) - M
            E = 0.5 * sum(DX * (dot(inv(S), DX)), axis=0)
            E = E + 0.5 * M.shape[0] * log(2 * pi) + 0.5 * log(det(S))
            P = exp(-E)
        else:
            DX = X - M
            E = 0.5 * dot(DX.T, dot(inv(S), DX))
            E = E + 0.5 * M.shape[0] * log(2 * pi) + 0.5 * log(det(S))
            P = exp(-E)
        return (P[0], E[0])

    def predict(self, records):
        X = None
        Y = None

        self.v_x = []
#         v_y = []
        self.X_x = []
#         X_y = []

        for record in records:

            if X is None:
                # Initialization of state matrices
                X = array([[record], [0.0], [0.0], [0.0]])
                P = diag((0.01, 0.01, 0.01, 0.01))
                A = array(
                    [[1, 0, self.dt, 0], [0, 1, 0, self.dt], [0, 0, 1, 0], [0, 0, 0, 1]])

                Q = eye(X.shape[0])
                B = eye(X.shape[0])
                U = zeros((X.shape[0], 1))

                # Measurement matrices
                # Y = array([[X[0,0] + abs(randn(1)[0])], [X[1,0] +\
                # abs(randn(1)[0])]])
                Y = array([[record]])

                H = array([[1, 0, 0, 0]])
                R = eye(Y.shape[0])
                self.X_x.append(X[0, 0])


#             print("usage:", record)
            self.v_x.append(record)

            x = record
            Y = array([[x]])
            (X, P) = self.kf_predict(X, P, A, Q, B, U)
            (X, P, K, IM, IS, LH) = self.kf_update(X, P, Y, H, R)

            self.X_x.append(X[0, 0])
#             print("predict:", X[0, 0])

#         import pylab
#         import datetime
#         pylab.figure()
#         pylab.plot(self.v_x, 'b:x', label='val 0, true', linewidth=1)
#         pylab.plot(self.X_x, 'r-o', label='val 0, noisy', linewidth=2)
#         pylab.savefig("/tmp/%s.svg"%datetime.datetime.now())
#         pylab.show()

        if X is None:
            return None

        return X[0, 0]
