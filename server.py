import re
import flask
from ml import genderize
from hashlib import sha256

app = flask.Flask(__name__)
classifier = genderize.GenderClassifier()

# Configurations
INVALID_USAGE_MESSAGE = "Usage: GET /classify?names=A,B,C,D"

@app.errorhandler(400)
def invalid_usage():
    resp = flask.jsonify({ "status": 400, "message": INVALID_USAGE_MESSAGE })
    resp.status_code = 400
    return resp

@app.route("/classify", methods=["GET"])
def classify_genders():
    params = flask.request.args
    if len(params) == 0 or "names" not in params:
        return invalid_usage()

    names = [name.strip() for name in params["names"].split(",")]
    if len(names) == 0:
        return flask.jsonify({})

    return flask.jsonify({name: classifier.gender(name) for name in names})

if __name__ == "__main__":
    app.run()
