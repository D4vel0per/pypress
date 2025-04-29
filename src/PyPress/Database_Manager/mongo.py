from typing import Any
from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database, Collection
from base64 import b64encode, b64decode
from .base import DB, insert_method, replace_method, get_method, delete_method, update_method

class DB_Mongo (DB):
    uri: str
    connection: MongoClient
    db: Database
    is_available: bool = False

    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        client = MongoClient(uri)

        client.admin.command("ping")
        self.connection = client
        if db_name in client.list_database_names():
            self.db = client.get_database(db_name)
            self.is_available = True

    def get_collection_or_table(self, collection_name):
        res = self.db.get_collection(collection_name) if collection_name else None
        return res

    def _doc_id_to_b64(self, doc: dict|list[dict]):
        result = { **doc }
        if type(doc) is list:
            results = [ self._doc_id_to_b64(document) for document in doc ]
            return results

        if "_id" in doc:
            if type(doc["_id"]) is ObjectId:
                result["_id"] = b64encode(doc["_id"].binary).decode()
            elif type(doc["_id"]) is str:
                result["_id"] = b64encode(bytes(doc["_id"], "utf-8")).decode()

        return result
    
    def _doc_b64_to_obj_id(self, doc: dict|list[dict]):
        result = { **doc }
        if type(doc) is list:
            results = [ self._doc_b64_to_obj_id(document) for document in doc ]
            return results
        
        if "_id" in doc:
            if type(doc["_id"]) is str:
                result["_id"] = ObjectId(b64decode(bytes(doc["_id"], "utf-8")))

        return result
    
    @insert_method
    def insert_to_db(self, collection_name, data):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        if type(data) is list:
            data = self._doc_b64_to_obj_id(data)
                
            collection.insert_many(data)
        elif type(data) is dict:
            data = self._doc_b64_to_obj_id(data)
            collection.insert_one(data)

    @replace_method
    def replace_to_db(self, collection_name, query, data):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        if type(data) is list:
            data = self._doc_b64_to_obj_id(data)
            query = self._doc_b64_to_obj_id(query)
            
            collection.delete_many(query)
            collection.insert_many(data)
        elif type(data) is dict:
            collection.replace_one(query, data)
    
    @update_method
    def update_to_db(self, collection_name, query, data, update_many = False):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        print(collection_name)
        data = self._doc_b64_to_obj_id(data)
        query = self._doc_b64_to_obj_id(query)

        if update_many:
            collection.update_many(query, data)
        else:
            collection.update_one(query, data)
    
    @delete_method
    def delete_to_db(self, collection_name, query, delete_many = False):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        query = self._doc_b64_to_obj_id(query)

        if delete_many:
            collection.delete_many(query)
        else:
            collection.delete_one(query)

    @get_method
    def get_from_db(self, collection_name, query):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        cursor: list[dict[str, Any]] = collection.find(query).to_list()
        docs: list[dict[str, Any]] = self._doc_id_to_b64(cursor)

        print("docs:", docs)
        return docs if len(docs) else None