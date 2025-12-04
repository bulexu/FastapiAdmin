# -*- coding: utf-8 -*-

from typing import List, Any
from sqlglot import select, exp

def build_query(args: dict, metadata_columns: list, table_name: str) -> str:
    """
    构建 SQL 查询字符串，适配 SQLAlchemy text() 执行
    
    参数:
    - args: 查询参数字典
    - metadata_columns: 字段定义列表
    - table_name: 表名
    
    返回:
    - str: SQL查询语句
    """
    query = select("*").from_(exp.Table(this=table_name))
    has_condition = False

    for column in metadata_columns:
        # 兼容字典和对象访问
        if isinstance(column, dict):
            column_name = column.get('column_name') or column.get('name')
            query_type = (column.get('query_type') or 'EQ').upper()
            python_type = column.get('python_type')
            python_field = column.get('python_field')
            is_query = column.get('is_query')
        else:
            column_name = getattr(column, 'column_name', None) or getattr(column, 'name', None)
            query_type = (getattr(column, 'query_type', None) or 'EQ').upper()
            python_type = getattr(column, 'python_type', None)
            python_field = getattr(column, 'python_field', None)
            is_query = getattr(column, 'is_query', None)

        if not is_query:
            continue

        col_exp = exp.Column(this=column_name)

        # 使用 python_field 作为参数名
        if python_field in args and args[python_field]:
            value = args[python_field]
            has_condition = True

            if query_type == 'EQ':
                query = query.where(col_exp.eq(value))
            elif query_type == 'NE':
                query = query.where(col_exp != value)
            elif query_type == 'GT':
                query = query.where(col_exp > value)
            elif query_type == 'LT':
                query = query.where(col_exp < value)
            elif query_type == 'GTE':
                query = query.where(col_exp >= value)
            elif query_type == 'LTE':
                query = query.where(col_exp <= value)
            elif query_type == 'LIKE':
                query = query.where(col_exp.ilike(f"%{value}%"))
            elif query_type == 'BETWEEN' and python_type and (
                    'date' in str(python_type).lower() or 'datetime' in str(python_type).lower()):
                # 时间类型字段的 BETWEEN 查询
                start_val = None
                end_val = None
                
                # 如果 args 是 dict，且 value 是 list/tuple
                if isinstance(value, (list, tuple)) and len(value) >= 2:
                    start_val = value[0]
                    end_val = value[1]
                else:
                    # 尝试从 args 中获取数组形式的参数
                    start_val = args.get(f'{python_field}[0]')
                    end_val = args.get(f'{python_field}[1]')

                if start_val and end_val:
                    query = query.where(col_exp.between(start_val, end_val))
                elif start_val:
                    query = query.where(col_exp >= start_val)
                elif end_val:
                    query = query.where(col_exp <= end_val)
            # 可扩展其他类型

    return query.order_by("id desc").sql()
