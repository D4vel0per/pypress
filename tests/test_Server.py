from pathlib import Path
import unittest
from src import Server

from src.mongo import DB_Mongo
from src.RequestHandler import RequestData
from src.ResponseManagers import Basic_GET_Response

class Server_Mongo_Test (unittest.TestCase):
    def test_server_initialized_correctly (self):
        my_server = Server("localhost:8080", Path.cwd())
        DB_Mongo(
            "mongodb+srv://D4veloper:pypressdb0608@pypress.1btky.mongodb.net/?retryWrites=true&w=majority&appName=PyPress", 
            "PyPress"
        )

        def home (request_data: RequestData):
            query = {
                "name": "Omar"
            }

            res = Basic_GET_Response("tests/xd.txt")
            res.send_file()

            return res

        my_server.GET("/", home)
        my_server.start()

if __name__ == "__main__":
    unittest.main()