from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Callable
from GET_Actions import display, home, retrn, show_set
from POST_Actions import post_person
from PUT_Actions import put_person
from RequestHandler import RequestHandler
from actions.DELETE_actions import delete_person
from actions.PATCH_actions import patch_person
from response_managers import Basic_DELETE_Response, Basic_PATCH_Response, Basic_POST_Response, Basic_PUT_Response

print_exp = lambda e, req: print(f"There was an exception while trying to proccess your {req} request:\n{repr(e)}")

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

    def GET (self, path: str, callback: Callable):
        self.CALL(path, callback, RequestHandler.get_callers)
        

    def POST (
            self, 
            path: str, 
            callback: Callable[
                [BaseHTTPRequestHandler, bytes, dict[str, Any]], 
                Basic_POST_Response
            ]
        ):
        self.CALL(path, callback, RequestHandler.post_callers)

    def PUT (
            self,
            path: str,
            callback: Callable[[BaseHTTPRequestHandler, bytes, dict[str, Any]], Basic_PUT_Response]
    ):
        self.CALL(path, callback, RequestHandler.put_callers)

    def PATCH (
            self,
            path: str,
            callback: Callable[[BaseHTTPRequestHandler, bytes, dict[str, Any]], Basic_PATCH_Response]
    ):
        self.CALL(path, callback, RequestHandler.patch_callers)

    def DELETE (
            self,
            path: str,
            callback: Callable[[BaseHTTPRequestHandler, bytes, dict[str, Any]], Basic_DELETE_Response]
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

my_server = Server("localhost", 8080, Path.cwd())

my_server.GET("/", home)
my_server.GET("/return", retrn)
my_server.GET("/[ID]/display", display)
my_server.GET("/set", show_set)
my_server.POST("/set", post_person)
my_server.PUT("/set/[name?]", put_person)
my_server.PATCH("/set/[name]", patch_person)
my_server.DELETE("/set/[name]", delete_person)
my_server.start()