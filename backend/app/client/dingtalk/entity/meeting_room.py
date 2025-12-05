from pydantic import BaseModel
from typing import List, Optional

class RoomLabel(BaseModel):
    labelId: Optional[int] = None
    labelName: Optional[str] = None

class RoomLocation(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None

class RoomGroup(BaseModel):
    groupId: Optional[int] = None
    groupName: Optional[str] = None
    parentId: Optional[int] = None

class MeetingRoomInfo(BaseModel):
    roomId: Optional[str] = None
    roomStaffId: Optional[str] = None
    corpId: Optional[str] = None
    roomName: Optional[str] = None
    roomStatus: Optional[int] = None
    roomLabels: Optional[List[RoomLabel]] = None
    roomCapacity: Optional[int] = None
    roomLocation: Optional[RoomLocation] = None
    roomPicture: Optional[str] = None
    isvRoomId: Optional[str] = None
    roomGroup: Optional[RoomGroup] = None

class MeetingRoomListResult(BaseModel):
    hasMore: Optional[bool] = None
    nextToken: Optional[int] = None
    result: Optional[List[MeetingRoomInfo]] = None
