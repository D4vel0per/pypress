from typing import Any
from pymongo.collection import Collection

from mongo_connection import get_collection


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