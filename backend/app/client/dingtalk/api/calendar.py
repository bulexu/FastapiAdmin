from typing import List
from client.dingtalk.client import DingTalkClient
from alibabacloud_dingtalk.calendar_1_0.client import Client as DingTalkCalendarClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.calendar_1_0 import models as dingtalk_calendar_models
from alibabacloud_tea_util import models as util_models
from client.dingtalk.constants import (
    DINGTALK_SDK_PROTOCOL,
    DINGTALK_SDK_REGION_ID,
    DEFAULT_TIMEZONE,
    DATE_FORMAT
)
from client.dingtalk.entity.event import DingTalkEvent
from client.dingtalk.entity.meeting_room_schedule import MeetingRoomScheduleResult
import asyncio

# 钉钉日历API
# https://open.dingtalk.com/document/development/dingtalk-event-overview
class Calendar(DingTalkClient):

    def __init__(self, app_key: str = None, app_secret: str = None):
        """
        获取钉钉日历客户端
        
        Args:
            app_key: 钉钉应用Key
            app_secret: 钉钉应用Secret
            
        Returns:
            DingTalkCalendarClient: 钉钉日历客户端
        """
        super().__init__(app_key, app_secret)
        config = open_api_models.Config()
        config.protocol = DINGTALK_SDK_PROTOCOL
        config.region_id = DINGTALK_SDK_REGION_ID
        self.client = DingTalkCalendarClient(config)

    # https://open.dingtalk.com/document/development/query-details-about-an-event
    async def get_event(
        self,
        union_id: str,
        event_id: str,
        calendar_id: str = 'primary',
        max_attendees: int = 100
    ) -> DingTalkEvent:
        """
        获取单个日程详情
        
        Args:
            union_id: 用户union_id
            calendar_id: 日历ID
            event_id: 日程ID
            max_attendees: 最大参与者数
            
        Returns:
            DingTalkEvent: 日程详情
        """
        try:
            # 设置请求头
            headers = dingtalk_calendar_models.GetEventHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()
            
            # 设置请求参数
            request = dingtalk_calendar_models.GetEventRequest(
                max_attendees=max_attendees
            )
            
            def _call_get_event():
                return self.client.get_event_with_options(
                    union_id,
                    calendar_id,
                    event_id,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            # 发起请求
            response = await asyncio.to_thread(_call_get_event)
            
            # 处理响应
            if response.status_code == 200:
                return DingTalkEvent(**response.body.to_map())
            else:
                raise Exception(f"获取日程详情失败: {response.body}")
                
        except Exception as e:
            raise Exception(f"获取日程详情失败: {str(e)}")

    async def get_meeting_rooms_schedule(
        self,
        union_id: str,
        room_ids: List[str],
        start_time: str,
        end_time: str
    ) -> MeetingRoomScheduleResult:
        """
        查询会议室忙闲状态
        
        Args:
            union_id: 用户union_id
            room_ids: 会议室ID列表
            start_time: 开始时间，格式：2024-01-01T00:00:00+08:00
            end_time: 结束时间，格式：2024-01-01T23:59:59+08:00
            
        Returns:
            MeetingRoomScheduleResult: 会议室忙闲状态
        """
        try:
            # 设置请求头
            headers = dingtalk_calendar_models.GetMeetingRoomsScheduleHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()
            
            # 设置请求参数
            request = dingtalk_calendar_models.GetMeetingRoomsScheduleRequest(
                room_ids=room_ids,
                start_time=start_time,
                end_time=end_time
            )
            
            def _call_api():
                return self.client.get_meeting_rooms_schedule_with_options(
                    union_id,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            # 发起请求
            response = await asyncio.to_thread(_call_api)
            
            # 处理响应
            if response.status_code == 200:
                return MeetingRoomScheduleResult(**response.body.to_map())
            else:
                raise Exception(f"查询会议室忙闲状态失败: {response.body}")
                
        except Exception as e:
            raise Exception(f"查询会议室忙闲状态失败: {str(e)}")