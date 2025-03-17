from http.server import HTTPServer, BaseHTTPRequestHandler
from requests.exceptions import HTTPError
from typing import Callable
from GET_Actions import display, home, retrn
from utils import Basic_GET_Response, get_complete_path, get_url_variables, url_to_dict, is_var_url

class RequestHandler (BaseHTTPRequestHandler):
    get_callers: dict[str, Callable] = {}
    post_callers: dict[str, Callable] = {}

    def do_POST (self):
        if self.path not in self.get_callers:
            return
        
        try:
            content = self.rfile.read()

            res: Basic_GET_Response = self.post_callers[self.path](self, content)
            self.send_response(res.status_code)

        except HTTPError as e:
            self.send_error(e.response.status_code, e.response.reason)

    def do_GET (self):

        exists = self.path in self.get_callers
        url_variables = {}
        GET_caller = lambda a, b, c: Basic_GET_Response(None, self, self.path)

        if not exists:
            for base_path in self.get_callers:
                if is_var_url(base_path, self.path):
                    exists = True
                    url_variables = get_url_variables(base_path, self.path)
                    GET_caller = self.get_callers[base_path]
        else:
            GET_caller = self.get_callers[self.path]
        
        if not exists:
            print("Prone to error")
        
        try:
            url_data = url_to_dict(self.path)

            res: Basic_GET_Response = GET_caller(self, url_data, url_variables)

            content = res.content
            
            if res.status_code == 200:
                print("200 OK")
            elif res.status_code == 303:
                print("303 REDIRECT")
                self.path = res.path
            elif res.status_code == 404:
                print("404 NOT_FOUND")
                self.path = "/not_found.html"
                res.status_code = 303 # redirect

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
        if self.session:
            with self.session as Http_Server:
                Http_Server.serve_forever()

my_server = Server("localhost", 8080)

my_server.GET("/", home)
my_server.GET("/return.html", retrn)
my_server.GET("/[ID]/display.html", display)

# ADD TOMORROW: /something/[ID]/display.html

print("Starting Server...")
my_server.start()
