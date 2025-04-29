from pymongo import MongoClient

server_URI = "mongodb+srv://D4veloper:pypressdb0608@pypress.1btky.mongodb.net/?retryWrites=true&w=majority&appName=PyPress"

client = MongoClient(server_URI)

print(client.admin.command("ping"))
print("Pinged to the client, the connection was successful!")

def get_collection(name: str):
    res = client["PyPress"].get_collection(name) if name else None
    print("Collection", res)
    return res
    