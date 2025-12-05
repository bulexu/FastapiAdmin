from typing import List, Dict, Any
from client.dingtalk.client import DingTalkClient
import dingtalk.api
from alibabacloud_dingtalk.contact_1_0.client import Client as DingTalkContactClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.contact_1_0 import models as dingtalk_contact_models
from alibabacloud_tea_util import models as util_models
from client.dingtalk.constants import (
    DINGTALK_SDK_PROTOCOL,
    DINGTALK_SDK_REGION_ID,
    DINGTALK_API_BASE_URL
)
import asyncio

# 钉钉通讯录API
# https://open.dingtalk.com/document/development/contacts-overview
class Contact(DingTalkClient):

    def __init__(self, app_key: str = None, app_secret: str = None):
        """
        获取钉钉通讯录客户端

        Returns:
        DingTalkContactClient: 钉钉通讯录客户端
        """
        super().__init__(app_key, app_secret)
        config = open_api_models.Config()
        config.protocol = DINGTALK_SDK_PROTOCOL
        config.region_id = DINGTALK_SDK_REGION_ID
        self.client = DingTalkContactClient(config)

    async def search_users(
        self,
        query_word: str,
        size: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        搜索用户
        
        Args:
            query_word: 搜索关键词（用户名称、名称拼音或英文名称）
            size: 分页大小，最大100
            offset: 分页偏移量
            
        Returns:
            Dict: 搜索结果，包含用户列表和总数
        """
        try:
            # 设置请求头
            headers = dingtalk_contact_models.SearchUserHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()
            
            # 设置请求参数
            request = dingtalk_contact_models.SearchUserRequest(
                query_word=query_word,
                size=size,
                offset=offset
            )
            
            # 发起请求 (SDK 为同步调用，放到线程池中执行以免阻塞事件循环)
            def _call_search_user():
                return self.client.search_user_with_options(
                    request, 
                    headers, 
                    util_models.RuntimeOptions()
                )
            
            response = await asyncio.to_thread(_call_search_user)
            
            # 处理响应
            if response.status_code == 200:
                return response.body.user_list
            else:
                raise Exception(f"搜索用户失败: {response.body.error_msg}")
                
        except Exception as e:
            raise Exception(f"搜索用户失败: {str(e)}")
        
    async def get_user_detail(
            self,
            user_id: str
        ) -> Dict[str, Any]:
            """
            获取用户详细信息
            
            Args:
                user_id: 用户ID
                
            Returns:
                Dict: 用户详细信息
            """
            try:
                # 设置请求头
                headers = dingtalk_contact_models.GetUserHeaders()
                headers.x_acs_dingtalk_access_token = self._get_access_token()
                
                # 设置请求参数
                request = dingtalk_contact_models.GetUserRequest()
                
                # 发起请求 (SDK 为同步调用，放到线程池中执行以免阻塞事件循环)
                def _call_get_user():
                    return self.client.get_user_with_options(
                        user_id, 
                        request, 
                        headers, 
                        util_models.RuntimeOptions()
                    )
                
                response = await asyncio.to_thread(_call_get_user)
                
                # 处理响应
                if response.status_code == 200:
                    return response.body
                else:
                    raise Exception(f"获取用户详情失败: {response.body.error_msg}")
                    
            except Exception as e:
                raise Exception(f"获取用户详情失败: {str(e)}")

    async def get_department_list(
            self,
            parent_id: int = 1
        ) -> List[Dict[str, Any]]:
            """
            获取部门列表
            
            Args:
                parent_id: 父部门ID，默认1表示根部门
                
            Returns:
                List: 部门列表
            """
            try:
                # 设置请求参数
                request = dingtalk.api.OapiV2DepartmentListsubRequest(f"{DINGTALK_API_BASE_URL}/topapi/v2/department/listsub")
                request.dept_id = parent_id
                request.language = "zh"
                
                # 发起请求 (SDK 为同步调用，放到线程池中执行以免阻塞事件循环)
                def _call_list_departments():
                    return request.getResponse(self._get_access_token())
                
                response = await asyncio.to_thread(_call_list_departments)
                
                # 处理响应
                if response.status_code == 200:
                    return response.body.result
                else:
                    raise Exception(f"获取部门列表失败: {response.body.err_msg}")
                    
            except Exception as e:
                raise Exception(f"获取部门列表失败: {str(e)}")

    async def get_department_users(
            self,
            department_id: int,
            offset: int = 0,
            size: int = 100
        ) -> List[Dict[str, Any]]:
            """
            获取部门用户列表
            
            Args:
                department_id: 部门ID
                offset: 分页偏移量
                size: 分页大小，最大100
                
            Returns:
                List: 部门用户列表
            """
            try:
                # 设置请求参数
                request = dingtalk.api.OapiV2UserListRequest(f"{DINGTALK_API_BASE_URL}/topapi/v2/user/list")
                request.dept_id = department_id
                request.offset = offset
                request.size = size
                request.language = "zh"
                
                # 发起请求 (SDK 为同步调用，放到线程池中执行以免阻塞事件循环)
                def _call_list_department_users():
                    return request.getResponse(self._get_access_token())
                
                response = await asyncio.to_thread(_call_list_department_users)
                
                # 处理响应
                if response.status_code == 200:
                    return response.body.result.list
                else:
                    raise Exception(f"获取部门用户列表失败: {response.body.err_msg}")
                    
            except Exception as e:
                raise Exception(f"获取部门用户列表失败: {str(e)}")
            


