from http.server import BaseHTTPRequestHandler
from typing import Any
from response_managers import Basic_GET_Response, HTTP_CODES, GET_mode

def home(handler: BaseHTTPRequestHandler, query, url_variables):
    new_path = handler.path + "return.html"
    print(f"Redirecting to {new_path}")

    res = Basic_GET_Response(HTTP_CODES.REDIRECT, handler, new_path)
    return res

def retrn(handler: BaseHTTPRequestHandler, query, url_variables):
    res = Basic_GET_Response(HTTP_CODES.SUCCESS, handler, handler.path)
    return res

def display(handler: BaseHTTPRequestHandler, query, url_variables):
    res = Basic_GET_Response(HTTP_CODES.SUCCESS, handler, handler.path, url_variables)
    return res

def try_int (value: Any):
    result = None
    try:
        result = int(value)
    except:
        result = value
    
    return result

def show_set(handler: BaseHTTPRequestHandler, query: dict[str, Any], url_variables):
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

    res = Basic_GET_Response(
        HTTP_CODES.SUCCESS, 
        handler, 
        handler.path, 
        mode=GET_mode.DATABASE,
        query=last_query
    )
    return res