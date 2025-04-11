from http.server import BaseHTTPRequestHandler
import json
from typing import Any

from pydantic import BaseModel

from response_managers import HTTP_CODES, Basic_POST_Response, Set_DB

def post_person (handler: BaseHTTPRequestHandler, data: Set_DB, url_variables: dict[str, Any]):
    content_type = handler.headers["Content-Type"] if "Content-Type" in handler.headers else "text/plain"
    print("Inside post_person")
    print(f"Content received ({content_type}): ", data.data)
    return Basic_POST_Response(HTTP_CODES.CREATED, handler, None, data, url_variables)