from util import *
import sys

DEFAULT_UNCERTAINTY_THRESHOLD = 0.1
DEFAULT_CLASSIFIER_FILENAME = "data/linsvc.json"
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
    def __init__(self, filename=DEFAULT_CLASSIFIER_FILENAME):
        params = load_json_as_object(filename)
        self.maleNames = set(params["male_names"])
        self.femaleNames = set(params["female_names"])
        self.intercept = params["intercept"]
        self.coefficients = params["coefficients"]
        self.uncertaintyThreshold = params["uncertainty_threshold"]

    def _signed_distance(self, name):
        dotProduct, norm = 0, 0
        for ngram in ngrams_in_name(name):
            if ngram in self.coefficients:
                dotProduct += self.coefficients[ngram]
                norm += 1
        return (dotProduct / norm) + self.intercept

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
    def debug(self, name, expected=None, loud=False):
        name = name.lower()
        distance = self._signed_distance(name)
        labelFromDistance = self._label_from_signed_distance(distance)
        labelFromData = self._label_from_data(name)
        if loud:
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

    def run_test(self):
        print "NAME".ljust(15), "EXP".ljust(10), "L(DATA)".ljust(10), "L(DIST)".ljust(10), "DIST"
        for name in ["wenson", "akash", "abishek", "abheek", "varun", "abhinav", "gopi", "aurash",
            "karthik", "keol", "ji-hern", "esaac", "jairus", "siddhu", "siddharth", "roshan", "seshadri",
            "japheth", "rayed", "tycho", "haruto", "yuto", "joon"]:
            self.debug(name, expected=MALE_LABEL)
        for name in ["wenny", "yehna", "anchal", "subha", "sahaana", "ketaki", "moeka", "cyntthia", "linzi",
            "sneha", "neha", "hina", "yuna"]:
            self.debug(name, expected=FEMALE_LABEL)

if __name__ == "__main__":
    cls = GenderClassifier()
