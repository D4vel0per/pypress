from http.server import BaseHTTPRequestHandler
from typing import Any

from utils import try_int
from utils import get_base_path, get_complete_path

from mongo_connection import get_collection

import json

from bson import ObjectId
from pymongo.collection import Collection

class HTTP_CODES ():
    REDIRECT = 303
    SUCCESS = 200
    CREATED = 201
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class GET_mode ():
    FILE = "FILE"
    DATABASE = "DB"

def get_from_db(path:str, query: dict[str, Any]={}):
    path = path.removeprefix("/")
    collection: Collection = get_collection(path)
    print(collection)
    cursor: list[dict[str, Any]] = collection.find(query).to_list()
    docs = []
    for doc in cursor:
        doc.pop("_id")
        docs.append(doc)
    print("docs:", docs)
    return bytes(json.dumps(docs), "utf-8")

class Basic_GET_Response ():
    def __init__(
            self, 
            status_code:HTTP_CODES, 
            handler:BaseHTTPRequestHandler, 
            new_path:str|None, 
            url_variables: dict[str, str]={},
            mode:GET_mode=GET_mode.FILE,
            query: dict[str, str]={}
        ):
        new_path = handler.path if new_path is None else new_path 
        
        self.status_code = status_code
        open_path = get_base_path(new_path, url_variables).removeprefix("/")
        
        self.url = get_complete_path(handler)
        self.path = new_path
        self.url_variables = url_variables
        self.content = b""

        print("QUERY: ", query)
        print("URL VARIABLES: ", url_variables)

        if status_code != HTTP_CODES.REDIRECT:
            try:
                if mode == GET_mode.FILE:
                    with open(open_path) as http_file:
                        self.content = bytes(http_file.read(), "utf-8")
                else:
                    self.content = get_from_db(open_path, query)
            except Exception as e:
                print (e)
                self.status_code = HTTP_CODES.NOT_FOUND

        print_status = lambda s: f"Basic_GET_Response -> {s}"
        match self.status_code:
            case HTTP_CODES.SUCCESS:
                print_status("200 OK") # Retrieve data
            case HTTP_CODES.REDIRECT:
                print_status("303 REDIRECT") # Just redirect to some other route
                print(f"Going from {handler.path} to {new_path}")
                handler.path = new_path

            case HTTP_CODES.NOT_FOUND:
                print_status("404 NOT FOUND") 
                # Handle this XD
            case HTTP_CODES.INTERNAL_SERVER_ERROR:
                print_status("500 INTERNAL SERVER ERROR")
                # I'll do this later (I won't)
        
class Set_DB:
    def __init__(self, content: bytes|str):
        self.id = ObjectId()
        try:
            json_data: dict[str, Any] = json.loads(content)

            self.name = json_data["name"]
            self.age = try_int(json_data["age"])
            self.description = json_data["description"]
            
            if "id" in json_data:
                id = ObjectId(json_data["id"])

                if ObjectId.is_valid(id):
                    self.id = id

        except Exception as e:
            print("There was a problem at Set_DB:", e.with_traceback(None))

    name: str
    age: int
    description: str
    id: ObjectId

def search_by_name (collection: Collection, name: str) -> Set_DB|None:
    result: Set_DB|None = collection.find_one({ name: name })
    return result
        
class Basic_POST_Response ():
    def __init__(
            self, 
            status_code:int|None, 
            handler:BaseHTTPRequestHandler, 
            new_path:str|None, 
            body: Set_DB
        ):
        new_path = handler.path if new_path is None else new_path
        self.status_code = status_code or 400

        set_col = get_collection("set")

        doc = search_by_name(set_col, body.name)

        if doc is not None:
            print("Update ", doc.name, f", {str(doc.name)}")
            set_col
        else:
            print("Create something: ", body.name)
            
            set_col.insert_one({
                'name': body.name,
                'age': body.age,
                'description': body.description,
                '_id': body.id
            })