# File extensions.py 
# Created at 25/03/2023
# Author Khanh

import redis
from app.odoo import tools

# load_dotenv()

# pool = redis.ConnectionPool(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=10, password = 'viber@123')
pool = redis.ConnectionPool(host=tools.config.get("redis_host"), port=tools.config.get("redis_port"),
                            db=tools.config.get("redis_dbindex"), password=tools.config.get("redis_pass"))
redis_single = redis.Redis(connection_pool=pool)

def gen_auth_key(obj_type: str, payload: dict):
    if obj_type == 'user_account':
        print('--------payload-------', payload)
        return f'token:{obj_type}:{payload.get("phone")}'
