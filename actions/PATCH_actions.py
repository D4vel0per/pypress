from http.server import BaseHTTPRequestHandler
import json
from typing import Any
from response_managers import Basic_PATCH_Response
from urllib import parse

class Person:
    name: str
    age: int
    description: str

def patch_person (handler: BaseHTTPRequestHandler, data: bytes, url_variables: dict[str, Any]):
    body = json.loads(data)
    query = {
        "name": parse.unquote(url_variables["[name]"])
    }

    res = Basic_PATCH_Response("set", {
        "$set": body
    }, query, Person)
    res.send()
    return res