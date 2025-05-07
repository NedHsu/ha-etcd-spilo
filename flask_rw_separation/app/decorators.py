from functools import wraps
from flask import current_app

def read_write_separation(read_only=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if read_only:
                # 使用從數據庫進行讀取操作（通過 HAProxy）
                session = current_app.slave_session()
            else:
                # 使用主數據庫進行寫入操作（通過 HAProxy）
                session = current_app.master_session()
            
            try:
                result = f(session, *args, **kwargs)
                return result
            finally:
                session.close()
        return wrapper
    return decorator 