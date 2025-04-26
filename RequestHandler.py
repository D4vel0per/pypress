from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from typing import Any, Callable

from requests import HTTPError

from constants import HTTP_CODES
from response_managers import (
    Basic_DELETE_Response, 
    Basic_GET_Response, 
    Basic_PATCH_Response, 
    Basic_POST_Response, 
    Basic_PUT_Response
)
from utils import get_complete_path, get_url_query, get_url_variables, is_var_url

def find_base_for_caller(path:str, callers: list[Callable]) -> str: 
    path = path.split("?")[0]
    exists = path in callers
    base: str = None
    if not exists:
        for base_path in callers:
            if is_var_url(base_path, path):
                exists = True
                base = base_path
    else:
        base = path
    return base

class BodyUtilities:
    def __init__(self, c, url_v):
        self.caller = c
        self.url_variables = url_v

class Basic_Response:
    status_code: HTTP_CODES = HTTP_CODES.SUCCESS
    
class RequestHandler (SimpleHTTPRequestHandler):
    get_callers: dict[str, Callable] = {}
    post_callers: dict[str, Callable] = {}
    put_callers: dict[str, Callable] = {}
    patch_callers: dict[str, Callable] = {}
    delete_callers: dict[str, Callable] = {}

    def read_content (self):
        content: bytes = b""
        if "Content-Length" in dict(self.headers):
            c_length = int(self.headers["Content-Length"])
            content = self.rfile.read(c_length)
        
        return content
    
    def write_content (self, content=bytes):
        try:
            self.wfile.write(content)
        except Exception as e:
            print("Error while writing data:", e)
    
    def get_utilities (self, callers: dict[str, Callable]):
        caller: Callable # Luego se hará una clase general
        base_path = find_base_for_caller(self.path, callers)
        url_variables = {}

        if base_path:
            caller = callers[base_path]
            url_variables = get_url_variables(base_path, self.path)
        
        return BodyUtilities(caller, url_variables) if base_path else None

    def send_res (self, res):
        try:
            self.send_response(res.status_code, "CONTENT")
        except HTTPError as e:
            self.send_error(e.response.status_code, e.response.reason)

        self.send_header("Location", get_complete_path(self))
        self.end_headers()
    
    def do_PUT (self):
        utilities = self.get_utilities(self.put_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            content = self.read_content()
            res: Basic_PUT_Response = utilities.caller(self, content, utilities.url_variables)
            self.send_res(res)
    
    def do_PATCH (self):
        utilities = self.get_utilities(self.patch_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            content = self.read_content()
            res: Basic_PATCH_Response = utilities.caller(self, content, utilities.url_variables)
            self.send_res(res)
    
    def do_DELETE (self):
        utilities = self.get_utilities(self.delete_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.BAD_REQUEST)
        else:
            content = self.read_content()
            res: Basic_DELETE_Response = utilities.caller(self, content, utilities.url_variables)
            self.send_res(res)
            self.write_content(res.content)

    def do_POST (self): # Create new records
        utilities = self.get_utilities(self.post_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            content = self.read_content()
            res: Basic_POST_Response = utilities.caller(self, content, utilities.url_variables)
            self.send_res(res)
            self.write_content(res.content)

    def do_GET (self): # Find records
        exists = self.path in self.get_callers
        url_variables = {}
        GET_caller = lambda a, b, c: Basic_GET_Response(None, self, self.path)
        base_path = find_base_for_caller(self.path, self.get_callers)

        if base_path:
            GET_caller = self.get_callers[base_path]
            url_variables = get_url_variables(base_path, self.path)
        elif not exists:
            print("Not an available path")
            self.send_response(HTTP_CODES.NOT_FOUND)
            self.end_headers()
            return
        
        try:
            query = get_url_query(self.path)

            host = self.headers["Host"]
            print(f"GET request at {self.path}, {host}")

            res: Basic_GET_Response = GET_caller(self, query, url_variables)

            content = res.content
            
            if res.status_code == 200:
                print("200 OK")
            elif res.status_code == 303:
                print("303 REDIRECT")
                self.path = res.path
            elif res.status_code == 404:
                print("404 NOT_FOUND")

            print(get_complete_path(self))
            self.send_response(res.status_code)

        except HTTPError as e:
            self.send_error(e.response.status_code, e.response.reason)
        self.send_header("Location", get_complete_path(self))
        self.end_headers()
        self.wfile.write(content)