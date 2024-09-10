from datetime import datetime, timezone

class Scrim:
    scrim_id: str
    scrim_start_time: datetime
    scrim_checkin_start_time: datetime
    scrim_checkin_end_time: datetime
    is_active: bool

    def is_checkin_active(self):
        return self.scrim_checkin_start_time <= datetime.now(timezone.utc) and datetime.now(timezone.utc) <= self.scrim_checkin_end_time
    
