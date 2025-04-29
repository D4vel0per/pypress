from typing import Any

from pydantic import BaseModel

from constants import Mongo_Update_Operators

def class_to_dict (clss):
    annotations: dict = clss.__annotations__
    proto_dict: dict[str, Any] = clss.__dict__
    constants_dict: dict = {}

    for key, value in proto_dict.items():
        if not (key.startswith("__") and key.endswith("__")):
            constants_dict[key] = value

    cls_dict = {}
    print("Inside class_to_dict")
    print("Annotations: ", clss.__annotations__)
    

    for (key, value_cls) in annotations.items():
        print (key, value_cls)
        cls_dict[key] = value_cls

    cls_dict.update(constants_dict)
    
    return cls_dict

def get_base_path (actual_path: str, url_variables: dict[str, str]):
    base_path = actual_path + ""
    for key, value in url_variables.items():
        base_path = actual_path.replace(value, key)

    base_path = base_path.split("?")[0] # Just in case it has a query

    return base_path.removeprefix("/")

def checkModel (model: Any, data:dict|list[dict]):
    class PassModel (BaseModel, model):
        pass

    try:
        if type(data) is list:
            for obj in data:
                PassModel.model_validate(obj)
        elif type(data) is dict:
            PassModel.model_validate(data)
        else:
            return False
        
        return True
    except:
        return False
    
def isPatchableBy (model: Any, patch: dict[str, Any]):
    model_dict: dict = class_to_dict(model)
    eval_patch = {}

    for key, value in patch.items():
        if key in list(class_to_dict(Mongo_Update_Operators).values()):
            eval_patch.update(patch[key])
        else:
            eval_patch.update({ key: value })

    for key, value in eval_patch.items():
        key_in_model = key in model_dict
        is_type_eq = model_dict[key] is type(value) if key_in_model else False 
        if not key_in_model or not is_type_eq:
            return False
        
    return True