from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable
from GET_Actions import display, home, retrn, show_set
from POST_Actions import post_person
from RequestHandler import RequestHandler
from response_managers import Basic_POST_Response

print_exp = lambda e, req: print(f"There was an exception while trying to proccess your {req} request:\n{repr(e)}")

class Server ():
    def __init__(self, address: str, port: int):
        self.session = HTTPServer((address, port), RequestHandler)
        self.address = address
        self.port = port

    def CALL (self, path: str, callback: Callable, caller_lib: dict[str, Callable]):
        if callback and path:
            caller_lib[path] = callback

    def GET (self, path: str, callback: Callable):
        try:
            self.CALL(path, callback, RequestHandler.get_callers)
        except Exception as e:
            print_exp(e, "GET")

    def POST (
            self, 
            path: str, 
            callback: Callable[
                [BaseHTTPRequestHandler, bytes, dict[str, Any]], 
                Basic_POST_Response
            ]
        ):
        try:
            self.CALL(path, callback, RequestHandler.post_callers)
        except Exception as e:
            print_exp(e, "POST")
        
    def start(self):
        print ("Starting Server...")
        if self.session:
            print(f"Session started at http://{self.address}:{self.port}")
            with self.session as Http_Server:
                Http_Server.serve_forever()
        else:
            print("There's no session available.")

my_server = Server("localhost", 8080)

my_server.GET("/", home)
my_server.GET("/return.html", retrn)
my_server.GET("/[ID]/display.html", display)
my_server.GET("/set", show_set)
my_server.POST("/set", post_person)
my_server.start()
