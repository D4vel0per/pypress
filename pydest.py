from pydantic import BaseModel

class Person:
    name: str
    age: int
    desc: str

class Model (BaseModel, Person):
    pass

stuff = {
    "name": "sdkahsdkj",
    "age": 8,
    "desc": "BRUHSAKJSH"
}

test = Model()

print(test.model_dump())