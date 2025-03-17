from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler
import re

NOT_FOUND_PAGE = "/not_found.html"

class Basic_GET_Response ():
    def __init__(
            self, 
            status_code:int|None, 
            handler:BaseHTTPRequestHandler, 
            new_path:str|None, 
            url_variables: dict[str, str]={}
        ):
        new_path = handler.path if new_path is None else new_path
        
        self.status_code = status_code if status_code else self.__eval(handler, new_path)
        open_path = get_base_path(new_path, url_variables).removeprefix("/")
        try:
            with open(open_path) as http_file:
                self.content = bytes(http_file.read(), "utf-8")
        except:
            self.status_code = 404

            with open(NOT_FOUND_PAGE.removeprefix("/"), "rb") as not_found_page:
                self.content = not_found_page.read()
        
        self.url = get_complete_path(handler)
        self.path = new_path
        self.url_variables = url_variables

    def __eval(self, handler:BaseHTTPRequestHandler, new_path:str):
        if handler.path == new_path:
            return 200 # Same page, just retrieving data
        else:
            print(f"Going from {handler.path} to {new_path}")
            handler.path = new_path
            return 303 # Different page, ready for redirect

def url_to_dict(path: str):
    path_arr = path.split("?")
    page = path_arr[0]
    query = {}
    if len(path_arr) > 1:
        query = parse_qs(path_arr[1])

    return {
        "page": page,
        "query": query
    }

separate_path = lambda path: list(filter(lambda a: bool(a), path.split("/")))

def is_var_url (base_path:str, actual_path:str):
    variables = get_url_variables(base_path, actual_path)

    pair_path = base_path + ""

    for key in variables:
        pair_path = pair_path.replace(key, variables[key])

    return pair_path == actual_path

def get_base_path (actual_path: str, url_variables: dict[str, str]):
    base_path = actual_path + ""
    for key, value in url_variables.items():
        base_path = actual_path.replace(value, key)

    return base_path

def get_url_variables(base_path:str, actual_path:str):
    keys = separate_path(base_path)
    values = separate_path(actual_path)

    result = {}
    
    for i in range(len(keys)):
        key = keys[i]
        if re.search("^\[.*\]$", key) and len(values) > i:
            result[key] = values[i]

    return result

def get_complete_path(handler: BaseHTTPRequestHandler):
    host = handler.headers["Host"]
    base = f"http://{host}{handler.path}"
    return base