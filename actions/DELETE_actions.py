from http.server import BaseHTTPRequestHandler
import json
from typing import Any
from response_managers import Basic_DELETE_Response
from urllib import parse

class Person:
    name: str
    age: int
    description: str

def delete_person (handler: BaseHTTPRequestHandler, data: bytes, url_variables: dict[str, Any]):
    query = {
        "name": parse.unquote(url_variables["[name]"])
    }

    res = Basic_DELETE_Response("set", query)
    res.send(b"Registro Eliminado")
    return res