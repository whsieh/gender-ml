import os
from flask import Flask, jsonify, request
from ml.genderize import GenderClassifier

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = dict(self.payload or ())
        result["message"] = self.message
        return result

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
def classify_genders():
    if len(request.args) == 0:
        raise InvalidUsage("Unable to parse names", status_code=400)

    cls = GenderClassifier()
    genders = [cls.gender(name) for name in request.args]
    return jsonify({ name: gender for name, gender in zip(request.args, genders) })

if __name__ == "__main__":
    app.run()
