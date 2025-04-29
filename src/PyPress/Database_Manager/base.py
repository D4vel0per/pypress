from types import NoneType
from typing import Any, Callable

from pymongo import MongoClient
from pymongo.database import Collection, Database

from sqlite3 import Connection, Cursor

class DB ():
    uri: str
    is_available: bool
    connection: MongoClient | Connection
    db: Database | Cursor
    """Connection types available in PyPress, MongoClient for Mongodb and Connection for SQLite (not released yet)"""

    def get_collection_or_table(
        self,
        collection_name:str
    ) -> Collection|Any|None: 
        """Collection for Mongodb, Any for sqlite3 (not implemented) and None for not found cases"""

    def collection_or_table_exists(
        self,
        collection_name:str
    ) -> bool: 
        """Returns True if the Mongodb Collection or the SQLite3 table exists, otherwise, returns False"""

    def insert_to_db(
            self, 
            collection_name:str, 
            data: dict|list[dict]
    ) -> NoneType: pass
    
    def replace_to_db(
            self, 
            collection_name:str, 
            query:dict[str, Any], data: dict[str, Any]|list
    ) -> NoneType: pass

    def update_to_db(
            self, 
            collection_name:str, 
            query:dict[str, Any], 
            data: dict[str, Any], 
            update_many: bool = False
    ) -> NoneType: pass

    def delete_to_db(
            self, 
            collection_name:str, 
            query:dict[str, Any], 
            delete_many: bool = False
    ) -> NoneType: pass

    def get_from_db(
            self, 
            collection_name:str, 
            query: dict[str, Any]={}
    ) -> list[dict[str, Any]] | NoneType: pass

def _set_method (base_method: Callable, other_method):
    def wrapper (self: DB, *args, **kwargs):
        match(base_method):
            case DB.get_from_db:
                if type(other_method) is type(DB.get_from_db):
                    DB.get_from_db = other_method
                    return DB.get_from_db(self, *args, **kwargs)
                
            case DB.insert_to_db:
                if type(other_method) is type(DB.insert_to_db):
                    DB.insert_to_db = other_method
                    return DB.insert_to_db(self, *args, **kwargs)
                
            case DB.replace_to_db:
                if type(other_method) is type(DB.replace_to_db):
                    DB.replace_to_db = other_method
                    return DB.replace_to_db(self, *args, **kwargs)
                
            case DB.update_to_db:
                if type(other_method) is type(DB.update_to_db):
                    DB.update_to_db = other_method
                    return DB.update_to_db(self, *args, **kwargs)
                
            case DB.delete_to_db:
                if type(other_method) is type(DB.delete_to_db):
                    DB.delete_to_db = other_method
                    return DB.delete_to_db(self, *args, **kwargs)
            case _:
                safe_to_set_vars = False

        if safe_to_set_vars:
            DB.uri = self.uri
            DB.is_available = self.is_available
                
    return wrapper

def get_method (method: Callable):
        return _set_method(DB.get_from_db, method)

def insert_method (method: Callable):
        return _set_method(DB.insert_to_db, method)

def replace_method (method: Callable):
        return _set_method(DB.replace_to_db, method)
    
def update_method (method: Callable):
        return _set_method(DB.update_to_db, method)

def delete_method (method: Callable):
    return _set_method(DB.delete_to_db, method)