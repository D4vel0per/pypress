from http.server import HTTPServer
from pathlib import Path
from typing import Any, Callable
from . import RequestHandler, RequestData
from .ResponseManagers import (
    Basic_DELETE_Response,
    Basic_GET_Response,
    Basic_PATCH_Response,
    Basic_POST_Response,
    Basic_PUT_Response,
    Basic_Response
)

from .Server_Exceptions import *

class Server ():
    root: str
    def __init__(self, address: str, root_folder: Path):
        inet_address = address.split(":")[0:2]
        inet_address[1] = int(inet_address[1])
        self.session = HTTPServer(tuple(inet_address), RequestHandler)
        self.address = address
        if root_folder.is_absolute():
            Basic_GET_Response.root = root_folder.as_posix()
        else:
            raise InvalidRootError("Path is not absolute. Try using Path.cwd() for root_folder argument")

    def CALL (
            self, 
            path: str, 
            callback: Callable[[RequestHandler, dict[str, Any]|bytes, dict[str, str]], Basic_Response], 
            caller_lib: dict[
                str, Callable[[RequestHandler, dict[str, Any]|bytes, dict[str, str]], Basic_Response]
            ]
        ):
        if callback and path:
            caller_lib[path] = callback

    def GET (
            self, 
            path: str, 
            callback: Callable[[RequestData], Basic_GET_Response]
        ):
        self.CALL(path, callback, RequestHandler.get_callers)
        

    def POST (
            self, 
            path: str, 
            callback: Callable[[RequestData], Basic_POST_Response]
        ):
        self.CALL(path, callback, RequestHandler.post_callers)

    def PUT (
            self,
            path: str,
            callback: Callable[[RequestData], Basic_PUT_Response]
    ):
        self.CALL(path, callback, RequestHandler.put_callers)

    def PATCH (
            self,
            path: str,
            callback: Callable[[RequestData], Basic_PATCH_Response]
    ):
        self.CALL(path, callback, RequestHandler.patch_callers)

    def DELETE (
            self,
            path: str,
            callback: Callable[[RequestData], Basic_DELETE_Response]
    ):
        self.CALL(path, callback, RequestHandler.delete_callers)
        
    def start(self):
        print ("Starting Server...")
        if self.session:
            print(f"Session started at http://{self.address}")
            with self.session as Http_Server:
                Http_Server.serve_forever()
        else:
            print("There's no session available.")