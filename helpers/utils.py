import json
from types import SimpleNamespace


def json_to_object(jsonStr: str):
    ''' Convert JSON string into object so that its elements can be easily accessed
    '''
    return json.loads(jsonStr, object_hook=lambda d: SimpleNamespace(**d))