# -*- coding: utf-8 -*-

from app.core.logger import log
from app.core.base_params import PaginationQueryParam
from app.utils.excel_util import ExcelUtil
from app.api.v1.module_system.auth.schema import AuthSchema
from .crud import DatasetCRUD


class DatasetService:
    
    @classmethod
    async def get_dataset_list_service(cls, auth: AuthSchema, page: PaginationQueryParam, args: dict, table_name: str, columns: list):
        """
        获取元数据表数据服务
        :param auth: 认证信息
        :param args: 查询参数
        :param table_name: 表名
        :param columns: 字段定义列表
        :param is_page: 是否分页
        """
        data_result = await DatasetCRUD(auth).get_dataset_data_crud(page, args, table_name, columns)
        return data_result

    @classmethod
    async def export_dataset_list_service(cls, auth: AuthSchema, args: dict, table_name: str, columns: list, dict_map: dict = None):
        """
        导出元数据表数据服务
        :param auth: 认证信息
        :param args: 查询参数
        :param table_name: 表名
        :param columns: 字段定义列表
        :param dict_map: 字典映射
        :return: excel 二进制数据
        """
        # 查询数据
        page = PaginationQueryParam(page_no=1, page_size=-1)
        data_result = await DatasetCRUD(auth).get_dataset_data_crud(page, args, table_name, columns)
        rows = data_result.get('items', []) if isinstance(data_result, dict) else data_result

        # 构建 mapping_dict: {python_field: columnComment}
        mapping_dict = {col.get('python_field'): (col.get('column_comment') or col.get('column_name')) for col in columns}

        log.info(f'导出数据条数: {len(rows)}')
        if rows:
            log.info(f'导出示例: {rows[0]}')
        log.info(f'导出字段映射: {mapping_dict}')

        # 转换为字典列表以便修改
        rows = [dict(row) for row in rows]

        # 处理字典字段
        if dict_map:
            for row in rows:
                for col in columns:
                    dict_type = col.get('dict_type')
                    python_field = col.get('python_field')
                    
                    if dict_type and dict_type in dict_map and python_field in row:
                        # dict_map[dict_type] is a list of objects
                        dict_options = {str(item.dict_value): item.dict_label for item in dict_map[dict_type]}
                        val = str(row[python_field])
                        if val in dict_options:
                            row[python_field] = dict_options[val]

        # 导出 excel 二进制
        binary_data = ExcelUtil.export_list2excel(rows, mapping_dict)
        return binary_data

    
    
    
    

    