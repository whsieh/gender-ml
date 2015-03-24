from sklearn import svm
from scipy.io import loadmat, savemat
from time import time
from util import *
import numpy as np
import sys

"""
Runs the given function, wrapping execution of the function with timing outputs.
"""
def run_and_time(message, function, messageLimit=70):
    print message, " " * (messageLimit - len(message)),
    sys.stdout.flush()
    currentTime = time()
    result = function()
    print "    done. (%.2f seconds)" % (time() - currentTime)
    return result

"""
Computes the fraction of entries in the given arrays that match.
"""
def prediction_accuracy(predicted, expected):
    correctEvaluationCount = 0
    for prediction, expectation in zip(predicted, expected):
        if prediction == expectation:
            correctEvaluationCount += 1
    return float(correctEvaluationCount) / len(predicted)

"""
Trains a classifier with the given data, labels, and parameter C.
"""
def train_svm_with_data(data, labels, C=1.0):
    classifier = svm.LinearSVC(C=C)
    classifier.fit(data, labels)
    return classifier
