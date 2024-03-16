from functools import wraps
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from .exceptions import RequiredAuth
from .unicube_redis import redis_single

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

def gen_auth_key(obj_type: str, payload: dict):
    if obj_type == 'user_account':
        return f"token:user_account:{payload.get('phone')}"

def get_token_info(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return False

def verify_token_request(token):
    """
        - The func verify token
    """
    _info = get_token_info(token)

    if not isinstance(_info, dict):
        return None
    
    _token_existed = redis_single.get(gen_auth_key('user_account', _info))

    if _token_existed:
        _token_existed = _token_existed.decode()

    if _token_existed and _token_existed == token:
        return _info
    else: 
        return None

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    result = verify_token_request(token)
    print('-----result-----', result)
    return verify_token_request(token)
  
    

async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def gen_decorator(key: str, obj_type: str, is_required: bool = True):
    def decorator(f):
        print
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(f.__name__ + ' was called')
            
            # auth_info = verify_token_request(obj_type)
            # print('----auth info----', auth_info)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def auth_user():
    """
        - Decorator check and get user info form user token, Return
    """
    return gen_decorator(key='user', obj_type='user_account', is_required=False)
