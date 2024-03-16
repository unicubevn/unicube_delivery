
from datetime import datetime, timezone

def get_current_time():
    return datetime.utcnow().replace(tzinfo=timezone.utc)

def make_response(data: dict = {},
                  msg: str = '',
                  error_code: str = '',
                  status: int = 1,
                  errors={}):
    result = {
        'data': data,
        'msg': msg,
        'error_code': error_code,
        'errors': errors,
        'status': status,
        'version': 'v1',
        'time': get_current_time().timestamp()
    }

    return result