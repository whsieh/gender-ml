import json

"""
Attempts to safely convert s to a float value. If s cannot be
converted to a float, returns None.
"""
def to_float(s):
    try:
        return float(s)
    except ValueError:
        return None

"""
Attempts to safely convert s to an int value. If s cannot be
converted to an int, returns None.
"""
def to_int(s):
    try:
        return int(s)
    except ValueError:
        return None

def filename_with_extension(filename, extension):
    extension = "." + extension if extension[0] != "." else extension
    return filename + extension if filename[-len(extension):] != extension else filename

def load_json_as_object(filename):
    filename = filename_with_extension(filename, "json")
    jsonFile = open(filename, "r")
    dataAsString = jsonFile.read()
    jsonFile.close()
    return json.loads(dataAsString)

def save_object_as_json(filename, data):
    filename = filename_with_extension(filename, "json")
    dataAsString = json.dumps(data, ensure_ascii=True)
    out = open(filename, "w")
    out.write(dataAsString)
    out.close()
