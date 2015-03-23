from util import *
import sys

UNCERTAINTY_THRESHOLD = 0.1

def ngrams_in_name(name):
    name = "^" + name + "$"
    grams = []
    for index, char in enumerate(name):
        for i in xrange(1, 4):
            if index < len(name) - i:
                grams.append(name[index:index + i + 1])
    return grams

class GenderClassifier(object):
    def __init__(self, filename="data/linsvc.json"):
        params = load_json_as_object(filename)
        self.maleNames = set(params["maleNames"])
        self.femaleNames = set(params["femaleNames"])
        self.intercept = params["intercept"]
        self.coefficients = params["coefficients"]

    def _signedDistance(self, name):
        evaluation = self.intercept
        ngrams = ngrams_in_name(name)
        l1Norm = float(len(ngrams))
        for ngram in ngrams:
            if ngram in self.coefficients:
                evaluation += self.coefficients[ngram] / l1Norm
        return evaluation

    """
    Given a first name, returns 0, 1, or 2, indicating the gender of the
    name. 0 indicates male, 1 indicates female, and 2 indicates that the
    classifier was unable to reach any conclusion.
    """
    def gender(self, name):
        name = name.lower()
        # First, attempt direct dataset lookup.
        if name in self.maleNames:
            return 0
        if name in self.femaleNames:
            return 1
        # Use the SVC classifier if all else fails.
        distance = self._signedDistance(name)
        if abs(distance) < UNCERTAINTY_THRESHOLD:
            return 2
        return 0 if distance <= 0 else 1

def run_gender_test():
    cls = GenderClassifier()
    # Testing the classifier against anomalies...
    def testEvaluation(name, gender):
        cls.gender(name)
        print "%sexpected %d, got %d (dist: %f)" % (name.ljust(15), gender, cls.gender(name), cls._signedDistance(name))
    testEvaluation("wenson", 0)
    testEvaluation("wenny", 1)
    testEvaluation("yehna", 1)
    testEvaluation("akash", 0)
    testEvaluation("rahul", 0)
    testEvaluation("anchal", 1)
    testEvaluation("subha", 1)
    testEvaluation("abishek", 0)
    testEvaluation("abheek", 0)
    testEvaluation("varun", 0)
    testEvaluation("abhinav", 0)
    testEvaluation("gopi", 0)
    testEvaluation("sahaana", 1)
    testEvaluation("aurash", 0)
    testEvaluation("karthik", 0)
    testEvaluation("keol", 0)
    testEvaluation("ketaki", 1)
    testEvaluation("ji-hern", 0)
    testEvaluation("esaac", 0)
    testEvaluation("jairus", 0)
    testEvaluation("siddhu", 0)
    testEvaluation("siddharth", 0)
