# -*- coding: utf-8 -*-

from typing import List, Any, Tuple, Dict
from datetime import datetime
from sqlglot import select, exp
from app.core.logger import log

def parse_time(val: Any) -> Any:
    if not isinstance(val, str):
        return val
    try:
        return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.strptime(val, '%Y-%m-%d')
        except ValueError:
            return val

def build_dataset_query(args: dict, metadata_columns: list, table_name: str) -> Tuple[str, Dict[str, Any]]:
    """
    构建 SQL 查询字符串，适配 SQLAlchemy text() 执行
    
    参数:
    - args: 查询参数字典
    - metadata_columns: 字段定义列表
    - table_name: 表名
    
    返回:
    - Tuple[str, Dict[str, Any]]: (SQL查询语句, 参数字典)
    """
    query = select("*").from_(exp.Table(this=table_name))
    params = {}

    log.info(f'构建查询 SQL，表名：{table_name}，参数：{args}')
    log.info(f'字段定义：{metadata_columns}')

    for column in metadata_columns:
        # 兼容字典和对象访问
        if isinstance(column, dict):
            column_name = column.get('column_name') or column.get('name')
            query_type = (column.get('query_type') or 'EQ').upper()
            python_type = column.get('python_type')
            is_query = column.get('is_query')
        else:
            column_name = getattr(column, 'column_name', None) or getattr(column, 'name', None)
            query_type = (getattr(column, 'query_type', None) or 'EQ').upper()
            python_type = getattr(column, 'python_type', None)
            is_query = getattr(column, 'is_query', None)

        if not is_query:
            continue

        col_exp = exp.Column(this=column_name)
        
        # 判断是否为时间类型
        is_date_col = python_type and ('date' in str(python_type).lower() or 'datetime' in str(python_type).lower())
        # 判断是否为整数类型
        is_int_col = python_type and ('int' in str(python_type).lower())

        log.info(f'处理字段：{column_name}，查询类型：{query_type}，参数值：{args.get(column_name)}')

        # 使用 column_name 作为参数名
        if column_name in args:
            value = args[column_name]
            if is_date_col:
                value = parse_time(value)
            elif is_int_col and value is not None and value != '':
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass

            if query_type == 'EQ':
                query = query.where(col_exp.eq(exp.Identifier(this=f":{column_name}", quoted=False)))
                params[column_name] = value
            elif query_type == 'NE':
                query = query.where(col_exp != exp.Identifier(this=f":{column_name}", quoted=False))
                params[column_name] = value
            elif query_type == 'GT':
                query = query.where(col_exp > exp.Identifier(this=f":{column_name}", quoted=False))
                params[column_name] = value
            elif query_type == 'LT':
                query = query.where(col_exp < exp.Identifier(this=f":{column_name}", quoted=False))
                params[column_name] = value
            elif query_type == 'GTE':
                query = query.where(col_exp >= exp.Identifier(this=f":{column_name}", quoted=False))
                params[column_name] = value
            elif query_type == 'LTE':
                query = query.where(col_exp <= exp.Identifier(this=f":{column_name}", quoted=False))
                params[column_name] = value
            elif query_type == 'LIKE':
                query = query.where(col_exp.ilike(exp.Identifier(this=f":{column_name}", quoted=False)))
                params[column_name] = f"%{value}%"
            
        # 特殊处理 BETWEEN 查询
        if query_type == 'BETWEEN' and is_date_col:
            # 时间类型字段的 BETWEEN 查询
            start_val = args.get(f'{column_name}[0]')
            end_val = args.get(f'{column_name}[1]')
            
            start_val = parse_time(start_val)
            end_val = parse_time(end_val)

            if start_val and end_val:
                start_key = f"{column_name}_start"
                end_key = f"{column_name}_end"
                query = query.where(col_exp.between(
                    exp.Identifier(this=f":{start_key}", quoted=False),
                    exp.Identifier(this=f":{end_key}", quoted=False)
                ))
                params[start_key] = start_val
                params[end_key] = end_val
            elif start_val:
                start_key = f"{column_name}_start"
                query = query.where(col_exp >= exp.Identifier(this=f":{start_key}", quoted=False))
                params[start_key] = start_val
            elif end_val:
                end_key = f"{column_name}_end"
                query = query.where(col_exp <= exp.Identifier(this=f":{end_key}", quoted=False))
                params[end_key] = end_val
                # 可扩展其他类型
    # 如果没有任何条件，不加 where
    if not args:
        query = query.where(exp.TRUE)
        
    return query.order_by("id desc").sql(), params
