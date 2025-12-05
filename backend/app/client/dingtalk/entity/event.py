from pydantic import BaseModel, Field
from typing import List, Optional

class DateTimeInfo(BaseModel):
    date: Optional[str] = None
    dateTime: Optional[str] = None
    timeZone: Optional[str] = None

class OriginStart(BaseModel):
    dateTime: Optional[str] = None

class RecurrencePattern(BaseModel):
    type: Optional[str] = None
    dayOfMonth: Optional[int] = None
    daysOfWeek: Optional[str] = None
    index: Optional[str] = None
    interval: Optional[int] = None

class RecurrenceRange(BaseModel):
    type: Optional[str] = None
    endDate: Optional[str] = None
    numberOfOccurrences: Optional[int] = None

class Recurrence(BaseModel):
    pattern: Optional[RecurrencePattern] = None
    range: Optional[RecurrenceRange] = None

class Attendee(BaseModel):
    id: Optional[str] = None
    displayName: Optional[str] = None
    responseStatus: Optional[str] = None
    self: Optional[bool] = None
    isOptional: Optional[bool] = None

class Organizer(BaseModel):
    id: Optional[str] = None
    displayName: Optional[str] = None
    responseStatus: Optional[str] = None
    self: Optional[bool] = None

class Location(BaseModel):
    displayName: Optional[str] = None
    meetingRooms: Optional[List[str]] = None

class Reminder(BaseModel):
    method: Optional[str] = None
    minutes: Optional[str] = None

class OnlineMeetingInfo(BaseModel):
    type: Optional[str] = None
    conferenceId: Optional[str] = None
    url: Optional[str] = None

class SharedProperties(BaseModel):
    sourceOpenCid: Optional[str] = None
    belongCorpId: Optional[str] = None

class ExtendedProperties(BaseModel):
    sharedProperties: Optional[SharedProperties] = None

class MeetingRoom(BaseModel):
    roomId: Optional[str] = None
    responseStatus: Optional[str] = None
    displayName: Optional[str] = None

class Category(BaseModel):
    displayName: Optional[str] = None

class DingTalkEvent(BaseModel):
    id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start: Optional[DateTimeInfo] = None
    originStart: Optional[OriginStart] = None
    end: Optional[DateTimeInfo] = None
    isAllDay: Optional[bool] = None
    recurrence: Optional[Recurrence] = None
    attendees: Optional[List[Attendee]] = None
    organizer: Optional[Organizer] = None
    location: Optional[Location] = None
    seriesMasterId: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None
    reminders: Optional[List[Reminder]] = None
    onlineMeetingInfo: Optional[OnlineMeetingInfo] = None
    extendedProperties: Optional[ExtendedProperties] = None
    meetingRooms: Optional[List[MeetingRoom]] = None
    categories: Optional[List[Category]] = None
