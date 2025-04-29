from typing import Any
from response_managers import Basic_GET_Response
from utils import try_int
from RequestHandler import RequestHandler

def home(handler: RequestHandler, query: dict[str, Any], url_variables: dict[str, str]):
    new_path = handler.path + "return"
    print(f"Redirecting to {new_path}")

    res = Basic_GET_Response(handler.path)
    res.redirect(handler, new_path)

    return res

def retrn(handler: RequestHandler, query: dict[str, Any], url_variables: dict[str, str]):
    res = Basic_GET_Response(handler.root + "/return.html")
    res.send_file() # should have url_variables as a argument
    return res

def display(handler: RequestHandler, query: dict[str, Any], url_variables: dict[str, str]):
    print("display")
    res = Basic_GET_Response(handler.root + handler.path + ".html")
    res.send_file(url_variables)
    return res

def show_set(handler: RequestHandler, query: dict[str, Any], url_variables: dict[str, str]):
    last_query = {}

    last_query["$or"] = []

    print(query)

    for key, value in query.items():
        arr: list = value
        or_array = []
        if len(arr) >= 2:
            for val in arr:
                or_array.append({ key: try_int(val) })
                
            last_query["$or"].extend(or_array)

        elif len(arr) == 1:
            last_query[key] = try_int(value[0])

    if len(last_query["$or"]) == 0:
        last_query.pop("$or")

    print(last_query)

    res = Basic_GET_Response("set")
    res.send_db(last_query)
    return res