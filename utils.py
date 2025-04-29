from typing import Any

def try_int (value: Any):
    result = None
    try:
        result = int(value)
    except:
        result = value
    
    return result