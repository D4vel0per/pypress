from typing import Any
from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database, Collection
from .base import DB, PressDB
from .mongo_utils import doc_b64_to_obj_id, doc_id_to_b64

@PressDB
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

            DB(self.uri, self.is_available, self.connection, self.db)
            DB.collection_or_table_exists = self.collection_or_table_exists
            DB.get_collection_or_table = self.get_collection_or_table

    @classmethod
    def get_collection_or_table(self, collection_name):
        res = self.db.get_collection(collection_name) if collection_name else None
        return res
    
    @classmethod
    def collection_or_table_exists(self, collection_name):
        return self.db.get_collection(collection_name) is not None
    
    def insert_to_db(self, collection_name, data):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        if type(data) is list:
            data = doc_b64_to_obj_id(data)
                
            collection.insert_many(data)
        elif type(data) is dict:
            data = doc_b64_to_obj_id(data)
            collection.insert_one(data)

    def replace_to_db(self, collection_name, query, data):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        if type(data) is list:
            data = doc_b64_to_obj_id(data)
            query = doc_b64_to_obj_id(query)
            
            collection.delete_many(query)
            collection.insert_many(data)
        elif type(data) is dict:
            collection.replace_one(query, data)
    
    def update_to_db(self, collection_name, query, data, update_many = False):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        data = doc_b64_to_obj_id(data)
        query = doc_b64_to_obj_id(query)
        print(data, query)

        if update_many:
            collection.update_many(query, data)
        else:
            collection.update_one(query, data)
    
    def delete_to_db(self, collection_name, query, delete_many = False):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        query = doc_b64_to_obj_id(query)

        if delete_many:
            collection.delete_many(query)
        else:
            collection.delete_one(query)

    def get_from_db(self, collection_name, query):
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        cursor: list[dict[str, Any]] = collection.find(query).to_list()
        docs: list[dict[str, Any]] = doc_id_to_b64(cursor)

        print("docs:", docs)
        return docs if len(docs) else None