from typing import Any, Callable
from constants import QueryComparison, QueryLogical, QueryArray, QueryElement

def isInClass (clss: type|list[type], value):
    values = []
    if type(clss) is list:
        for cls_vals in clss:
            values.extend(cls_vals.__dict__.values())
    elif type(clss) is type:
        values = clss.__dict__.values()

    return value in values

isValidOperator: Callable[[str], bool] = lambda key: isInClass([
    QueryLogical,
    QueryComparison,
    QueryElement,
    QueryArray
], key)

class QueryManager ():
    class LOGICAL ():
        def CORE (self, operation: QueryLogical, data: dict[str, Any]|tuple[dict[str, Any]]):
            query: dict[str, Any] = {}
            if type(data) is tuple:
                #query[operation] = [
                    #{ key: value } for items in data for key, value in items.items()
                #]
                #query[operation] = []

                inside = []
                outside = {}

                for obj in data:
                    for key, value in obj.items():
                        print(key, value)
                        if isInClass(QueryLogical, key) or not isValidOperator(key):
                            inside.append({ key: value })
                        elif isValidOperator(key):
                            outside[key] = value

                query = outside
                if len(inside):
                    query[operation] = inside
                
            elif type(data) is dict[str, Any]:
                query[operation] = data
            
            return query

        def OR (self, *data: dict[str, Any]):
            return self.CORE(QueryLogical.OR, data)
            
        def AND (self, *data: dict[str, Any]): 
            
            return self.CORE(QueryLogical.AND, data)
        
        def NOR (self, *data: dict[str, Any]):
            return self.CORE(QueryLogical.NOR, data)
        
        def NOT (self, data: dict[str, Any]):
            if len(data.items()) > 1:
                return self.NOR(data) 
            elif len(data.items()):
                key: str = list(data.keys())[0]
                value: Any = list(data.values())[0]

                data = {
                    key: value if isValidOperator(key) else QueryManager.COMPARE.EQUAL(value)
                }

            return self.CORE(QueryLogical.NOT, data)

    class COMPARE ():
        def CORE (self, operation: QueryComparison, val: Any, key: str = None):
            query = {
                (key or operation): { operation: val } if key else val
            }
            return query
            
        def EQUAL (self, val: Any, key: str = None):
            return self.CORE(QueryComparison.EQUAL, val, key)
        
        def GREATER_THAN (self, val: Any, key: str = None): 
            return self.CORE(QueryComparison.GREATER_THAN, val, key)
        
        def GREATER_THAN_OR_EQUAL (self, val: Any, key: str = None): 
            return self.CORE(QueryComparison.GREATER_THAN_OR_EQUAL, val, key)
        
        def LOWER_THAN (self, val: Any, key: str = None): 
            return self.CORE(QueryComparison.LOWER_THAN, val, key)
        
        def LOWER_THAN_OR_EQUAL (self, val: Any, key: str = None): 
            return self.CORE(QueryComparison.LOWER_THAN_OR_EQUAL, val, key)
        
        def NOT_EQUAL (self, val: Any, key: str = None): 
            return self.CORE(QueryComparison.NOT_EQUAL, val, key)
        
        def IN (self, val: list[Any], key: str = None):
            return self.CORE(QueryComparison.IN, val, key)
        
        def NOT_IN (self, val: list[Any], key: str = None):
            return self.CORE(QueryComparison.NOT_IN, val, key)

    class ELEMENT:
        def CORE (self, operation: QueryElement, val: Any, key: str = None):
            query = {
                (key or operation): { operation: val } if key else val
            }
            return query
        
        def EXISTS (self, val: bool, key: str = None): 
            return self.CORE(QueryElement.EXISTS, val, key)
        def TYPE (self, val: str, key: str = None):
            return self.CORE(QueryElement.EXISTS, val, key)

    class ARRAY:
        def CORE (self, operation: QueryArray, val: Any, key: str = None):
            query = {
                (key or operation): { operation: val } if key else val
            }
            return query
        def ALL (self, val: list[Any], key: str = None): 
            return self.CORE(QueryArray.ALL, val, key)
        def ELEMENT_MATCH (self, obj: dict[str, Any], field: str = None):
            for key in obj.keys():
                if not isValidOperator(key):
                    obj.pop(key)
            return self.CORE(QueryArray.ALL, obj, field)
        def SIZE (self, val: int, key: str = None):
            return self.CORE(QueryArray.SIZE, val, key)
    
    LOGICAL = LOGICAL()
    COMPARE = COMPARE()
    ELEMENT = ELEMENT()
    ARRAY = ARRAY()

Q_LGL = QueryManager.LOGICAL
Q_CMP = QueryManager.COMPARE
Q_ELM = QueryManager.ELEMENT
Q_ARR = QueryManager.ARRAY