import base64
from http.server import BaseHTTPRequestHandler
from typing import Any

from pathlib import Path

from pydantic import BaseModel

from constants import HTTP_CODES, GET_mode, Mongo_Update_Operators
from utils import bytes_to_b64, class_to_dict, get_base_path, get_complete_path

from mongo_connection import get_collection

import json

from pymongo.collection import Collection

def insert_to_db(collection:str, data: dict|list):
    collection: Collection = get_collection(collection)
    if type(data) is list:
        collection.insert_many(data)
    elif type(data) is dict:
        collection.insert_one(data)

def replace_to_db(path:str, query:dict[str, Any], data: dict[str, Any]|list):
    collection: Collection = get_collection(path)
    if type(data) is list:
        collection.delete_many(query)
        collection.insert_many(data)
    elif type(data) is dict:
        collection.replace_one(query, data)

def update_to_db(path:str, query:dict[str, Any], data: dict[str, Any], update_many: bool = False):
    collection: Collection = get_collection(path)
    print(path)
    if update_many:
        collection.update_many(query, data)
    else:
        collection.update_one(query, data)

def delete_to_db(path:str, query:dict[str, Any], delete_many: bool = False):
    collection: Collection = get_collection(path)
    if delete_many:
        collection.delete_many(query)
    else:
        collection.delete_one(query)

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

'''
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
'''


'''
res = Basic_GET_Response("set", {'name': "Steve"})
res.get_file() -> None (Not an absolute path, file searching do not accepts queries)
res.get_db() -> [{...}, {...}, {...}]

-------------------------------------------------------------------------------------------

res = Basic_GET_Response("set", {})
res.get_file() -> None (Not an absolute path, file searching do not accepts queries)
res.get_db() -> [{...}, {...}, {...}, {...}, {...}, {...}, ...]

-------------------------------------------------------------------------------------------

res = Basic_GET_Response("set")
res.get_file() -> None (Not an absolute path)
res.get_db() -> None (Not Allowed: You need atleast a query to call your db)

-------------------------------------------------------------------------------------------

res = Basic_GET_Response("[absolute-path-file]")
res.get_file() -> b"Something"
res.get_db() -> None (Not Allowed: You need atleast a query to call your db)

-------------------------------------------------------------------------------------------

res = Basic_GET_Response("[absolute-path-folder]")
res.get_file() -> {
    "filename1.txt": b"Something"
}
res.get_db() -> None (Not Allowed: You need atleast a query to call your db)


'''
class Basic_GET_Response ():
    path: str
    status_code: HTTP_CODES
    content: bytes = None

    def __init__(
            self,
            path_or_collection_name: str
        ):

        self.status_code = HTTP_CODES.BAD_REQUEST
        self.path = path_or_collection_name

    
    def redirect(self, handler: BaseHTTPRequestHandler, new_path: str):
        self.status_code = HTTP_CODES.REDIRECT
        handler.path = new_path

    def send_file (self, url_variables: dict[str, str] = {}):
        path = Path(get_base_path(Path(self.path).as_posix(), url_variables))
        print(path)

        if path.exists() and path.is_absolute() and path.is_file():
            print("exists, is absolute and is a file")
            self.path = str(path)
        else:
            self.status_code = HTTP_CODES.NOT_FOUND
            
        try:
            file = Path(self.path)
            if file.is_file():
                with open(str(file), "rb") as file_data:
                    self.content = file_data.read()
                self.status_code = HTTP_CODES.SUCCESS

        except Exception as e:
            print(e)
            self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR

    def send_db (self, query: dict[str, Any]):
        try:
            if get_collection(self.path) is not None:
                docs = get_from_db(self.path, query)
                if docs is not None:
                    self.content = doc_to_bytes(docs)
                    self.status_code = HTTP_CODES.SUCCESS

        except Exception as e:
            print(e)
            self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR


def checkModel (model: Any, data:dict|list[dict]):
    class PassModel (BaseModel, model):
        pass

    try:
        if type(data) is list:
            for obj in data:
                PassModel.model_validate(obj)
        elif type(data) is dict:
            PassModel.model_validate(data)
        else:
            return False
        
        return True
    except:
        return False
        
class Basic_POST_Response (): # CREATE
    status_code: HTTP_CODES
    body: dict|list
    collection_name: str
    valid_model: bool
    content: str

    def __init__(
            self, 
            collection_name:str,
            body: dict|list,
            model: Any
        ):
        self.valid_model = checkModel(model, body)
        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST
        self.content = b""

        if get_collection(collection_name) is None:
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None

    def send(self, html:str = ""):
        if self.valid_model:
            self.content = html
            try:
                insert_to_db(self.collection_name, self.body)
                self.status_code = HTTP_CODES.CREATED
            except Exception as e:
                print("Internal Server Error on Post: ", e.with_traceback())
                self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        else:
            self.status_code = HTTP_CODES.BAD_REQUEST


class Basic_PUT_Response ():
    status_code: HTTP_CODES
    body: dict|list
    collection_name: str
    valid_model: bool
    query: dict[str, Any]
    ref: Any
    
    def __init__(
            self, 
            collection_name:str,
            body: dict|list,
            query: dict[str, Any],
            model: Any
        ):
        
        self.valid_model = checkModel(model, body)

        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST

        if get_collection(collection_name) is None:
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None
            self.query = query if self.valid_model else None

    def send(self, path: str = None, ref_key: str = None):
        if self.valid_model:
            doc = get_from_db(self.collection_name, self.query)

            print(doc)

            if ref_key in self.body and path:
                self.ref = f"{path}/{self.body[ref_key]}"
            else:
                self.ref = path

            if doc is None:
                try:
                    insert_to_db(self.collection_name, self.body)
                    self.status_code = HTTP_CODES.CREATED if path or ref_key else HTTP_CODES.NO_CONTENT
                except:
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
            else:
                try:
                    replace_to_db(self.collection_name, self.query, self.body)
                    self.status_code = HTTP_CODES.SUCCESS if path or ref_key else HTTP_CODES.NO_CONTENT
                except:
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR

def isPatchableBy (model: Any, patch: dict[str, Any]):
    model_dict: dict = class_to_dict(model)
    eval_patch = {}

    for key, value in patch.items():
        if key in list(class_to_dict(Mongo_Update_Operators).values()):
            eval_patch.update(patch[key])
        else:
            eval_patch.update({ key: value })

    for key, value in eval_patch.items():
        key_in_model = key in model_dict
        is_type_eq = model_dict[key] is type(value) if key_in_model else False 
        if not key_in_model or not is_type_eq:
            return False
        
    return True
        
class Basic_PATCH_Response (): # UPDATE ONLY WORKS WITH $ OPERATORS
    def __init__(
            self,
            collection_name:str,
            body: dict,
            query: dict,
            model: Any
    ):
        self.valid_model = isPatchableBy(model, body)
        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST

        if get_collection(collection_name) is None:
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None
            self.query = query if self.valid_model else None
        
    def send(self, path: str = None, ref_key: str = None, patch_many = False):
        if self.valid_model:
            doc = get_from_db(self.collection_name, self.query)

            if ref_key in self.body and path:
                self.ref = f"{path}/{self.body[ref_key]}"
                self.status_code = HTTP_CODES.SUCCESS
            else:
                self.ref = path
                self.status_code = HTTP_CODES.NO_CONTENT

            if doc is not None:
                try:
                    update_to_db(self.collection_name, self.query, self.body, patch_many)
                except Exception as e:
                    print(e.with_traceback())
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR


class Basic_DELETE_Response ():
    def __init__(
            self,
            collection_name: str,
            query: dict[str, Any]

    ):
        self.docs = get_from_db(collection_name, query)
        self.collection_name = collection_name
        self.query = query
        self.status_code = HTTP_CODES.ACCEPTED
        self.content = b""

    def send (self, success_msg: bytes = b"", delete_many = False):
        
        if self.docs is not None:
            try:
                delete_to_db(self.collection_name, self.query, delete_many)
                self.status_code = HTTP_CODES.SUCCESS if success_msg else HTTP_CODES.NO_CONTENT
                self.content = success_msg
            except:
                self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        else:
            self.status_code = HTTP_CODES.NOT_FOUND