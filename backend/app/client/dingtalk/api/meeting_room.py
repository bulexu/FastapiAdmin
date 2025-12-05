from client.dingtalk.client import DingTalkClient
from alibabacloud_dingtalk.rooms_1_0.client import Client as DingTalkRoomsClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.rooms_1_0 import models as dingtalk_rooms_models
from alibabacloud_tea_util import models as util_models
from client.dingtalk.constants import (
    DINGTALK_SDK_PROTOCOL,
    DINGTALK_SDK_REGION_ID
)
from client.dingtalk.entity.meeting_room import MeetingRoomListResult
import asyncio

# 钉钉会议室API
# https://open.dingtalk.com/document/development/smart-meeting-room-overview
class MeetingRoom(DingTalkClient):
    def __init__(self, app_key: str = None, app_secret: str = None):
        """
        获取钉钉会议室客户端
        
        Args:
            app_key: 钉钉应用Key
            app_secret: 钉钉应用Secret
        """
        super().__init__(app_key, app_secret)
        config = open_api_models.Config()
        config.protocol = DINGTALK_SDK_PROTOCOL
        config.region_id = DINGTALK_SDK_REGION_ID
        self.client = DingTalkRoomsClient(config)

    # https://open.dingtalk.com/document/development/check-the-meeting-room-list
    async def query_meeting_room_list(
        self,
        union_id: str,
        next_token: int = None,
        max_results: int = 20
    ) -> MeetingRoomListResult:
        """
        查询会议室列表
        
        Args:
            union_id: 用户union_id
            next_token: 分页游标
            max_results: 每页数量
            
        Returns:
            MeetingRoomListResult: 会议室列表结果
        """
        try:
            # 设置请求头
            headers = dingtalk_rooms_models.QueryMeetingRoomListHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()

            # 设置请求参数
            request = dingtalk_rooms_models.QueryMeetingRoomListRequest(
                union_id=union_id,
                next_token=next_token,
                max_results=max_results
            )

            def _call_api():
                return self.client.query_meeting_room_list_with_options(
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            # 发起请求
            response = await asyncio.to_thread(_call_api)

            # 处理响应
            if response.status_code == 200:
                return MeetingRoomListResult(**response.body.to_map())
            else:
                raise Exception(f"查询会议室列表失败: {response.body}")

        except Exception as e:
            raise Exception(f"查询会议室列表失败: {str(e)}")
