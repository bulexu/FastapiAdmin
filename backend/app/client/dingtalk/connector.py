"""DingTalk AI 表（Connector）封装

将 baseId 与 unionId 作为可配置变量，提供常用方法：
- list_sheets: 列出 Base 下所有 Sheet
- get_fields: 获取 Sheet 的字段定义
- get_records: 获取 Sheet 的记录
- create_records: 批量新增记录
- update_records: 批量更新记录

基于现有 RPC 服务（hprose）：http://asst.magene.cn/rpc/dingtalk
"""

from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

import hprose


DEFAULT_RPC_URL = os.getenv("DINGTALK_RPC_URL", "http://asst.magene.cn/rpc/dingtalk")


class DingTalkAIConnector:
  """钉钉 AI 表连接器封装"""

  def __init__(
    self,
    base_id: str,
    union_id: str,
    rpc_url: str = DEFAULT_RPC_URL,
  ) -> None:
    """
    Args:
      base_id: AI 表 Base ID
      union_id: 操作人 unionId（需具备目标 Base 的访问权限）
      rpc_url: RPC 服务地址，默认从环境变量 DINGTALK_RPC_URL 读取
    """
    if not base_id:
      raise ValueError("base_id 不能为空")
    if not union_id:
      raise ValueError("union_id 不能为空")
    self.base_id = base_id
    self.union_id = union_id
    self.client = hprose.HttpClient(rpc_url)

  # -------- 基础查询能力 --------
  def list_sheets(self, base_id: Optional[str] = None, union_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """列出 Base 下的所有 Sheet

    Args:
      base_id: 覆盖默认 base_id
      union_id: 覆盖默认 union_id
    """
    bid = base_id or self.base_id
    uid = union_id or self.union_id
    return self.client.get_ai_table_sheets(bid, uid)

  def get_fields(self, sheet_id: str, base_id: Optional[str] = None, union_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取某个 Sheet 的字段列表"""
    if not sheet_id:
      raise ValueError("sheet_id 不能为空")
    bid = base_id or self.base_id
    uid = union_id or self.union_id
    return self.client.get_ai_table_sheet_fields(bid, uid, sheet_id)

  def get_records(self, sheet_id: str, base_id: Optional[str] = None, union_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取某个 Sheet 的所有记录（自动分页获取全部）"""
    if not sheet_id:
      raise ValueError("sheet_id 不能为空")
    bid = base_id or self.base_id
    uid = union_id or self.union_id
    
    all_records = []
    has_more = True
    next_token = None
    
    while has_more:
      response = self.client.get_ai_table_sheet_records(bid, uid, sheet_id, next_token)
      # 兼容两种返回格式：字典（带分页）或列表（无分页）
      if isinstance(response, dict):
        all_records.extend(response.get('records', []))
        has_more = response.get('hasMore', False)
        next_token = response.get('nextToken', None)
      else:
        # 旧版本直接返回列表
        all_records.extend(response if isinstance(response, list) else [])
        has_more = False
    
    return all_records

  # -------- 写入/更新能力 --------
  def create_records(
    self,
    sheet_id: str,
    records: List[Dict[str, Any]],
    base_id: Optional[str] = None,
    union_id: Optional[str] = None,
  ) -> Dict[str, Any]:
    """批量新增记录

    records 结构示例：
    [{
      "fields": {
        "标题": "新标题：2025-11-10 10:00:00",
        "单选": "选项一",
        "日期": "2025-11-10"
      }
    }]
    """
    if not sheet_id:
      raise ValueError("sheet_id 不能为空")
    if not records:
      raise ValueError("records 不能为空")
    bid = base_id or self.base_id
    uid = union_id or self.union_id
    # 自动分批，每批最多 100 条
    batch_size = 100
    results: List[Dict[str, Any]] = []
    for i in range(0, len(records), batch_size):
      batch = records[i:i + batch_size]
      res = self.client.create_ai_table_sheet_records(bid, uid, sheet_id, batch)
      results.append(res)
    return {"success": True, "batches": len(results), "results": results}

  def update_records(
    self,
    sheet_id: str,
    records: List[Dict[str, Any]],
    base_id: Optional[str] = None,
    union_id: Optional[str] = None,
  ) -> Dict[str, Any]:
    """批量更新记录

    records 结构示例：
    [{
      "id": "记录ID",
      "fields": {
        "标题": "新标题3",
        "单选": "选项一"
      }
    }]
    """
    if not sheet_id:
      raise ValueError("sheet_id 不能为空")
    if not records:
      raise ValueError("records 不能为空")
    bid = base_id or self.base_id
    uid = union_id or self.union_id
    # 自动分批，每批最多 50 条
    batch_size = 50
    results: List[Dict[str, Any]] = []
    for i in range(0, len(records), batch_size):
      batch = records[i:i + batch_size]
      res = self.client.update_ai_table_sheet_records(bid, uid, sheet_id, batch)
      results.append(res)
    return {"success": True, "batches": len(results), "results": results}

  # -------- 便捷方法（单条） --------
  def create_record(self, sheet_id: str, fields: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """新增单条记录"""
    return self.create_records(sheet_id, records=[{"fields": fields}], **kwargs)

  def update_record(self, sheet_id: str, record_id: str, fields: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """更新单条记录"""
    return self.update_records(sheet_id, records=[{"id": record_id, "fields": fields}], **kwargs)


# if __name__ == "__main__":
#   # 示例：从环境变量读取 baseId 与 union_id（或直接替换字符串）
#   base_id = "jb9Y4gmKWr7wkj2pTpA2APwMVGXn6lpz"
#   union_id = "WE8EbHLx019kz537fwygrAiEiE"
#   if not base_id or not union_id:
#     print("请先设置 DINGTALK_AI_BASE_ID 与 DINGTALK_AI_UNION_ID 环境变量后再运行此示例")
#   else:
#     conn = DingTalkAIConnector(base_id=base_id, union_id=union_id)
#     sheets = conn.list_sheets()
#     print("Sheets:", sheets)
#     if sheets:
#       sheet_id = sheets[0]["id"]
#       fields = conn.get_fields(sheet_id)
#       print("Fields:", fields)
#       records = conn.get_records(sheet_id)
#       print("Records count:", len(records))

#       # 新增一条记录示例
#       new_fields = {'会议标题': 'DH80充电线&臂带单卖事宜沟通（客户包装设计已完成）', '会议说明': '', '会议类型': '研讨', '组织者': [{'unionId': 'yqGQ8EULRVfuPTDjiPt3NRQiEiE'}], '组织者所属部门': '室外项目部', '3级部门': '室外产品中心', '2级部门': '室外BU', '参会人数': 12, '会议日期': '2025-11-19', '开始时间': '2025-11-19 13:15', '结束时间': '2025-11-19 14:00', '时长(分钟)': 45, 'AI 评分[十分制]': 5.0, 'AI 评分理由': '标题表达较为清晰，明确了会议主题为DH80充电线与臂带单卖事宜的沟通，且提及客户包装设计已完成，具备一定背景信息。但在描述中未提供任何内容，导致无法评估会议的目的（Purpose）、目标（Objective）和议程流程（Timeline/Agenda），POT模型三要素均缺失，严重影响会议目标清晰度。此外，描述空白，无法判断参会人是否合理，尤其对于研讨类会议缺少关键决策人信息。无加分项体现，如背景补充或会议资料。整体信息不完整，仅凭标题给予基础分。'}
#       create_res = conn.create_record(sheet_id, new_fields)
#       print("Create result:", create_res)