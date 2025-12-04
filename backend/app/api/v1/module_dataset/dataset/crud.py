# -*- coding: utf-8 -*-

from sqlalchemy import text
from app.core.exceptions import CustomException
from app.utils.dataset_util import build_query

from app.api.v1.module_system.auth.schema import AuthSchema

class DatasetCRUD:
    """元数据数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth

    async def get_dataset_data_crud(self, args: dict, table_name: str, columns: list, is_page: bool = False) -> dict | list:
        """
        获取元数据表数据
        """
        try:
            # 使用 build_query 构建 SQL
            sql = build_query(args, columns, table_name)
            
            # 提取参数用于 SQLAlchemy 执行
            # 注意：build_query 生成的 SQL 是直接嵌入值的（sqlglot 默认行为），
            # 或者如果使用了参数化占位符，需要相应处理。
            # sqlglot 生成的 SQL 通常是完整的 SQL 字符串。
            # 如果需要参数化，build_query 需要调整为生成带占位符的 SQL 和参数字典。
            # 但根据 build_query 的实现，它直接生成了带值的 SQL (例如 where name = 'value')
            # 这在安全性上依赖于 sqlglot 的转义机制。
            # 为了安全起见，最好还是使用参数化查询。
            # 但目前的 build_query 实现似乎是直接拼接值的（通过 sqlglot 表达式）。
            # 让我们检查一下 build_query 的实现。
            # build_query 使用了 col_exp.eq(value)，sqlglot 会处理值的转义。
            
            if is_page:
                page = int(args.get('page_no', 1))
                size = int(args.get('page_size', 10))
                offset = (page - 1) * size
                
                # 构建 count SQL
                # 简单的替换 SELECT * 为 SELECT COUNT(*)
                # 或者重新调用 build_query 但只获取 count
                # 这里简单处理：
                count_sql = f"SELECT COUNT(*) FROM ({sql}) AS count_table"
                count_res = await self.auth.db.execute(text(count_sql))
                total = count_res.scalar()
                
                # 添加分页
                sql += f" LIMIT {size} OFFSET {offset}"
                result = await self.auth.db.execute(text(sql))
                rows = result.mappings().all()
                
                return {
                    "rows": rows,
                    "total": total,
                    "page_no": page,
                    "page_size": size
                }
            else:
                result = await self.auth.db.execute(text(sql))
                rows = result.mappings().all()
                return rows
                
        except Exception as e:
            raise CustomException(msg=f"查询数据失败: {str(e)}")
