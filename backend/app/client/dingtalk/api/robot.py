"""钉钉机器人能力封装

提供两类功能：
1. 群机器人 Webhook（自定义机器人）发送普通消息：text/markdown/link/actionCard/feedCard
2. “钉”通知 (Ding) 与单聊/批量机器人发送，使用官方 `robot_1_0` OpenAPI

依赖：
- alibabacloud-dingtalk (用于 robot_1_0 Client)
- requests (Webhook 直接 POST)
"""
import json
import time
from typing import List, Dict, Any, Optional
import requests

from alibabacloud_dingtalk.robot_1_0.client import Client as DingTalkRobotClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.robot_1_0 import models as robot_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from client.dingtalk.client import DingTalkClient
from client.dingtalk.constants import DINGTALK_SDK_PROTOCOL, DINGTALK_SDK_REGION_ID


class RobotWebhook:
    """钉钉群自定义机器人（Webhook + 可选签名）"""

    def __init__(self, webhook: str, secret: Optional[str] = None, timeout: int = 10):
        self.webhook = webhook
        self.secret = secret
        self.timeout = timeout

    def _sign(self) -> Dict[str, str]:
        if not self.secret:
            return {}
        import hashlib, hmac, base64
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.secret}".encode("utf-8")
        hmac_code = hmac.new(self.secret.encode("utf-8"), string_to_sign, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return {"timestamp": timestamp, "sign": sign}

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        params = self._sign()
        try:
            resp = requests.post(self.webhook, params=params, json=payload, timeout=self.timeout)
            data = resp.json() if resp.content else {}
            if resp.status_code == 200 and data.get("errcode") == 0:
                return {"success": True}
            return {"success": False, "error": data.get("errmsg", f"HTTP {resp.status_code}")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_text(self, content: str, at_mobiles: Optional[List[str]] = None, is_at_all: bool = False):
        payload = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {"atMobiles": at_mobiles or [], "isAtAll": is_at_all}
        }
        return self._post(payload)

    def send_markdown(self, title: str, text: str):
        payload = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
        return self._post(payload)

    def send_link(self, title: str, text: str, message_url: str, pic_url: str = ""):
        payload = {
            "msgtype": "link",
            "link": {"title": title, "text": text, "messageUrl": message_url, "picUrl": pic_url}
        }
        return self._post(payload)

    def send_action_card(self, title: str, text: str, btns: List[Dict[str, str]], btn_orientation: str = "0"):
        payload = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btns": btns,
                "btnOrientation": btn_orientation
            }
        }
        return self._post(payload)

    def send_feed_card(self, links: List[Dict[str, str]]):
        payload = {"msgtype": "feedCard", "feedCard": {"links": links}}
        return self._post(payload)


class Robot(DingTalkClient):
    """钉通知 / 单聊机器人消息封装 (依赖 robot_1_0 OpenAPI)"""

    def __init__(self, app_key: str = None, app_secret: str = None):
        super().__init__(app_key, app_secret)
        config = open_api_models.Config()
        config.protocol = DINGTALK_SDK_PROTOCOL
        config.region_id = DINGTALK_SDK_REGION_ID
        self.client = DingTalkRobotClient(config)

    def _headers(self):
        h = robot_models.RobotSendDingHeaders()
        h.x_acs_dingtalk_access_token = self._get_access_token()
        return h

    def send_ding(
        self,
        robot_code: str,
        receiver_user_ids: List[str],
        content: str,
        remind_type: int = 1,
        call_voice: str = "Standard_Female_Voice",
    ) -> Dict[str, Any]:
        """发送钉通知 (语音/文字提醒)

        remind_type: 1=语音, 2=文字
        call_voice: 语音类型，可在开放平台文档查看枚举
        """
        req = robot_models.RobotSendDingRequest(
            robot_code=robot_code,
            remind_type=remind_type,
            receiver_user_id_list=receiver_user_ids,
            content=content,
            call_voice=call_voice,
        )
        try:
            resp = self.client.robot_send_ding_with_options(req, self._headers(), util_models.RuntimeOptions())
            if resp.status_code == 200 and getattr(resp.body, "result", None):
                return {"success": True, "request_id": resp.body.request_id}
            return {"success": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # https://open.dingtalk.com/document/dingstart/types-of-messages-sent-by-robots
    # 不同的通知类型
    def batch_send_oto(
        self,
        robot_code: str,
        user_ids: List[str],
        msg_key: str,
        msg_param: Dict[str, Any],
    ) -> Dict[str, Any]:
        """单聊批量发送（例如 markdown 模板）

        msg_key: 需在钉钉开发后台配置的消息模板 key
        msg_param: 与模板匹配的参数字典
        """
        headers = robot_models.BatchSendOTOHeaders()
        headers.x_acs_dingtalk_access_token = self._get_access_token()
        req = robot_models.BatchSendOTORequest(
            robot_code=robot_code,
            user_ids=user_ids,
            msg_key=msg_key,
            msg_param=json.dumps(msg_param, ensure_ascii=False)
        )
        try:
            resp = self.client.batch_send_otowith_options(req, headers, util_models.RuntimeOptions())
            
            if resp.status_code == 200:
                return {"success": True, "process_query_key": resp.body.process_query_key}
            
            return {"success": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


__all__ = ["RobotWebhook", "Robot"]
