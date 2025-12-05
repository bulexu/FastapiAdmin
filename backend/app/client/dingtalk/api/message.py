from typing import List, Dict, Any, Optional, Union
from client.dingtalk.client import DingTalkClient
from alibabacloud_tea_openapi import models as open_api_models
from client.dingtalk.constants import (
    DINGTALK_SDK_PROTOCOL,
    DINGTALK_SDK_REGION_ID,
    DINGTALK_API_BASE_URL,
)
import asyncio
import json
import requests


# 钉钉工作通知 TODO 待测试
class Message(DingTalkClient):
    """钉钉消息通知类，支持文本、Markdown、卡片等多种消息类型。

    说明：
    - 工作通知消息直接调用 TopAPI：
      `POST /topapi/message/corpconversation/asyncsend_v2`。
    """

    def __init__(self, app_key: str = None, app_secret: str = None):
        super().__init__(app_key, app_secret)
        # 仍保留通用 SDK 配置对象，便于将来切换到 SDK
        config = open_api_models.Config()
        config.protocol = DINGTALK_SDK_PROTOCOL
        config.region_id = DINGTALK_SDK_REGION_ID
        self._config = config
    
    async def send_text_message(
        self,
        user_ids: Union[str, List[str]],
        content: str,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            user_ids: 接收用户ID列表或逗号分隔的字符串
            content: 文本内容
            agent_id: 应用agentId（选填，默认使用环境配置）
            
        Returns:
            Dict: 发送结果，包含task_id等信息
        """
        msg = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        return await self._send_corp_conversation_message(user_ids, msg, agent_id)
    
    async def send_markdown_message(
        self,
        user_ids: Union[str, List[str]],
        title: str,
        content: str,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送Markdown消息
        
        Args:
            user_ids: 接收用户ID列表或逗号分隔的字符串
            title: 消息标题
            content: Markdown内容
            agent_id: 应用agentId
            
        Returns:
            Dict: 发送结果
        """
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            }
        }
        return await self._send_corp_conversation_message(user_ids, msg, agent_id)
    
    async def send_link_message(
        self,
        user_ids: Union[str, List[str]],
        title: str,
        text: str,
        message_url: str,
        pic_url: Optional[str] = None,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送链接消息
        
        Args:
            user_ids: 接收用户ID列表
            title: 消息标题
            text: 消息文本
            message_url: 点击消息跳转的URL
            pic_url: 图片URL（可选）
            agent_id: 应用agentId
            
        Returns:
            Dict: 发送结果
        """
        msg = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "messageUrl": message_url,
                "picUrl": pic_url or ""
            }
        }
        return await self._send_corp_conversation_message(user_ids, msg, agent_id)
    
    async def send_action_card_message(
        self,
        user_ids: Union[str, List[str]],
        title: str,
        markdown: str,
        single_title: str,
        single_url: str,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送独立跳转ActionCard消息
        
        Args:
            user_ids: 接收用户ID列表
            title: 消息标题
            markdown: Markdown格式的消息内容
            single_title: 单个按钮的标题
            single_url: 单个按钮的跳转链接
            agent_id: 应用agentId
            
        Returns:
            Dict: 发送结果
        """
        msg = {
            "msgtype": "action_card",
            "action_card": {
                "title": title,
                "markdown": markdown,
                "single_title": single_title,
                "single_url": single_url
            }
        }
        return await self._send_corp_conversation_message(user_ids, msg, agent_id)
    
    async def send_action_card_multi_message(
        self,
        user_ids: Union[str, List[str]],
        title: str,
        markdown: str,
        btn_orientation: str,
        btns: List[Dict[str, str]],
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送多按钮ActionCard消息
        
        Args:
            user_ids: 接收用户ID列表
            title: 消息标题
            markdown: Markdown格式的消息内容
            btn_orientation: 按钮排列方向，"0"横向，"1"纵向
            btns: 按钮列表，格式：[{"title": "按钮1", "action_url": "https://..."}]
            agent_id: 应用agentId
            
        Returns:
            Dict: 发送结果
        """
        msg = {
            "msgtype": "action_card",
            "action_card": {
                "title": title,
                "markdown": markdown,
                "btn_orientation": btn_orientation,
                "btn_json_list": btns
            }
        }
        return await self._send_corp_conversation_message(user_ids, msg, agent_id)
    
    async def send_oa_message(
        self,
        user_ids: Union[str, List[str]],
        head_bgcolor: str,
        head_text: str,
        body_title: str,
        body_form: List[Dict[str, str]],
        body_content: Optional[str] = None,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送OA消息
        
        Args:
            user_ids: 接收用户ID列表
            head_bgcolor: 消息头部的背景颜色，如"FFBBBBBB"
            head_text: 消息头部的标题
            body_title: 消息体的标题
            body_form: 消息体的表单，格式：[{"key": "字段名", "value": "字段值"}]
            body_content: 消息体的内容（可选）
            agent_id: 应用agentId
            
        Returns:
            Dict: 发送结果
        """
        msg = {
            "msgtype": "oa",
            "oa": {
                "head": {
                    "bgcolor": head_bgcolor,
                    "text": head_text
                },
                "body": {
                    "title": body_title,
                    "form": body_form
                }
            }
        }
        if body_content:
            msg["oa"]["body"]["content"] = body_content
        
        return await self._send_corp_conversation_message(user_ids, msg, agent_id)
    
    async def _send_corp_conversation_message(
        self,
        user_ids: Union[str, List[str]],
        msg: Dict[str, Any],
        agent_id: Optional[int] = None,
        to_all_user: bool = False,
    ) -> Dict[str, Any]:
        """
        发送工作通知消息（内部方法）
        
        Args:
            user_ids: 接收用户ID列表或逗号分隔的字符串
            msg: 消息体
            agent_id: 应用agentId（必填，若未传入将抛出异常）
            to_all_user: 是否发给企业全部用户
            
        Returns:
            Dict: 发送结果
        """
        try:
            # 校验 agent_id
            if not agent_id:
                raise ValueError("agent_id 不能为空，请传入钉钉应用的 agentId")

            # 处理 user_ids 格式
            if isinstance(user_ids, list):
                user_id_list = ",".join(user_ids)
            else:
                user_id_list = str(user_ids or "").strip()

            url = f"{DINGTALK_API_BASE_URL}/topapi/message/corpconversation/asyncsend_v2"
            access_token = self._get_access_token()

            payload = {
                "agent_id": agent_id,
                "msg": json.dumps(msg, ensure_ascii=False),
                "to_all_user": to_all_user,
            }
            if user_id_list:
                payload["userid_list"] = user_id_list

            resp = requests.post(url, params={"access_token": access_token}, data=payload, timeout=10)

            if resp.status_code != 200:
                return {"success": False, "error": f"HTTP {resp.status_code}"}

            data = resp.json()
            if data.get("errcode") == 0:
                task_id = data.get("result", {}).get("task_id") or data.get("task_id")
                return {"success": True, "task_id": task_id}
            else:
                return {"success": False, "error": data.get("errmsg")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_text_message_sync(
        self,
        user_ids: Union[str, List[str]],
        content: str,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送文本消息（同步版本）"""
        return asyncio.run(self.send_text_message(user_ids, content, agent_id))
    
    def send_markdown_message_sync(
        self,
        user_ids: Union[str, List[str]],
        title: str,
        content: str,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送Markdown消息（同步版本）"""
        return asyncio.run(self.send_markdown_message(user_ids, title, content, agent_id))
    
    def send_link_message_sync(
        self,
        user_ids: Union[str, List[str]],
        title: str,
        text: str,
        message_url: str,
        pic_url: Optional[str] = None,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送链接消息（同步版本）"""
        return asyncio.run(self.send_link_message(user_ids, title, text, message_url, pic_url, agent_id))