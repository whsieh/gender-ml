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

"""
This method is training.py and not util.py since it requires knowledge
of a LinearSVC.
"""
def save_linear_classifier(filename, svm, ngramIndices, rawData):
    ngrams = [None] * len(ngramIndices)
    for ngram, index in ngramIndices.items():
        ngrams[index] = ngram
    save_object_as_json(filename, {
        "intercept": svm.intercept_[0],
        "coefficients": {ngrams[index]:round(c, 4) for index, c in enumerate(svm.coef_[0])},
        "maleNames": [name for name in rawData if rawData[name] == 0],
        "femaleNames": [name for name in rawData if rawData[name] == 1]
    })
