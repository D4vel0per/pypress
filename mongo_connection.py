from pymongo import MongoClient

server_URI = "mongodb+srv://D4veloper:pypressdb0608@pypress.1btky.mongodb.net/?retryWrites=true&w=majority&appName=PyPress"

client = MongoClient(server_URI)

client.admin.command("ping")
print("Pinged to the client, the connection was successful!")

def get_collection(name: str):
    res = client["PyPress"].get_collection(name) if name else None
    print("Collection", res) #Still throws 500, solve tomorrow 11/04/25 -> 12/04/25
    return res
    