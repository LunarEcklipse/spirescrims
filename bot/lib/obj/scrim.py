from datetime import datetime, timezone
from lib.obj.scrim_format import ScrimFormat

class Scrim:
    scrim_id: str
    scrim_format: ScrimFormat
    scrim_start_time: datetime
    scrim_checkin_start_time: datetime
    scrim_checkin_end_time: datetime
    is_active: bool

    def __init__(self, scrim_id: str, scrim_format: ScrimFormat, scrim_start_time: datetime, scrim_checkin_start_time: datetime, scrim_checkin_end_time: datetime):
        self.scrim_id = scrim_id
        self.scrim_format = scrim_format
        self.scrim_start_time = scrim_start_time
        self.scrim_checkin_start_time = scrim_checkin_start_time
        self.scrim_checkin_end_time = scrim_checkin_end_time
        self.is_active = self.is_checkin_active()

    def is_checkin_active(self):
        return self.scrim_checkin_start_time <= datetime.now(timezone.utc) and datetime.now(timezone.utc) <= self.scrim_checkin_end_time
    
