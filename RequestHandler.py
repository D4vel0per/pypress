from http.server import SimpleHTTPRequestHandler
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from requests import HTTPError

from constants import HTTP_CODES
from response_managers import (
    Basic_DELETE_Response, 
    Basic_GET_Response, 
    Basic_PATCH_Response, 
    Basic_POST_Response, 
    Basic_PUT_Response,
    Basic_Response
)
from utils import get_complete_path, get_url_variables, is_var_url

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
    def __init__(self, c: Callable, url_v: dict[str, str]):
        self.caller = c
        self.url_variables = url_v
    
class RequestHandler (SimpleHTTPRequestHandler):
    get_callers: (dict[
        str, Callable[[SimpleHTTPRequestHandler, dict[str, Any], dict[str, str]], Basic_GET_Response]
    ]) = {}
    post_callers: (dict[
        str, Callable[[SimpleHTTPRequestHandler, bytes, dict[str, str]], Basic_POST_Response]
    ]) = {}
    put_callers: (dict[
        str, Callable[[SimpleHTTPRequestHandler, bytes, dict[str, str]], Basic_PUT_Response]
    ]) = {}
    patch_callers: (dict[
        str, Callable[[SimpleHTTPRequestHandler, bytes, dict[str, str]], Basic_PATCH_Response]
    ]) = {}
    delete_callers: (dict[
        str, Callable[[SimpleHTTPRequestHandler, bytes, dict[str, str]], Basic_DELETE_Response]
    ]) = {}
    root: str

    def read_content (self):
        content: bytes = b""
        if "Content-Length" in dict(self.headers):
            c_length = int(self.headers["Content-Length"])
            content = self.rfile.read(c_length)
        
        return content
    
    def write_content (self, content=bytes):
        try:
            if content is not None:
                self.wfile.write(content)
        except Exception as e:
            print("Error while writing data:", e)
    
    def get_utilities (
            self, 
            callers: dict[str,(
                Callable[[SimpleHTTPRequestHandler, bytes, dict[str, str]], Basic_Response] |
                Callable[[SimpleHTTPRequestHandler, dict[str, Any], dict[str, str]], Basic_Response]
            )]
        ):
        caller: (
            Callable[[RequestHandler, bytes, dict[str, str]], Basic_Response] |
            Callable[[RequestHandler, dict[str, Any], dict[str, str]], Basic_Response]
        )

        base_path = find_base_for_caller(self.path, callers)
        url_variables = {}

        if base_path:
            caller = callers[base_path]
            url_variables = get_url_variables(base_path, self.path)
        
        return BodyUtilities(caller, url_variables) if base_path else None

    def send_res (self, res: Basic_Response):
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
            self.write_content(res.content)
    
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
        utilities = self.get_utilities(self.get_callers)

        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            query = parse_qs(urlparse(self.path).query)
            res: Basic_GET_Response = utilities.caller(self, query, utilities.url_variables)
            self.send_res(res)
            self.write_content(res.content)

    def set_root (root: str):
        RequestHandler.root = root