from util import *
import sys

DEFAULT_UNCERTAINTY_THRESHOLD = 0.1
MALE_LABEL = 0
FEMALE_LABEL = 1
UNCERTAIN_LABEL = 2

def ngrams_in_name(name):
    name = "^" + name + "$"
    grams = []
    for index, char in enumerate(name):
        for i in xrange(1, 4):
            if index < len(name) - i:
                grams.append(name[index:index + i + 1])
    return grams

class GenderClassifier(object):
    def __init__(self, filename="data/linsvc.json", uncertaintyThreshold=DEFAULT_UNCERTAINTY_THRESHOLD):
        params = load_json_as_object(filename)
        self.maleNames = set(params["maleNames"])
        self.femaleNames = set(params["femaleNames"])
        self.intercept = params["intercept"]
        self.coefficients = params["coefficients"]
        self.uncertaintyThreshold = uncertaintyThreshold

    def _signed_distance(self, name):
        evaluation = self.intercept
        ngrams = ngrams_in_name(name)
        l1Norm = float(len(ngrams))
        for ngram in ngrams:
            if ngram in self.coefficients:
                evaluation += self.coefficients[ngram] / l1Norm
        return evaluation

    def _label_from_signed_distance(self, distance):
        if abs(distance) < self.uncertaintyThreshold:
            return UNCERTAIN_LABEL
        return MALE_LABEL if distance <= 0 else FEMALE_LABEL

    def _label_from_data(self, name):
        if name in self.maleNames:
            return MALE_LABEL
        if name in self.femaleNames:
            return FEMALE_LABEL
        return UNCERTAIN_LABEL

    """
    Returns a tuple containing the signed distance, predicted label using
    the signed distance, and the predicted label using the data.
    """
    def debug(self, name, expected=None):
        distance = self._signed_distance(name)
        labelFromDistance = self._label_from_signed_distance(distance)
        labelFromData = self._label_from_data(name)
        print name.ljust(15),
        if expected is not None:
            print str(expected).ljust(10),
        print str(labelFromData).ljust(10),
        print str(labelFromDistance).ljust(10),
        print str(round(distance, 2))
        return labelFromData, labelFromDistance, distance

    """
    Given a first name, returns 0, 1, or 2, indicating the gender of the
    name. 0 indicates male, 1 indicates female, and 2 indicates that the
    classifier was unable to reach any conclusion.
    """
    def gender(self, name):
        name = name.lower()
        genderFromData = self._label_from_data(name)
        if genderFromData is not UNCERTAIN_LABEL:
            return genderFromData
        return self._label_from_signed_distance(self._signed_distance(name))

def run_gender_test():
    # Tests the classifier against some anomalies...
    cls = GenderClassifier()
    print "NAME".ljust(15), "EXP".ljust(10), "L(DATA)".ljust(10), "L(DIST)".ljust(10), "DIST"
    cls.debug("wenson", expected=0)
    cls.debug("wenny", expected=1)
    cls.debug("yehna", expected=1)
    cls.debug("akash", expected=0)
    cls.debug("rahul", expected=0)
    cls.debug("anchal", expected=1)
    cls.debug("subha", expected=1)
    cls.debug("abishek", expected=0)
    cls.debug("abheek", expected=0)
    cls.debug("varun", expected=0)
    cls.debug("abhinav", expected=0)
    cls.debug("gopi", expected=0)
    cls.debug("sahaana", expected=1)
    cls.debug("aurash", expected=0)
    cls.debug("karthik", expected=0)
    cls.debug("keol", expected=0)
    cls.debug("ketaki", expected=1)
    cls.debug("ji-hern", expected=0)
    cls.debug("esaac", expected=0)
    cls.debug("jairus", expected=0)
    cls.debug("siddhu", expected=0)
    cls.debug("siddharth", expected=0)

if __name__ == "__main__":
    cls = GenderClassifier()
