from pathlib import Path
import unittest

def home (request_data: RequestData):
    handler = request_data.handler
    query = request_data.url_query
    url_variables = request_data.url_variables

    res = Basic_GET_Response("set")
    res.send_db(query)

    return res

class Server_Mongo_Test (unittest.TestCase):
    def server_initialized_correctly ():
        my_server = Server("localhost:8080", Path.cwd())
        DB_Mongo(
            "mongodb+srv://D4veloper:pypressdb0608@pypress.1btky.mongodb.net/?retryWrites=true&w=majority&appName=PyPress", 
            "PyPress"
        )

        my_server.GET("/", home)
        my_server.start()

unittest.main()