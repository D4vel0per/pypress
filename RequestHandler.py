from http.server import BaseHTTPRequestHandler
import json
from typing import Callable

from pydantic import BaseModel
from requests import HTTPError

from constants import HTTP_CODES
from response_managers import Basic_GET_Response, Basic_POST_Response, Set_DB
from utils import get_complete_path, get_url_query, get_url_variables, is_var_url

def find_base_for_caller(path:str, callers: list[Callable]) -> str: 
    path = path.split("?")[0]
    exists = path in callers
    base = None
    if not exists:
        for base_path in callers:
            if is_var_url(base_path, path):
                exists = True
                base:str = base_path
    else:
        base = path

    return base


class RequestHandler (BaseHTTPRequestHandler):
    get_callers: dict[str, Callable] = {}
    post_callers: dict[str, Callable] = {}
    path_models: dict[str, BaseModel] = {}
    search_keys: dict[str, str] = {}

    def read_content (self):
        c_length = int(self.headers["Content-Length"])
        content = self.rfile.read(c_length)
        return content

    def do_POST (self): # Create a New record or update an old one
        class DefaultModel:
            name:str
            age:int
            description:str
        
        default_content = Set_DB(json.dumps(
            {
                "name": "Omar",
                "age": 18,
                "description": "Your Creator."
            }
        ), DefaultModel)
        POST_caller = lambda a, b, c: Basic_POST_Response(None, self, self.path, default_content)

        base_path = find_base_for_caller(self.path, self.post_callers)
        url_variables = {}

        if base_path:
            POST_caller = self.post_callers[base_path]
            url_variables = get_url_variables(base_path, self.path)


        print("Also works")
        
        try:
            print("Inside try, content length is", self.headers["Content-Length"])
            content = self.read_content()
            model = self.path_models[base_path]

            data = Set_DB(content, model)

            res: Basic_POST_Response = POST_caller(self, data, url_variables)
            self.send_response(res.status_code)

        except HTTPError as e:
            self.send_error(e.response.status_code, e.response.reason)

        self.send_header("Location", get_complete_path(self))
        self.end_headers()

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