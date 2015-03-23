import flask
from ml.genderize import GenderClassifier
from hashlib import sha256

app = flask.Flask(__name__)

# Configurations
SECRET_DIGEST = "65eb608c22cff0e6c4a4bef0aa04eae4e3cc6e9c42adf53965a26a57e584c7be"
AUTH_FAILURE_MESSAGE = "Authentication failed. Please fork github.com/whsieh/gender-ml if you want to use our API"
INVALID_USAGE_MESSAGE = "Usage: GET /classify?auth_token=XXXXXX&names=A,B,C,D"

@app.errorhandler(400)
def invalid_usage():
    resp = flask.jsonify({ "status": 400, "message": INVALID_USAGE_MESSAGE })
    resp.status_code = 400
    return resp

@app.errorhandler(401)
def authentication_failure():
    resp = flask.jsonify({ "status": 401, "message": AUTH_FAILURE_MESSAGE })
    resp.status_code = 401
    return resp

@app.route("/classify", methods=["GET"])
def classify_genders():
    params = flask.request.args
    if len(params) == 0 or "auth_token" not in params or "names" not in params:
        return invalid_usage()

    if sha256(params["auth_token"].upper()).hexdigest() != SECRET_DIGEST:
        return authentication_failure()

    names = [name.strip() for name in params["names"].split(",")]
    if len(names) == 0:
        return flask.jsonify({})

    cls = GenderClassifier()
    genders = [cls.gender(name) for name in names]
    return flask.jsonify({ name: gender for name, gender in zip(names, genders) })

if __name__ == "__main__":
    app.run()
