from http.server import BaseHTTPRequestHandler
import json
from typing import Any

from response_managers import Basic_POST_Response

class Person:
    name: str
    age: int
    description: str

def post_person (handler: BaseHTTPRequestHandler, data: bytes, url_variables: dict[str, Any]):
    content_type = handler.headers["Content-Type"] if "Content-Type" in handler.headers else "text/plain"
    print("Inside post_person")
    print(f"Content received ({content_type}): ", data)
    post_data: dict|list = json.loads(data)

    if type(post_data) is list:
        for post_entry in post_data:
            post_entry["age"] = int(post_entry["age"])
    else:
        post_data["age"] = int(post_data["age"])

    print(post_data)
    return Basic_POST_Response("set", post_data, Person)