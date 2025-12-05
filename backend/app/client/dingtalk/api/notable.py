from typing import List, Dict, Any, Optional
from client.dingtalk.client import DingTalkClient
from alibabacloud_dingtalk.notable_1_0.client import Client as DingTalkNotableClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.notable_1_0 import models as dingtalk_notable_models
from alibabacloud_tea_util import models as util_models
from client.dingtalk.constants import (
    DINGTALK_SDK_PROTOCOL,
    DINGTALK_SDK_REGION_ID
)
import asyncio

# 钉钉文档 https://open.dingtalk.com/document/development/api-notable-listrecords
class Notable(DingTalkClient):
    """钉钉AI表格 API"""

    def __init__(self, app_key: str = None, app_secret: str = None):
        """
        初始化钉钉知识库客户端

        Args:
            app_key: 钉钉应用 Key
            app_secret: 钉钉应用 Secret
        """
        super().__init__(app_key, app_secret)
        config = open_api_models.Config()
        config.protocol = DINGTALK_SDK_PROTOCOL
        config.region_id = DINGTALK_SDK_REGION_ID
        self.client = DingTalkNotableClient(config)

    async def list_records(
        self,
        base_id: str,
        table_name: str,
        operator_id: str,
        max_results: int = 100,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询知识库记录列表

        Args:
            base_id: 知识库 ID
            table_name: 数据表名称
            operator_id: 操作者的 union_id
            max_results: 单页最大记录数，默认 100
            next_token: 分页标记，用于翻页

        Returns:
            Dict: 记录列表结果，包含 records 和 next_token
        """
        try:
            # 设置请求头
            headers = dingtalk_notable_models.ListRecordsHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()

            # 设置请求参数
            request = dingtalk_notable_models.ListRecordsRequest(
                operator_id=operator_id,
                max_results=max_results,
                next_token=next_token
            )

            # 发起请求 (SDK 为同步调用，放到线程池中执行以免阻塞事件循环)
            def _call_list_records():
                return self.client.list_records_with_options(
                    base_id,
                    table_name,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            response = await asyncio.to_thread(_call_list_records)

            # 处理响应
            if response.status_code == 200:
                return {
                    'records': response.body.records,
                    'next_token': response.body.next_token,
                    'has_more': response.body.has_more
                }
            else:
                raise Exception(f"查询记录列表失败: {response.body.error_msg}")

        except Exception as e:
            raise Exception(f"查询记录列表失败: {str(e)}")

    async def get_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
        operator_id: str
    ) -> Dict[str, Any]:
        """
        获取单条记录详情

        Args:
            base_id: 知识库 ID
            table_name: 数据表名称
            record_id: 记录 ID
            operator_id: 操作者的 union_id

        Returns:
            Dict: 记录详情
        """
        try:
            # 设置请求头
            headers = dingtalk_notable_models.GetRecordHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()

            # 设置请求参数
            request = dingtalk_notable_models.GetRecordRequest(
                operator_id=operator_id
            )

            # 发起请求
            def _call_get_record():
                return self.client.get_record_with_options(
                    base_id,
                    table_name,
                    record_id,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            response = await asyncio.to_thread(_call_get_record)

            # 处理响应
            if response.status_code == 200:
                return response.body.to_map()
            else:
                raise Exception(f"获取记录详情失败: {response.body.error_msg}")

        except Exception as e:
            raise Exception(f"获取记录详情失败: {str(e)}")

    async def create_record(
        self,
        base_id: str,
        table_name: str,
        operator_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建记录

        Args:
            base_id: 知识库 ID
            table_name: 数据表名称
            operator_id: 操作者的 union_id
            fields: 记录字段，key 为字段名，value 为字段值

        Returns:
            Dict: 创建的记录信息
        """
        try:
            # 设置请求头
            headers = dingtalk_notable_models.CreateRecordHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()

            # 设置请求参数
            request = dingtalk_notable_models.CreateRecordRequest(
                operator_id=operator_id,
                fields=fields
            )

            # 发起请求
            def _call_create_record():
                return self.client.create_record_with_options(
                    base_id,
                    table_name,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            response = await asyncio.to_thread(_call_create_record)

            # 处理响应
            if response.status_code == 200:
                return response.body.to_map()
            else:
                raise Exception(f"创建记录失败: {response.body.error_msg}")

        except Exception as e:
            raise Exception(f"创建记录失败: {str(e)}")

    async def update_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
        operator_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新记录

        Args:
            base_id: 知识库 ID
            table_name: 数据表名称
            record_id: 记录 ID
            operator_id: 操作者的 union_id
            fields: 要更新的字段，key 为字段名，value 为字段值

        Returns:
            Dict: 更新后的记录信息
        """
        try:
            # 设置请求头
            headers = dingtalk_notable_models.UpdateRecordHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()

            # 设置请求参数
            request = dingtalk_notable_models.UpdateRecordRequest(
                operator_id=operator_id,
                fields=fields
            )

            # 发起请求
            def _call_update_record():
                return self.client.update_record_with_options(
                    base_id,
                    table_name,
                    record_id,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            response = await asyncio.to_thread(_call_update_record)

            # 处理响应
            if response.status_code == 200:
                return response.body.to_map()
            else:
                raise Exception(f"更新记录失败: {response.body.error_msg}")

        except Exception as e:
            raise Exception(f"更新记录失败: {str(e)}")

    async def delete_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
        operator_id: str
    ) -> bool:
        """
        删除记录

        Args:
            base_id: 知识库 ID
            table_name: 数据表名称
            record_id: 记录 ID
            operator_id: 操作者的 union_id

        Returns:
            bool: 是否删除成功
        """
        try:
            # 设置请求头
            headers = dingtalk_notable_models.DeleteRecordHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()

            # 设置请求参数
            request = dingtalk_notable_models.DeleteRecordRequest(
                operator_id=operator_id
            )

            # 发起请求
            def _call_delete_record():
                return self.client.delete_record_with_options(
                    base_id,
                    table_name,
                    record_id,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            response = await asyncio.to_thread(_call_delete_record)

            # 处理响应
            if response.status_code == 200:
                return True
            else:
                raise Exception(f"删除记录失败: {response.body.error_msg}")

        except Exception as e:
            raise Exception(f"删除记录失败: {str(e)}")

    async def batch_create_records(
        self,
        base_id: str,
        table_name: str,
        operator_id: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量创建记录

        Args:
            base_id: 知识库 ID
            table_name: 数据表名称
            operator_id: 操作者的 union_id
            records: 记录列表，每条记录为 {fields: {...}}

        Returns:
            Dict: 批量创建结果
        """
        try:
            # 设置请求头
            headers = dingtalk_notable_models.BatchCreateRecordsHeaders()
            headers.x_acs_dingtalk_access_token = self._get_access_token()

            # 设置请求参数
            request = dingtalk_notable_models.BatchCreateRecordsRequest(
                operator_id=operator_id,
                records=records
            )

            # 发起请求
            def _call_batch_create():
                return self.client.batch_create_records_with_options(
                    base_id,
                    table_name,
                    request,
                    headers,
                    util_models.RuntimeOptions()
                )

            response = await asyncio.to_thread(_call_batch_create)

            # 处理响应
            if response.status_code == 200:
                return response.body.to_map()
            else:
                raise Exception(f"批量创建记录失败: {response.body.error_msg}")

        except Exception as e:
            raise Exception(f"批量创建记录失败: {str(e)}")
