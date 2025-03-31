import pymongo
from pymongo import MongoClient

server_URI = "mongodb+srv://D4veloper:pypressdb0608@pypress.1btky.mongodb.net/?retryWrites=true&w=majority&appName=PyPress"

client = MongoClient(server_URI)

def get_collection(name: str):
    try:
        client.admin.command("ping")
        print("Pinged to the client, the connection was successful!")

        res = client["PyPress"].get_collection(name) if name else None

        return res
    except Exception as e:
        print(f"Couldn't connect to the database: {e}")