import re
from types import NoneType
from typing import Any, Callable

from pymongo import MongoClient
from pymongo.database import Collection, Database

from sqlite3 import Connection, Cursor
from .constants import DB_METHODS

class DB ():
    uri: str
    is_available: bool
    connection: MongoClient | Connection
    db: Database | Cursor
    """Connection types available in PyPress, MongoClient for Mongodb and Connection for SQLite (not released yet)"""

    def __init__(self, uri: str, is_available: bool, connection: MongoClient | Connection, db: Database | Cursor):
        DB.uri = uri
        DB.is_available = is_available
        DB.connection = connection
        DB.db = db

    @classmethod
    def get_collection_or_table(
        self,
        collection_name:str
    ) -> Collection|Any|None: 
        """Collection for Mongodb, Any for sqlite3 (not implemented) and None for not found cases"""

    @classmethod
    def collection_or_table_exists(
        self,
        collection_name:str
    ) -> bool: 
        """Returns True if the Mongodb Collection or the SQLite3 table exists, otherwise, returns False"""

    @classmethod
    def insert_to_db(
            self, 
            collection_name:str, 
            data: dict|list[dict]
    ) -> NoneType: pass
    
    @classmethod
    def replace_to_db(
            self, 
            collection_name:str, 
            query:dict[str, Any], data: dict[str, Any]|list
    ) -> NoneType: pass

    @classmethod
    def update_to_db(
            self, 
            collection_name:str, 
            query:dict[str, Any], 
            data: dict[str, Any], 
            update_many: bool = False
    ) -> NoneType: pass

    @classmethod
    def delete_to_db(
            self, 
            collection_name:str, 
            query:dict[str, Any], 
            delete_many: bool = False
    ) -> NoneType: pass

    @classmethod
    def get_from_db(
            self, 
            collection_name:str, 
            query: dict[str, Any]={}
    ) -> list[dict[str, Any]] | NoneType: pass

def get_method (method: Callable):
    print("Annotations are equal: ", method.__annotations__, DB.get_from_db.__annotations__)
    def wrapper (
        self: DB,
        collection_name: str,
        query: dict[str, Any] = {}
    ):
         if type(method) is type(DB.get_from_db):
            DB.get_from_db = classmethod(self.get_from_db)
            return DB.get_from_db(collection_name, query)
         
    return wrapper

def insert_method (method: Callable):
    print("Annotations are equal: ", method.__annotations__, DB.insert_to_db.__annotations__)
    def wrapper (
        self: DB,
        collection_name: str,
        data: dict | list[dict]
    ):
         if type(method) is type(DB.insert_to_db):
            DB.insert_to_db = classmethod(self.insert_to_db)
            return DB.insert_to_db(collection_name, data)
         
    return wrapper

def replace_method (method: Callable):
    print("Annotations are equal: ", method.__annotations__, DB.replace_to_db.__annotations__)
    def wrapper (
        self: DB,
        collection_name: str,
        query: dict[str, Any],
        data: dict[str, Any] | list
    ):
         if type(method) is type(DB.replace_to_db):
            DB.replace_to_db = classmethod(self.replace_to_db)
            return DB.replace_to_db(collection_name, query, data)
         
    return wrapper
    
def update_method (method: Callable):
    print("Annotations are equal: ", method.__annotations__, DB.update_to_db.__annotations__)
    def wrapper (
        self: DB, 
        collection_name: str,
        query: dict[str, Any],
        data: dict[str, Any],
        update_many: bool = False
    ):
        if type(method) is type(DB.update_to_db):
            DB.update_to_db = classmethod(self.update_to_db)
            return DB.update_to_db(collection_name, query, data, update_many)
         
    return wrapper

def delete_method (method: Callable):
    print("Annotations are equal: ", classmethod(method).__dict__, DB.delete_to_db.__annotations__)
    def wrapper (
        self: DB,
        collection_name: str,
        query: dict[str, Any],
        delete_many: bool = False
    ):
        if type(method) is type(DB.delete_to_db):
            DB.delete_to_db = classmethod(self.delete_to_db)
            return DB.delete_to_db(collection_name, query, delete_many)
         
    return wrapper
'''
def validate_method (original: Callable, new): # Solve this later
    print("Validate: ", original.__annotations__, new.__dir__())
    if original.__annotations__ == new.__annotations__:
        return classmethod(new)
    return original

def PressDB (cls: DB):
    DB.delete_to_db = validate_method(DB.delete_to_db, cls.delete_to_db)
    DB.insert_to_db = validate_method(DB.insert_to_db, cls.insert_to_db)
    DB.get_from_db = validate_method(DB.get_from_db, cls.get_from_db)
    DB.update_to_db = validate_method(DB.update_to_db, cls.update_to_db)
    DB.replace_to_db = validate_method(DB.replace_to_db, cls.replace_to_db)
    return cls
'''
def PressDB (cls):
    DB.delete_to_db = classmethod(cls.delete_to_db)
    DB.insert_to_db = classmethod(cls.insert_to_db)
    DB.get_from_db = classmethod(cls.get_from_db)
    DB.update_to_db = classmethod(cls.update_to_db)
    DB.replace_to_db = classmethod(cls.replace_to_db)
    return cls