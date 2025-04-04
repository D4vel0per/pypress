from http.server import BaseHTTPRequestHandler
import json

from response_managers import HTTP_CODES, Basic_POST_Response, Set_DB

def post_person (handler: BaseHTTPRequestHandler, content: bytes|str):
    content_type = handler.headers["Content-Type"] if "Content-Type" in handler.headers else "text/plain"
    print("Inside post_person")
    print(f"Content received ({content_type}): ", json.loads(content.decode()))
    return Basic_POST_Response(HTTP_CODES.CREATED, handler, None, Set_DB(content))