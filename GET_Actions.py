from http.server import BaseHTTPRequestHandler
from utils import Basic_GET_Response

def home(handler: BaseHTTPRequestHandler, url_data, url_variables):
    host = handler.headers["Host"]
    print(f"GET request at {handler.path}, {host}")
    print(url_variables)
    new_path = handler.path + "return.html"
    print(f"Redirecting to {new_path}")

    res = Basic_GET_Response(None, handler, new_path)
    return res

def retrn(handler: BaseHTTPRequestHandler, url_data, url_variables):
    host = handler.headers["Host"]
    print(f"GET request at {handler.path}, {host}")

    res = Basic_GET_Response(None, handler, handler.path)
    return res

def display(handler: BaseHTTPRequestHandler, url_data, url_variables):
    print(url_variables, url_data)
    res = Basic_GET_Response(None, handler, handler.path, url_variables)
    return res
