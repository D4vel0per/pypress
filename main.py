from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from requests.exceptions import HTTPError
from typing import Callable
from GET_Actions import display, home, retrn, show_set
from POST_Actions import post_person
from response_managers import HTTP_CODES, Basic_GET_Response, Basic_POST_Response, Set_DB
from utils import get_complete_path, get_url_variables, get_url_query, is_var_url

def find_base(path:str, callers: list[Callable]) -> str|None: 
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

    def do_POST (self): # Create a New record or update an old one
        default_content = Set_DB(json.dumps(
            {
                "name": "Omar",
                "age": 18,
                "description": "Your Creator."
            }
        ))
        POST_caller = lambda a, b, c: Basic_POST_Response(None, self, self.path, default_content)

        base_path = find_base(self.path, self.post_callers)

        if base_path:
            POST_caller = self.post_callers[base_path]

        print("Also works")
        
        try:
            print("Inside try, content length is", self.headers["Content-Length"])
            c_length = int(self.headers["Content-Length"])
            content = self.rfile.read(c_length)

            res: Basic_POST_Response = POST_caller(self, content)
            self.send_response(res.status_code)

        except HTTPError as e:
            self.send_error(e.response.status_code, e.response.reason)

        self.send_header("Location", get_complete_path(self))
        self.end_headers()

    def do_GET (self): # Find records

        exists = self.path in self.get_callers
        url_variables = {}
        GET_caller = lambda a, b, c: Basic_GET_Response(None, self, self.path)
        base_path = find_base(self.path, self.get_callers)

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


    def POST (self, path: str, callback: Callable):
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
