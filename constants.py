from typing import Callable


class HTTP_CODES:
    REDIRECT = 303
    SUCCESS = 200
    CREATED = 201
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400
    NO_CONTENT = 204
    ACCEPTED = 202

class GET_mode:
    FILE = "FILE"
    DATABASE = "DB"

class QueryLogical:
    OR = "$or"
    AND = "$and"
    NOT = "$not"
    NOR = "$nor"

class QueryComparison:
    EQUAL = "$eq"
    GREATER_THAN = "$gt"
    GREATER_THAN_OR_EQUAL = "$gte"
    IN = "$in"
    LOWER_THAN = "$lt"
    LOWER_THAN_OR_EQUAL = "$lte"
    NOT_EQUAL = "$ne"
    NOT_IN = "$nin"

class QueryElement:
    EXISTS = "$exists"
    TYPE = "$type"

class QueryArray:
    ALL = "$all"
    ELEMENT_MATCH = "$elemMatch"
    SIZE = "$size"

class Mongo_Update_Operators:
    CURRENT_DATE = "$currentDate"
    INC = "$inc"
    MIN = "$min"
    MAX = "$max"
    MUL = "$mul"
    RENAME = "$rename"
    SET = "$set"
    SET_ON_INSERT = "$setOnInsert"
    UNSET = "$unset"
