from pydantic import BaseModel
from typing import List, Optional

class Organizer(BaseModel):
    id: Optional[str] = None

class DateTimeInfo(BaseModel):
    dateTime: Optional[str] = None
    timeZone: Optional[str] = None

class ScheduleItem(BaseModel):
    status: Optional[str] = None
    eventId: Optional[str] = None
    organizer: Optional[Organizer] = None
    start: Optional[DateTimeInfo] = None
    end: Optional[DateTimeInfo] = None

class ScheduleInformation(BaseModel):
    roomId: Optional[str] = None
    error: Optional[str] = None
    scheduleItems: Optional[List[ScheduleItem]] = None

class MeetingRoomScheduleResult(BaseModel):
    scheduleInformation: Optional[List[ScheduleInformation]] = None
