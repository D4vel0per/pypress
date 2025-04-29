from http.server import SimpleHTTPRequestHandler
import re

def is_var_url (base_path:str, actual_path:str):
    variables = get_url_variables(base_path, actual_path)
    pair_path = base_path + ""
    for key in variables:
        if re.search("^\[.*\?\]$", key):
            simple_match = is_var_url(base_path.replace(key, ""), actual_path)
            if simple_match: return True

        pair_path = pair_path.replace(key, variables[key])

    return re.sub("^/+|/+$", "", pair_path) == re.sub("^/+|/+$", "", actual_path)

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

def get_complete_path(handler: SimpleHTTPRequestHandler):
    host = handler.headers["Host"]
    base = f"http://{host}{handler.path}"
    return base