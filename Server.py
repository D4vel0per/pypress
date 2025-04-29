from http.server import HTTPServer
from pathlib import Path
from typing import Any, Callable
from RequestHandler import RequestHandler
from response_managers import (
    Basic_DELETE_Response, 
    Basic_GET_Response, 
    Basic_PATCH_Response, 
    Basic_POST_Response, 
    Basic_PUT_Response
)

class InvalidRootError (BaseException):
    """Path is not absolute. Try using Path.cwd() for root_folder argument"""

class Server ():
    def __init__(self, address: str, port: int, root_folder: Path):
        self.session = HTTPServer((address, port), RequestHandler)
        self.address = address
        self.port = port
        root = str(root_folder.as_posix())
        if root_folder.is_absolute():
            RequestHandler.set_root(root)
        else:
            raise InvalidRootError("Path is not absolute. Try using Path.cwd() for root_folder argument")

    def CALL (self, path: str, callback: Callable, caller_lib: dict[str, Callable]):
        if callback and path:
            caller_lib[path] = callback

    def GET (
            self, 
            path: str, 
            callback: Callable[[RequestHandler, dict[str, Any], dict[str, str]], Basic_GET_Response]
        ):
        self.CALL(path, callback, RequestHandler.get_callers)
        

    def POST (
            self, 
            path: str, 
            callback: Callable[[RequestHandler, bytes, dict[str, Any]], Basic_POST_Response]
        ):
        self.CALL(path, callback, RequestHandler.post_callers)

    def PUT (
            self,
            path: str,
            callback: Callable[[RequestHandler, bytes, dict[str, Any]], Basic_PUT_Response]
    ):
        self.CALL(path, callback, RequestHandler.put_callers)

    def PATCH (
            self,
            path: str,
            callback: Callable[[RequestHandler, bytes, dict[str, Any]], Basic_PATCH_Response]
    ):
        self.CALL(path, callback, RequestHandler.patch_callers)

    def DELETE (
            self,
            path: str,
            callback: Callable[[RequestHandler, bytes, dict[str, Any]], Basic_DELETE_Response]
    ):
        self.CALL(path, callback, RequestHandler.delete_callers)
        
    def start(self):
        print ("Starting Server...")
        if self.session:
            print(f"Session started at http://{self.address}:{self.port}")
            with self.session as Http_Server:
                Http_Server.serve_forever()
        else:
            print("There's no session available.")