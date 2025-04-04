from typing import Any
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler
import re

def get_url_query(path: str):
    path_arr = path.split("?")
    query = {}
    if len(path_arr) > 1:
        query = parse_qs(path_arr[1])

    return query

separate_path = lambda path: list(filter(lambda a: bool(a), path.split("/")))

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
        pair_path = pair_path.replace(key, variables[key])

    return pair_path == actual_path

def get_base_path (actual_path: str, url_variables: dict[str, str]):
    base_path = actual_path + ""
    for key, value in url_variables.items():
        base_path = actual_path.replace(value, key)

    base_path = base_path.split("?")[0] # Just in case it has a query

    return base_path

def get_url_variables(base_path:str, actual_path:str):
    keys = separate_path(base_path)
    values = separate_path(actual_path)

    result = {}
    
    for i in range(len(keys)):
        key = keys[i]
        if re.search("^\[.*\]$", key) and len(values) > i:
            result[key] = values[i]

    return result

def get_complete_path(handler: BaseHTTPRequestHandler):
    host = handler.headers["Host"]
    base = f"http://{host}{handler.path}"
    return base

def class_to_dict (clss):
    annotations = clss.__annotations__
    cls_dict = {}
    
    for (key, value_cls) in annotations.items():
        value = clss.__dict__[key] if key in clss.__dict__ else None
        cls_dict[key] = (value, value_cls)
    
    return cls_dict