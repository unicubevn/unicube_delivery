# File extensions.py 
# Created at 25/03/2023
# Author Khanh

import json
import redis
import os
from dotenv import load_dotenv

load_dotenv()

pool = redis.ConnectionPool(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=10, password = 'viber@123')
redis_single = redis.Redis(connection_pool=pool)

def gen_auth_key(obj_type: str, payload: dict):
    if obj_type == 'user_account':
        print('--------payload-------', payload)
        return f'token:{obj_type}:{payload.get("phone")}'
