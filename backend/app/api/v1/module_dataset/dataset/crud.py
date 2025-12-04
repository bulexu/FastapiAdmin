# -*- coding: utf-8 -*-

from sqlalchemy import text
from app.core.exceptions import CustomException
from app.core.base_params import PaginationQueryParam
from app.utils.raw_sql_util import build_dataset_query
from app.core.logger import log

from app.api.v1.module_system.auth.schema import AuthSchema

class DatasetCRUD:
    """元数据数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth

    async def get_dataset_data_crud(self, page: PaginationQueryParam, args: dict, table_name: str, columns: list) -> dict | list:
        """
        获取元数据表数据
        """
        try:
            # 使用 build_query 构建 SQL, 注意处理 sql 注入
            sql, params = build_dataset_query(args, columns, table_name)

            log.info(f'查询元数据表 SQL: {sql}')
            log.info(f'查询元数据表参数: {params}')
            
            # 构建 count SQL
            # 简单的替换 SELECT * 为 SELECT COUNT(*)
            # 或者重新调用 build_query 但只获取 count
            # 这里简单处理：
            count_sql = f"SELECT COUNT(*) FROM ({sql}) AS count_table"
            count_res = await self.auth.db.execute(text(count_sql), params)
            total = count_res.scalar()
            
            # 添加分页
            offset = (page.page_no - 1) * page.page_size
            limit = page.page_size
            has_next = False

            # page_size = -1 表示不分页，获取所有数据
            if page.page_size > 0:
                sql += f" LIMIT {limit} OFFSET {offset}"
                has_next = offset + limit < total

            # 执行查询
            result = await self.auth.db.execute(text(sql), params)
            rows = [dict(row) for row in result.mappings().all()]
            
            return {
                "page_no": page.page_no,
                "page_size": page.page_size,
                "total": total,
                "has_next": has_next,
                "items": rows,
            }
                
        except Exception as e:
            raise CustomException(msg=f"查询数据失败: {str(e)}")
