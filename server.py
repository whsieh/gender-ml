import re
import flask
import json
from ml import genderize
from hashlib import sha256

app = flask.Flask(__name__)
classifier = genderize.GenderClassifier()

# Configurations
INVALID_USAGE_MESSAGE = "Usage: GET /classify?names=A,B,C,D"

def extract_names_from_params(params):
    if len(params) == 0 or "names" not in params:
        return None
    return [name.strip() for name in params["names"].split(",")]

def extract_name_from_params(params):
    if len(params) == 0 or "name" not in params:
        return None
    return params["name"]

@app.errorhandler(400)
def invalid_usage():
    resp = flask.jsonify({ "status": 400, "message": INVALID_USAGE_MESSAGE })
    resp.status_code = 400
    return resp

@app.route("/debug", methods=["GET"])
def debug_gender():
    name = extract_name_from_params(flask.request.args)
    if name is None:
        return invalid_usage()

    jsonpFunction = flask.request.args["callback"] if "callback" in flask.request.args else None
    labelFromData, labelFromDistance, distance = classifier.debug(name)
    result = {
        "name": name,
        "label_from_data": labelFromData,
        "label_from_dist": labelFromDistance,
        "hyperplane_dist": distance
    }
    return flask.jsonify(result) if jsonpFunction is None else jsonpFunction + "(" + json.dumps(result) + ")"

@app.route("/classify", methods=["GET"])
def classify_genders():
    names = extract_names_from_params(flask.request.args)
    if names is None:
        return invalid_usage()
    return flask.jsonify({ name: classifier.gender(name) for name in names })

@app.route("/", methods=["GET"])
def serve_index():
    return flask.redirect("http://whsieh.github.io/gender-ml")

if __name__ == "__main__":
    app.run()
