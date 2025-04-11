from http.server import BaseHTTPRequestHandler
from typing import Any

from pydantic import BaseModel

from constants import HTTP_CODES, GET_mode
from utils import class_to_dict, try_int
from utils import get_base_path, get_complete_path

from mongo_connection import get_collection

import json

from bson import ObjectId
from pymongo.collection import Collection

def insert_to_db(path:str, data: dict[str, Any]):
    collection: Collection = get_collection(path)
    collection.insert_one(data)

def replace_to_db(path:str, query:dict[str, Any], data: dict[str, Any]):
    collection: Collection = get_collection(path)
    collection.replace_one(query, data)

def get_from_db(path:str, query: dict[str, Any]={}):
    collection: Collection = get_collection(path)
    print(collection)
    cursor: list[dict[str, Any]] = collection.find(query).to_list()
    docs: list[dict[str, Any]] = []
    for doc in cursor:
        doc.pop("_id")
        docs.append(doc)
    print("docs:", docs)
    return docs if len(docs) else None

doc_to_bytes = lambda doc: bytes(json.dumps(doc), "utf-8") if doc is not None else None

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
        open_path = get_base_path(new_path, url_variables)
        
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
                    docs = get_from_db(open_path, query)
                    self.content = doc_to_bytes(docs)
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
    def __init__(self, content: bytes|str, model: BaseModel):
        self.id = ObjectId()
        try:
            class PassModel (BaseModel, model):
                pass
            
            json_data: dict[str, Any] = json.loads(content)
            cls_dict = class_to_dict(model, json_data)

            print(cls_dict)

            try:
                test_data: PassModel = PassModel(**cls_dict)
                self.data: dict[str, Any] = cls_dict
            except Exception as e:
                print("Data is incorrect: ", json_data)
                print("Error: ", e)
                self.data = None
            
            if "id" in json_data:
                id = ObjectId(json_data["id"])

                if ObjectId.is_valid(id):
                    self.id = id

        except Exception as e:
            print("There was a problem at Set_DB:", e.with_traceback(None))
    id: ObjectId
        
class Basic_POST_Response ():
    def __init__(
            self, 
            status_code:int|None, 
            handler:BaseHTTPRequestHandler, 
            new_path:str|None, 
            body: Set_DB,
            url_variables: dict[str, str]={}
        ):
        new_path = handler.path if new_path is None else new_path
        self.status_code = status_code or 400

        open_path = get_base_path(handler.path, url_variables)

        print("POST")
        print(body)

        query = {}

        search_key = handler.search_keys["/" + open_path]

        query[search_key] = body.data[search_key]

        doc = get_from_db(open_path, query)

        if doc is not None:
            print("Updating ", doc)
            replace_to_db(open_path, query, body.data)

        else:
            print("Create something: ", body.data)
            
            insert_to_db(open_path, body.data)