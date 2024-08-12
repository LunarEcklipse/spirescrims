import sqlean, pytz, asyncio, sys, threading
from typing import List, Tuple, Union
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from contextlib import closing

sqlean.extensions.enable_all()

sqlite_db_path: str = "../rsc/spire_scrims.db"
db_lock = threading.Lock()

class BoolConvert:
    @staticmethod
    def convert_int_to_bool(value: int) -> bool:
        if value not in [0, 1]:
            raise ValueError("Value must be either 0 or 1.")
        return False if value == 0 else True
    
    @staticmethod
    def convert_bool_to_int(value: bool) -> int:
        return 1 if value else 0

if __name__ == "__main__":
    print("This does not run on its own.")
    sys.exit()

def connect_to_db() -> sqlean.Connection:
    '''Connects to the database.'''
    return sqlean.connect(sqlite_db_path)

class DatetimeConvert:
    @staticmethod
    def convert_datetime_to_str(value: datetime) -> str:
        return value.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def convert_str_to_datetime(value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)

# Decorator wrapper
def database_transaction(func): # This is a decorator that wraps a function in a database transaction.
    def wrapper(*args, **kwargs):
        with db_lock:
            with closing(connect_to_db()) as conn:
                with closing(conn.cursor()) as cur:
                    conn.begin()
                    try:
                        result = func(cur, *args, **kwargs)
                        conn.commit()
                        return result
                    except Exception as e:
                        conn.rollback()
                        raise e
    return wrapper

@database_transaction
def init_scrim_db(cur: sqlean.Connection.cursor) -> None:
    '''Initializes the database.'''
    cur.execute("CREATE TABLE IF NOT EXISTS api_data (auth_token TEXT, auth_expiration TEXT);")

class DeceiveAPIData:
    
    @staticmethod
    def is_token_expired(expiration: Union[datetime, None]) -> bool:
        '''Determines if the token is expired based on the database timestamp.'''
        if expiration is None:
            return True
        return expiration <= datetime.now(timezone.utc)

    @staticmethod
    @database_transaction
    def get_auth_token(cur) -> Union[Tuple[str, datetime], None]:
        '''Gets the auth token from the database, if one exists.'''
        cur.execute("SELECT * FROM api_data;")
        result = cur.fetchone()
        if result is None:
            return None
        return (result[0], DatetimeConvert.convert_str_to_datetime(result[1]))
    
    @staticmethod
    @database_transaction
    def set_auth_token(cur, token: str, expiration: datetime) -> None:
        '''Sets the auth token in the database.'''
        cur.execute("DELETE FROM api_data;")
        cur.execute("INSERT INTO api_data (auth_token, auth_expiration) VALUES (?, ?);", (token, DatetimeConvert.convert_datetime_to_str(expiration)))