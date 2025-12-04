# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, Request, Path
from fastapi.responses import JSONResponse, StreamingResponse
from redis.asyncio.client import Redis
import urllib.parse

from app.common.response import SuccessResponse, StreamResponse
from app.core.router_class import OperationLogRoute
from app.core.dependencies import AuthPermission, redis_getter
from app.core.base_params import PaginationQueryParam
from app.core.logger import log
from app.utils.common_util import bytes2file_response
from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_generator.gencode.service import GenTableService, GenTableColumnService
from app.api.v1.module_generator.gencode.schema import GenTableQueryParam
from app.api.v1.module_system.dict.service import DictDataService
from .service import DatasetService


DatasetRouter = APIRouter(route_class=OperationLogRoute, prefix='/dataset', tags=["数据集管理"])

@DatasetRouter.get('/list', summary="获取数据集表列表", description="获取数据集表列表")
async def get_meta_table_list_controller(
    search: GenTableQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_dataset:dataset:query"]))
) -> JSONResponse:
    """
    获取数据集表列表
    
    参数:
    - search (GenTableQueryParam): 查询参数
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含数据集表列表的JSON响应
    """
    result = await GenTableService.get_gen_table_list_service(auth, search)
    log.info('获取数据集表列表成功')
    return SuccessResponse(data=result, msg="获取数据集表列表成功")


@DatasetRouter.get('/{table_id}', summary="获取数据集表详情", description="获取数据集表详情")
async def query_detail_gen_table_controller(
    table_id: int = Path(..., description="表ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_dataset:dataset:query"]))
) -> JSONResponse:
    """
    获取数据集表详情
    
    参数:
    - table_id (int): 表ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含数据集表列信息的JSON响应
    """
    result = await GenTableColumnService.get_gen_table_column_list_by_table_id_service(auth, table_id)
    log.info(f'获取table_id为{table_id}的信息成功')
    return SuccessResponse(data=result, msg="获取数据集表详情成功")


@DatasetRouter.get('/{table_id}/data', summary="获取数据集表数据", description="获取数据集表数据")
async def get_meta_table_data_controller(
    request: Request,
    page: PaginationQueryParam = Depends(),
    table_id: int = Path(..., description="表ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_dataset:dataset:query"]))
) -> JSONResponse:
    """
    获取数据集表数据
    
    参数:
    - request (Request): 请求对象
    - table_id (int): 表ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含数据集表数据的JSON响应
    """
    args = dict(request.query_params)

    gen_table = await GenTableService.get_gen_table_by_id_service(auth, table_id)
    gen_columns = await GenTableColumnService.get_gen_table_column_list_by_table_id_service(auth, table_id)

    result = await DatasetService.get_dataset_list_service(
        auth=auth, 
        page=page,
        args=args, 
        table_name=gen_table.table_name, 
        columns=gen_columns
    )
    
    log.info(f'获取table_id为{table_id}的数据成功')
    return SuccessResponse(data=result, msg="获取数据集表数据成功")


@DatasetRouter.get('/{table_id}/export', summary="导出数据集表数据", description="导出数据集表数据")
async def export_meta_table_data_controller(
    request: Request,
    table_id: int = Path(..., description="表ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_dataset:dataset:export"])),
    redis: Redis = Depends(redis_getter)
) -> StreamingResponse:
    """
    导出数据集表数据
    
    参数:
    - request (Request): 请求对象
    - table_id (int): 表ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - StreamingResponse: 包含导出数据的Excel文件流响应
    """
    args = dict(request.query_params)

    gen_table = await GenTableService.get_gen_table_by_id_service(auth, table_id)
    gen_columns = await GenTableColumnService.get_gen_table_column_list_by_table_id_service(auth, table_id)

    # 获取相关字典
    dict_map = {}
    dict_types = {col.get('dict_type') for col in gen_columns if col.get('dict_type')}
    
    # 批量获取字典数据
    for dict_type in dict_types:
        if not dict_type:
            continue
        dict_data = await DictDataService.get_init_dict_service(redis=redis, dict_type=dict_type)
        dict_map[dict_type] = dict_data

    # 导出数据
    export_result = await DatasetService.export_dataset_list_service(
        auth=auth, 
        args=args, 
        table_name=gen_table.table_name, 
        columns=gen_columns, 
        dict_map=dict_map
    )

    # 返回导出结果
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f'attachment; filename={urllib.parse.quote(gen_table.table_name)}.xlsx'
        }
    )