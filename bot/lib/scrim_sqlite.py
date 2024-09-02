import sqlean, pytz, asyncio, sys, threading, os, discord, uuid
from typing import List, Tuple, Union
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from contextlib import closing
from lib.DI_API_Obj.sweet_user import SweetUserPartial, SweetUser
from lib.scrim_logging import scrim_logger
from lib.obj.scrim_user import ScrimUser

sqlean.extensions.enable_all()

absPath = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname = os.path.dirname(absPath)
os.chdir(dname)
load_dotenv()

sqlite_db_path: str = "../rsc/spire_scrims.db"
sweet_user_cache_expiration_seconds: int = 3600 # 1 hour
db_lock = threading.Lock()

class UUIDGenerator:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid.uuid4())

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
    # sys.exit()

def connect_to_db() -> sqlean.Connection:
    '''Connects to the database.'''
    return sqlean.connect(sqlite_db_path)

class DatetimeConvert:
    @staticmethod
    def convert_datetime_to_str(value: datetime) -> str:
        return value.astimezone(pytz.utc).isoformat()
    
    @staticmethod
    def convert_str_to_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value).replace(tzinfo=pytz.utc)

# Decorator wrapper
def database_transaction(func): # This is a decorator that wraps a function in a database transaction.
    def wrapper(*args, **kwargs):
        with db_lock:
            with closing(connect_to_db()) as conn:
                with closing(conn.cursor()) as cur:
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
    cur.execute("CREATE TABLE IF NOT EXISTS user_master (internal_user_id TEXT PRIMARY KEY NOT NULL, discord_id INTEGER, sweet_id TEXT, twitch_id TEXT);")
    cur.execute("CREATE TABLE IF NOT EXISTS api_data (auth_token TEXT, auth_expiration TEXT);")
    cur.execute("CREATE TABLE IF NOT EXISTS ocr_reader_channels (guild_id INTEGER, channel_id INTEGER, PRIMARY KEY(guild_id, channel_id));")
    cur.execute("CREATE TABLE IF NOT EXISTS sweet_user_partial_cache (sweet_id TEXT PRIMARY KEY NOT NULL, display_name TEXT, last_updated TEXT);")
    cur.execute("CREATE TABLE IF NOT EXISTS sweet_user_cache (sweet_id TEXT PRIMARY KEY NOT NULL, json_data TEXT, last_updated TEXT, FOREIGN KEY(sweet_id) REFERENCES sweet_user_partial_cache(sweet_id));")
    cur.execute("CREATE TABLE IF NOT EXISTS sweet_user_discord_links (discord_id INTEGER NOT NULL, sweet_id TEXT NOT NULL, PRIMARY KEY (discord_id, sweet_id), FOREIGN KEY(sweet_id) REFERENCES sweet_user_partial_cache(sweet_id));")
    cur.execute("CREATE TABLE IF NOT EXISTS duo_teams (duo_id TEXT PRIMARY KEY NOT NULL, duo_name TEXT, team_member_id_1 TEXT NOT NULL, team_member_id_2 TEXT NOT NULL, FOREIGN KEY (team_member_id_1) REFERENCES user_master(internal_user_id), FOREIGN KEY (team_member_id_2) REFERENCES user_master(internal_user_id));")

init_scrim_db()

### USERS ###

class ScrimUserData:
    @staticmethod
    @database_transaction
    def insert_user_from_discord(cur, discord_user: Union[discord.Member, discord.User, int]) -> None:
        '''Inserts a user into the database from a Discord object if they do not exist.'''
        if isinstance(discord_user, discord.Member) or isinstance(discord_user, discord.User):
            discord_user = discord_user.id
        cur.execute("SELECT * FROM user_master WHERE discord_id = ?;", (discord_user,))
        result = cur.fetchone()
        if result is not None:
            return
        scrim_logger.debug(f"Inserting user with Discord ID: \"{discord_user}\" into the database.")
        cur.execute("INSERT INTO user_master (internal_user_id, discord_id) VALUES (?, ?);", (UUIDGenerator.generate_uuid(), discord_user))
    
    @staticmethod
    @database_transaction
    def get_user_by_discord_id(cur, discord_user: Union[discord.Member, discord.User, int]) -> Union[ScrimUser, None]:
        '''Gets a user from the database by Discord ID.'''
        if isinstance(discord_user, discord.Member) or isinstance(discord_user, discord.User):
            discord_user = discord_user.id
        cur.execute("SELECT * FROM user_master WHERE discord_id = ?;", (discord_user,))
        result = cur.fetchone()
        if result is None:
            return None
        return ScrimUser(result[0], result[1], result[2], result[3])
    
    @staticmethod
    @database_transaction
    def get_user_by_sweet_id(cur, sweet_id: str) -> Union[ScrimUser, None]:
        '''Gets a user from the database by Sweet ID.'''
        cur.execute("SELECT * FROM user_master WHERE sweet_id = ?;", (sweet_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return ScrimUser(result[0], result[1], result[2], result[3])
    
    @staticmethod
    @database_transaction
    def get_user_by_twitch_id(cur, twitch_id: str) -> Union[ScrimUser, None]:
        '''Gets a user from the database by Twitch ID.'''
        cur.execute("SELECT * FROM user_master WHERE twitch_id = ?;", (twitch_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return ScrimUser(result[0], result[1], result[2], result[3])
    
    @staticmethod
    @database_transaction
    def get_user_by_id(cur, internal_id: str) -> Union[ScrimUser, None]:
        '''Gets a user from the database by internal ID.'''
        cur.execute("SELECT * FROM user_master WHERE internal_user_id = ?;", (internal_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return ScrimUser(result[0], result[1], result[2], result[3])
    
    def connect_discord_to_id(cur, internal_id: str, discord_user: Union[discord.Member, discord.User, int]) -> None:
        '''Connects a Discord ID to an internal ID.'''
        if isinstance(discord_user, discord.Member) or isinstance(discord_user, discord.User):
            discord_user = discord_user.id
        cur.execute("UPDATE user_master SET discord_id = ? WHERE internal_user_id = ?;", (discord_user, internal_id))

    def connect_sweet_to_id(cur, internal_id: str, sweet_id: str) -> None:
        '''Connects a Sweet ID to an internal ID.'''
        cur.execute("UPDATE user_master SET sweet_id = ? WHERE internal_user_id = ?;", (sweet_id, internal_id))
    
    def connect_twitch_to_id(cur, internal_id: str, twitch_id: str) -> None:
        '''Connects a Twitch ID to an internal ID.'''
        cur.execute("UPDATE user_master SET twitch_id = ? WHERE internal_user_id = ?;", (twitch_id, internal_id))

    



### DECEIVE API ###

class DeceiveAPIAuthData:
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

class SweetUserCache:
    @staticmethod
    @database_transaction
    def get_user(cur, sweet_id: str) -> Union[SweetUser, None]:
        '''Gets a user from the cache.'''
        cur.execute("SELECT * FROM sweet_user_cache WHERE sweet_id = ?;", (sweet_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return SweetUser.from_json(result[1])

    @staticmethod
    @database_transaction
    def set_user(cur, user: SweetUser) -> None:
        '''Sets a user in the cache.'''
        cur.execute("DELETE FROM sweet_user_cache WHERE sweet_id = ?;", (user.sweet_id,))
        cur.execute("INSERT INTO sweet_user_cache (sweet_id, json_data, last_updated) VALUES (?, ?, ?);", (user.sweet_id, user.dump_json(), DatetimeConvert.convert_datetime_to_str(datetime.now(timezone.utc))))

    @staticmethod
    @database_transaction
    def get_user_last_updated(cur, sweet_id: str) -> Union[datetime, None]:
        '''Gets the last updated timestamp for a user.'''
        cur.execute("SELECT last_updated FROM sweet_user_cache WHERE sweet_id = ?;", (sweet_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return DatetimeConvert.convert_str_to_datetime(result[0])

    @staticmethod
    @database_transaction
    def has_user_cache_expired(cur, sweet_id: str) -> bool:
        '''Determines if the user cache has expired.'''
        last_updated = SweetUserCache.get_user_last_updated(cur, sweet_id)
        if last_updated is None:
            return True
        return last_updated + timedelta(seconds=sweet_user_cache_expiration_seconds) <= datetime.now(timezone.utc)

    @staticmethod
    @database_transaction
    def get_user_partial_by_id(cur, sweet_id: str) -> Union[SweetUserPartial, None]:
        '''Gets a user partial from the cache.'''
        cur.execute("SELECT * FROM sweet_user_partial_cache WHERE sweet_id = ?;", (sweet_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return SweetUserPartial(result[0], result[1], DatetimeConvert.convert_str_to_datetime(result[2]))

    def get_user_partial_by_name(cur, name: str) -> Union[List[SweetUserPartial], None]:
        '''Gets a user partial from the cache by name. As names are not unique, returns a list instead.'''
        cur.execute("SELECT * FROM sweet_user_partial_cache WHERE display_name = ?;", (name,))
        results = cur.fetchall()
        if results is None:
            return None
        return [SweetUserPartial(result[0], result[1], DatetimeConvert.convert_str_to_datetime(result[2])) for result in results]

    @staticmethod
    @database_transaction
    def get_user_partial_last_updated(cur, sweet_id: str) -> Union[datetime, None]:
        '''Gets the last updated timestamp for a user partial.'''
        cur.execute("SELECT last_updated FROM sweet_user_partial_cache WHERE sweet_id = ?;", (sweet_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return DatetimeConvert.convert_str_to_datetime(result[0])

    @staticmethod
    @database_transaction
    def set_user_partial(cur, user: SweetUserPartial) -> None:
        '''Sets a user partial in the cache.'''
        cur.execute("DELETE FROM sweet_user_partial_cache WHERE sweet_id = ?;", (user.sweet_id,))
        cur.execute("INSERT INTO sweet_user_partial_cache (sweet_id, display_name, last_updated) VALUES (?, ?, ?);", (user.sweet_id, user.display_name, DatetimeConvert.convert_datetime_to_str(datetime.now(timezone.utc))))

    @staticmethod
    @database_transaction
    def has_user_partial_cache_expired(cur, sweet_id: str) -> bool:
        '''Determines if the user partial cache has expired.'''
        last_updated = SweetUserCache.get_user_partial_last_updated(cur, sweet_id)
        if last_updated is None:
            return True
        return last_updated + timedelta(seconds=sweet_user_cache_expiration_seconds) <= datetime.now(timezone.utc)

class DiscordAccountLinks:
    @staticmethod
    @database_transaction
    def get_sweet_id_from_discord_id(cur, discord_id: Union[discord.Member, discord.User, int]) -> Union[str, None]:
        '''Gets the Sweet ID linked to a Discord ID.'''
        if isinstance(discord_id, discord.Member) or isinstance(discord_id, discord.User):
            discord_id = discord_id.id
        cur.execute("SELECT sweet_id FROM sweet_user_discord_links WHERE discord_id = ?;", (discord_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return result[0]
    
    @staticmethod
    @database_transaction
    def get_discord_id_from_sweet_id(cur, sweet_id: str) -> Union[int, None]:
        '''Gets the Discord ID linked to a Sweet ID.'''
        cur.execute("SELECT discord_id FROM sweet_user_discord_links WHERE sweet_id = ?;", (sweet_id,))
        result = cur.fetchone()
        if result is None:
            return None
        return result[0]

    @staticmethod
    @database_transaction
    def link_discord_id_to_sweet_id(cur, discord_id: Union[discord.Member, discord.User, int], sweet_id: str) -> None:
        '''Links a Discord ID to a Sweet ID.'''
        if isinstance(discord_id, discord.Member) or isinstance(discord_id, discord.User):
            discord_id = discord_id.id
        cur.execute("INSERT INTO sweet_user_discord_links (discord_id, sweet_id) VALUES (?, ?);", (discord_id, sweet_id))

    @staticmethod
    @database_transaction
    def unlink_discord_id(cur, discord_id: Union[discord.Member, discord.User, int]) -> None:
        '''Unlinks a Discord ID from a Sweet ID.'''
        if isinstance(discord_id, discord.Member) or isinstance(discord_id, discord.User):
            discord_id = discord_id.id
        cur.execute("DELETE FROM sweet_user_discord_links WHERE discord_id = ?;", (discord_id,))

### READER ###

class DeceiveReaderActiveChannels:
    @staticmethod
    @database_transaction
    def get_active_channels(cur) -> List[int]:
        '''Gets the active channels from the database.'''
        cur.execute("SELECT * FROM active_channels;")
        results = cur.fetchall()
        return [result[0] for result in results]

    @staticmethod
    @database_transaction
    def add_active_channel(cur, channel_id: int) -> None:
        '''Adds an active channel to the database.'''
        cur.execute("INSERT INTO active_channels (channel_id) VALUES (?);", (channel_id,))

    @staticmethod
    @database_transaction
    def remove_active_channel(cur, channel_id: int) -> None:
        '''Removes an active channel from the database.'''
        cur.execute("DELETE FROM active_channels WHERE channel_id = ?;", (channel_id,))