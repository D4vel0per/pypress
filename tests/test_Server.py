import json
from pathlib import Path
import unittest

from src.PyPress import (
    RequestData, 
    Basic_DELETE_Response, 
    Basic_GET_Response, 
    Basic_PATCH_Response, 
    Basic_POST_Response, 
    Basic_PUT_Response,
    DB_Mongo,
    Server
)

class Server_Mongo_Test (unittest.TestCase):
    def test_server_initialized_correctly (self):
        my_server = Server("localhost:8080", Path.cwd())
        DB_Mongo(
            "mongodb+srv://D4veloper:pypressdb0608@pypress.1btky.mongodb.net/?retryWrites=true&w=majority&appName=PyPress", 
            "PyPress"
        )

        class Person:
            name: str
            age: int
            description: str

        def home (request_data: RequestData):
            query = {
                "name": "UMAMI"
            }

            print(json.loads(request_data.body))

            data = json.loads(request_data.body)

            body = {
                "$set": data
            }

            res = Basic_DELETE_Response("set", data)
            '''
            content = ("""
                    <html>
                        <body>
                            <h1>POSTED:</h1>
                            <h2>{name}, {age}</h2>
                            <p>{description}</p>
                        </body>
                    </html>
                """
                .format(**data).strip())
            '''
            
            res.send(b"Deleted succesfully", True)

            return res

        #my_server.GET("/", home)
        my_server.DELETE("/", home)
        my_server.start()
    
if __name__ == "__main__":
    unittest.main()