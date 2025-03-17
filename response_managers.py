from http.server import BaseHTTPRequestHandler

from utils import get_base_path, get_complete_path

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
            self.content = b""
        
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