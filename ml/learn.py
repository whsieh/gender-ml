import sys
import argparse
import os
from util import *
from training_util import *
from math import log
from genderize import DEFAULT_UNCERTAINTY_THRESHOLD, DEFAULT_CLASSIFIER_FILENAME

NAME_BEGIN_CHAR = "^"
NAME_END_CHAR = "$"

def ngrams_from_name(name, uniqueOnly=True):
    name = NAME_BEGIN_CHAR + name + NAME_END_CHAR
    if uniqueOnly:
        grams = set([])
        for index, char in enumerate(name):
            for i in xrange(1, 4):
                if index < len(name) - i:
                    grams.add(name[index:index + i + 1])
        return list(grams)
    else:
        grams = []
        for index, char in enumerate(name):
            for i in xrange(1, 4):
                if index < len(name) - i:
                    grams.append(name[index:index + i + 1])
        return grams

def ngram_features_from_name_data(nameData, threshold=10):
    numFemales = sum(nameData.values())
    numMales = len(nameData) - numFemales
    fmRatio = numFemales / float(numMales)
    scores = {}
    for name, gender in nameData.items():
        for ngram in ngrams_from_name(name, uniqueOnly=True):
            if ngram not in scores:
                scores[ngram] = 0
            scores[ngram] += 1 if gender == 1 else -fmRatio
    scores = { g: np.sign(s) * log(abs(s), threshold) for g, s in scores.items() if abs(s) > threshold }
    ngrams = { ngram: index for index, ngram in enumerate(sorted(scores)) }
    return ngrams, scores

def test_and_training_data_from_file(filename="data/names.json", testDatasetSize=0):
    allData = load_json_as_object(filename)
    allNames = np.array(allData.keys())
    testIndices = np.random.choice(np.arange(len(allNames)), testDatasetSize, replace=False)
    testNames = set([name for name in allNames[testIndices]])
    testData, trainData = {}, {}
    for name, gender in allData.items():
        if name in testNames:
            testData[name] = gender
        else:
            trainData[name] = gender
    return trainData, testData

def featurize_name_data_and_labels(nameData, ngramIndices):
    names = nameData.keys()
    data = featurize_names(names, ngramIndices)
    labels = np.array([nameData[name] for name in names])
    return data, labels

def featurize_names(names, ngramIndices):
    data = []
    for name in names:
        featureVector = np.zeros(len(ngramIndices))
        for ngram in ngrams_from_name(name, uniqueOnly=False):
            if ngram in ngramIndices:
                featureVector[ngramIndices[ngram]] += 1
        l1Norm = featureVector.sum()
        data.append(featureVector / l1Norm if l1Norm != 0 else featureVector)
    return np.array(data)

def print_ngram_scores(ngramScores):
    ngramList = sorted(ngramScores.items(), lambda u,v: int(100*u[1] - 100*v[1]))
    for ngram, score in ngramList:
        print ngram.ljust(20), score

def test_accuracy(testDatasetSize=500):
    rawTrainData, rawTestData = test_and_training_data_from_file(testDatasetSize=testDatasetSize)
    ngramIndices, ngramScores = ngram_features_from_name_data(rawTrainData)
    print "Feature vector length: ", len(ngramIndices)
    data, labels = featurize_name_data_and_labels(rawTrainData, ngramIndices)
    svm = run_and_time("Training SVM...", lambda: train_svm_with_data(data, labels, C=50))
    testData, testLabels = featurize_name_data_and_labels(rawTestData, ngramIndices)
    predictions = run_and_time("Predicting test data...", lambda: svm.predict(testData))
    print prediction_accuracy(predictions, testLabels)

"""
This method is here and not util.py since it requires knowledge of a LinearSVC.
"""
def save_linear_classifier(filename, svm, ngramIndices, rawGenderMapping, compressData=True, uncertainty=DEFAULT_UNCERTAINTY_THRESHOLD):
    names = rawGenderMapping.keys()
    trainingData = featurize_names(names, ngramIndices)
    evaluations = svm.decision_function(trainingData)
    if compressData:
        uncertainNames = []
        for evaluation, name in zip(evaluations, names):
            distanceToHyperplane = evaluation * ((2 * rawGenderMapping[name]) - 1)
            if distanceToHyperplane <= uncertainty:
                uncertainNames.append(name)
    else:
        uncertainNames = names
    ngrams = [None] * len(ngramIndices)
    for ngram, index in ngramIndices.items():
        ngrams[index] = ngram
    save_object_as_json(filename, {
        "intercept": svm.intercept_[0],
        "coefficients": {ngrams[index]:round(c, 4) for index, c in enumerate(svm.coef_[0])},
        "male_names": [name for name in uncertainNames if rawGenderMapping[name] == 0],
        "female_names": [name for name in uncertainNames if rawGenderMapping[name] == 1],
        "uncertainty_threshold": uncertainty
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a gender classifier.")
    parser.add_argument("--dataset", "-d", default="data/names.json", help="The name of the dataset.")
    parser.add_argument("--ngram-threshold", "-ng", default="10", help="The ngram absolute value score threshold.")
    parser.add_argument("--regularization", "-C", default="50", help="Regularization term to use when training the SVM.")
    parser.add_argument("--output", "-o", default=DEFAULT_CLASSIFIER_FILENAME, help="The name of the output file.")
    parser.add_argument("--uncertainty", "-u", default=DEFAULT_UNCERTAINTY_THRESHOLD, help="The uncertainty threshold.")
    parser.add_argument("--compress", "-c", action="store_const", const=True, default=False, help="Whether or not to compress the output dataset.")
    parser.add_argument("--name-test", "-nt", action="store_const", const=True, default=False, help="Whether or not to run a testing routine after training.")
    args = parser.parse_args()

    args.ngram_threshold = to_int(args.ngram_threshold)
    args.regularization = to_float(args.regularization)
    args.uncertainty = to_float(args.uncertainty)

    rawData, _ = test_and_training_data_from_file(filename=args.dataset)
    ngramIndices, ngramScores = ngram_features_from_name_data(rawData, threshold=args.ngram_threshold)
    print "Feature vector length: ", len(ngramIndices)
    data, labels = featurize_name_data_and_labels(rawData, ngramIndices)
    svm = run_and_time("Training SVM...", lambda: train_svm_with_data(data, labels, C=args.regularization))
    filename = args.output
    run_and_time("Serializing SVC to %s..." % filename, lambda: save_linear_classifier(filename, svm, ngramIndices, rawData, compressData=args.compress, uncertainty=args.uncertainty))
    print "Saved %s (%d K)" % (filename, os.stat(filename).st_size >> 10)
    if args.name_test:
        from genderize import GenderClassifier
        cls = GenderClassifier(filename=args.output)
        cls.run_test()
