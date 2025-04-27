from typing import Any
from http.server import BaseHTTPRequestHandler
import re
import base64

def bytes_to_b64 (data: bytes):
    result = base64.b64encode(data).decode("ascii")
    return result

def try_int (value: Any):
    result = None
    try:
        result = int(value)
    except:
        result = value
    
    return result

def is_var_url (base_path:str, actual_path:str):
    variables = get_url_variables(base_path, actual_path)
    pair_path = base_path + ""
    for key in variables:
        if re.search("^\[.*\?\]$", key):
            simple_match = is_var_url(base_path.replace(key, ""), actual_path)
            if simple_match: return True

        pair_path = pair_path.replace(key, variables[key])

    return re.sub("^/+|/+$", "", pair_path) == re.sub("^/+|/+$", "", actual_path)

def get_base_path (actual_path: str, url_variables: dict[str, str]):
    base_path = actual_path + ""
    for key, value in url_variables.items():
        base_path = actual_path.replace(value, key)

    base_path = base_path.split("?")[0] # Just in case it has a query

    return base_path.removeprefix("/")

def get_url_variables(base_path:str, actual_path:str):
    separate_path = lambda path: list(filter(lambda a: bool(a), path.split("/")))

    keys: list[str] = separate_path(base_path)
    values: list[str] = separate_path(actual_path)

    result = {}
    
    for i in range(len(keys)):
        key = keys[i]
        if re.search("^\[.*\]$", key) and len(values) > i:
            result[key] = values[i]
        elif re.search("^\[.*\?\]$", key):
            result[key] = ""

    return result

def get_complete_path(handler: BaseHTTPRequestHandler):
    host = handler.headers["Host"]
    base = f"http://{host}{handler.path}"
    return base

def class_to_dict (clss):
    annotations: dict = clss.__annotations__
    proto_dict: dict[str, Any] = clss.__dict__
    constants_dict: dict = {}

    for key, value in proto_dict.items():
        if not (key.startswith("__") and key.endswith("__")):
            constants_dict[key] = value

    cls_dict = {}
    print("Inside class_to_dict")
    print("Annotations: ", clss.__annotations__)
    

    for (key, value_cls) in annotations.items():
        print (key, value_cls)
        cls_dict[key] = value_cls

    cls_dict.update(constants_dict)
    
    return cls_dict