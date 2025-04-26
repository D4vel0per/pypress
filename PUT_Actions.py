from http.server import BaseHTTPRequestHandler
import json
from typing import Any
from response_managers import Basic_PUT_Response

class Person:
    name: str
    age: int
    description: str

def put_person (handler: BaseHTTPRequestHandler, data: bytes, url_variables: dict[str, Any]):
    body = json.loads(data)
    
    query = {
        "name": body["name"]
    }

    res = Basic_PUT_Response("set", body, query, Person)
    res.send()
    return res