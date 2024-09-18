from datetime import datetime, timezone, timedelta
from typing import Union

### DISCORD DATESTRING GENERATORS ###

class DiscordDatestring:
    @staticmethod
    def _get_epoch_unix_timestamp(time: datetime = datetime.now(timezone.utc)) -> int:
        return int(time.timestamp())
    
    @staticmethod
    def get_discord_timestamp_default(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}>"
    
    @staticmethod
    def get_discord_timestamp_short_time(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}:t>"
    
    @staticmethod
    def get_discord_timestamp_long_time(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}:T>"
    
    @staticmethod
    def get_discord_timestamp_short_date(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}:d>"
    
    @staticmethod
    def get_discord_timestamp_long_date(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}:D>"
    
    @staticmethod
    def get_discord_timestamp_short_datetime(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}:f>"
    
    @staticmethod
    def get_discord_timestamp_long_datetime(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}:F>"
    
    @staticmethod
    def get_discord_timestamp_relative(time: datetime = datetime.now(timezone.utc)) -> str:
        return f"<t:{DiscordDatestring._get_epoch_unix_timestamp(time)}:R>"
    
    @staticmethod
    def is_valid_discord_timestamp(string: str) -> bool:
        return string.startswith("<t:") and string.endswith(">")

    @staticmethod
    def get_datetime_from_discord_timestamp(timestamp: str) -> Union[datetime, None]:
        '''Returns a datetime object from a Discord timestamp string.'''
        try:
            return datetime.fromtimestamp(int(timestamp.split(":")[1]), timezone.utc)
        except ValueError:
            raise ValueError("Invalid Discord timestamp string.")