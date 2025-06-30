from functools import wraps

from utils.utils_request import request_failed

MAX_CHAR_LENGTH = 255

class ErrorCode:
    NO_PERMISSION = {"code": 1020, "msg": "No permission"}
    USER_DOES_NOT_EXIST = {"code": 1021, "msg": "User does not exist"}
    PAGE_OUT_OF_RANGE = {"code": 1023, "msg": "Page out of range"}
    POST_DOES_NOT_EXIST = {"code": 1024, "msg": "Post does not exist"}
    INVALID_CONTENT_TYPE = {"code": 1031, "msg": "Invalid content type"}
    OBJECT_DOES_NOT_EXIST = {"code": 1032, "msg": "Object does not exist"}
    COMMENT_DOES_NOT_EXIST = {"code": 1035, "msg": "Comment does not exist"}
    REPORT_DOES_NOT_EXIST = {"code": 1036, "msg": "Report does not exist"}

def missing_param_msg(param):
    return f"Missing or error type of [{param}]"

# A decorator function for processing `require` in view function.
def check_require(check_fn):
    @wraps(check_fn)
    def decorated(*args, **kwargs):
        try:
            return check_fn(*args, **kwargs)
        except Exception as e:
            # Handle exception e
            error_code = -2 if len(e.args) < 2 else e.args[1]
            return request_failed(error_code, e.args[0], 400)  # Refer to below
    return decorated

def convert_type(val, type):
    if type == "int":
        val = int(val)
        return val
    elif type == "float":
        val = float(val)
        return val
    elif type == "string":
        val = str(val)
        return val
    elif type == "bool":
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            if val.lower() in ["true", "1"]:
                return True
            if val.lower() in ["false", "0"]:
                return False 
        assert(0)
    elif type == "list":
        assert isinstance(val, list)
        return val

# Here err_code == -2 denotes "Error in request body"
# And err_code == -1 denotes "Error in request URL parsing"
def require(body, key, type="string", err_msg=None, err_code=-2):
    
    if key not in body.keys():
        if err_msg is None:
            err_msg = f"Invalid parameters. Expected `{key}`, but not found."
        raise KeyError(err_msg, err_code)
    
    val = body[key]
    
    if err_msg is None:
        err_msg = missing_param_msg(key)

    if type not in ["int", "float", "string", "list", "bool"]:
        raise NotImplementedError(f"Type `{type}` not implemented.", err_code)
    
    try:
        return convert_type(val, type)
    except (ValueError, AssertionError):
        raise KeyError(err_msg, err_code)