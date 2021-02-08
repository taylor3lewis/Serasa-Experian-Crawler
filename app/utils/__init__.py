import json
from flask import Response


def response_json(content):
    if isinstance(content, dict) or isinstance(content, list):
        resp = Response(json.dumps(content))
    else:
        resp = Response(content)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp
