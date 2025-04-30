from http.server import BaseHTTPRequestHandler
from types import NoneType
from typing import Any

from pathlib import Path

from .constants import HTTP_CODES
from .base import DB
from .utilities import checkModel, get_base_path, isPatchableBy

import json

doc_to_bytes = lambda doc: bytes(json.dumps(doc), "utf-8") if doc is not None else None

class Basic_Response ():
    status_code: HTTP_CODES
    content: bytes|NoneType

class Basic_GET_Response (Basic_Response):
    root: str
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
        print(self.root, self.path)
        base_path = get_base_path(Path(self.path).as_posix(), url_variables)
        path = (
            Path(self.root).joinpath(base_path) if 
            self.root else 
            Path(base_path)
        )

        if path.exists() and path.is_absolute() and path.is_file():
            self.path = path.as_posix()
        else:
            self.status_code = HTTP_CODES.NOT_FOUND
            
        try:
            if path.is_file():
                with open(self.path, "rb") as file_data:
                    self.content = file_data.read()
                self.status_code = HTTP_CODES.SUCCESS

        except Exception as e:
            print(e)
            self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR

    def send_db (self, query: dict[str, Any]):
        try:
            if DB.collection_or_table_exists(self.path):
                docs = DB.get_from_db(self.path, query)
                print(docs)
                if docs is not None:
                    self.content = doc_to_bytes(docs)
                    self.status_code = HTTP_CODES.SUCCESS

        except Exception as e:
            print(e.with_traceback(None))
            self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        
class Basic_POST_Response (Basic_Response): # CREATE
    status_code: HTTP_CODES
    body: dict|list
    collection_name: str
    valid_model: bool
    content: bytes

    def __init__(
            self, 
            collection_name:str,
            body: dict|list,
            model: Any
        ):
        self.valid_model = checkModel(model, body)
        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST
        self.content = b""

        if DB.collection_or_table_exists(collection_name):
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None

    def send(self, html:bytes = b""):
        if self.valid_model:
            self.content = html
            try:
                DB.insert_to_db(self.collection_name, self.body)
                self.status_code = HTTP_CODES.CREATED
            except Exception as e:
                print("Internal Server Error on Post: ", e.with_traceback())
                self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        else:
            self.status_code = HTTP_CODES.BAD_REQUEST


class Basic_PUT_Response (Basic_Response):
    status_code: HTTP_CODES
    body: dict|list
    collection_name: str
    valid_model: bool
    query: dict[str, Any]
    
    def __init__(
            self, 
            collection_name:str,
            body: dict|list,
            query: dict[str, Any],
            model: Any
        ):
        
        self.valid_model = checkModel(model, body)

        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST

        if DB.collection_or_table_exists(collection_name):
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None
            self.query = query if self.valid_model else None

    def send(self, path: str = None):
        if self.valid_model:
            doc = DB.get_from_db(self.collection_name, self.query)

            print(doc)

            self.content = bytes(path, "utf-8")

            if doc is None:
                try:
                    DB.insert_to_db(self.collection_name, self.body)
                    self.status_code = HTTP_CODES.CREATED if path else HTTP_CODES.NO_CONTENT
                except:
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
            else:
                try:
                    DB.replace_to_db(self.collection_name, self.query, self.body)
                    self.status_code = HTTP_CODES.SUCCESS if path else HTTP_CODES.NO_CONTENT
                except:
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        
class Basic_PATCH_Response (Basic_Response): # UPDATE ONLY WORKS WITH $ OPERATORS
    def __init__(
            self,
            collection_name:str,
            body: dict,
            query: dict,
            model: Any
    ):
        self.valid_model = isPatchableBy(model, body)
        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST
        self.content = b""

        if DB.collection_or_table_exists(collection_name):
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None
            self.query = query if self.valid_model else None
        
    def send(self, path: str = None, patch_many = False):
        if self.valid_model:
            doc = DB.get_from_db(self.collection_name, self.query)

            self.status_code = HTTP_CODES.SUCCESS if path else HTTP_CODES.NO_CONTENT
            self.content = bytes(path, "utf-8")

            if doc is not None:
                try:
                    DB.update_to_db(self.collection_name, self.query, self.body, patch_many)
                except Exception as e:
                    print(e.with_traceback())
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR


class Basic_DELETE_Response (Basic_Response):
    def __init__(
            self,
            collection_name: str,
            query: dict[str, Any]

    ):
        self.docs = DB.get_from_db(collection_name, query)
        self.collection_name = collection_name
        self.query = query
        self.status_code = HTTP_CODES.ACCEPTED
        self.content = b""

    def send (self, success_msg: bytes = b"", delete_many = False):
        
        if self.docs is not None:
            try:
                DB.delete_to_db(self.collection_name, self.query, delete_many)
                self.status_code = HTTP_CODES.SUCCESS if success_msg else HTTP_CODES.NO_CONTENT
                self.content = success_msg
            except:
                self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        else:
            self.status_code = HTTP_CODES.NOT_FOUND