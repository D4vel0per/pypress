from ipaddress import IPv4Address
from bson import ObjectId
from base64 import b64encode, b64decode

obj = ObjectId()
encode = b64encode(obj.binary)
decode = b64decode(bytes(encode.decode(), "utf-8"))

class Home ():
    lights: str
    def turn_on (mode: str) -> None: pass