# -*- coding: utf-8 -*-

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse, StreamingResponse

from app.common.response import SuccessResponse
from app.core.router_class import OperationLogRoute
from app.core.base_params import PaginationQueryParam
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.api.v1.module_system.auth.schema import AuthSchema
from .service import PromptService
from .schema import (
    PromptCreateSchema,
    PromptUpdateSchema,
    PromptQueryParam
)


PromptRouter = APIRouter(route_class=OperationLogRoute, prefix="/prompt", tags=["提示词模块"])

@PromptRouter.get("/detail/{id}", summary="获取提示词详情", description="获取提示词详情")
async def get_obj_detail_controller(
    id: int = Path(..., description="提示词ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:query"]))
) -> JSONResponse:
    """
    获取提示词详情
    
    参数:
    - id (int): 提示词ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含提示词详情的JSON响应
    """
    result_dict = await PromptService.detail_service(id=id, auth=auth)
    log.info(f"获取提示词详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取提示词详情成功")

@PromptRouter.get("/page", summary="查询提示词列表", description="查询提示词列表")
async def get_obj_page_controller(
    page: PaginationQueryParam = Depends(),
    search: PromptQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:query"]))
) -> JSONResponse:
    """
    查询提示词列表
    
    参数:
    - page (PaginationQueryParam): 分页查询参数
    - search (PromptQueryParam): 查询参数
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含提示词列表分页信息的JSON响应
    """
    result_dict = await PromptService.page_service(
        auth=auth, 
        page=page, 
        search=search, 
    )
    log.info("查询提示词列表成功")
    return SuccessResponse(data=result_dict, msg="查询提示词列表成功")

@PromptRouter.post("/create", summary="创建提示词", description="创建提示词")
async def create_obj_controller(
    data: PromptCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:create"]))
) -> JSONResponse:
    """
    创建提示词
    
    参数:
    - data (PromptCreateSchema): 提示词创建模型
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含创建提示词详情的JSON响应
    """
    result_dict = await PromptService.create_service(auth=auth, data=data)
    log.info(f"创建提示词成功: {result_dict.get('prompt_title')}")
    return SuccessResponse(data=result_dict, msg="创建提示词成功")

@PromptRouter.put("/update/{id}", summary="修改提示词", description="修改提示词")
async def update_obj_controller(
    data: PromptUpdateSchema,
    id: int = Path(..., description="提示词ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:update"]))
) -> JSONResponse:
    """
    修改提示词
    
    参数:
    - data (PromptUpdateSchema): 提示词更新模型
    - id (int): 提示词ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含修改提示词详情的JSON响应
    """
    result_dict = await PromptService.update_service(auth=auth, id=id, data=data)
    log.info(f"修改提示词成功: {result_dict.get('prompt_title')}")
    return SuccessResponse(data=result_dict, msg="修改提示词成功")

@PromptRouter.delete("/delete", summary="删除提示词", description="删除提示词")
async def delete_obj_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:delete"]))
) -> JSONResponse:
    """
    删除提示词
    
    参数:
    - ids (list[int]): 提示词ID列表
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含删除提示词详情的JSON响应
    """
    await PromptService.delete_service(auth=auth, ids=ids)
    log.info(f"删除提示词成功: {ids}")
    return SuccessResponse(msg="删除提示词成功")

@PromptRouter.get("/{prompt_id}/versions", summary="获取提示词版本列表", description="获取提示词版本列表")
async def get_version_list_controller(
    prompt_id: int = Path(..., description="提示词ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:query"]))
) -> JSONResponse:
    """
    获取提示词版本列表
    
    参数:
    - prompt_id (int): 提示词ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 包含提示词版本列表的JSON响应
    """
    result_list = await PromptService.get_version_list_service(auth=auth, prompt_id=prompt_id)
    log.info(f"获取提示词版本列表成功: {prompt_id}")
    return SuccessResponse(data=result_list, msg="获取提示词版本列表成功")

@PromptRouter.post("/{prompt_id}/rollback/{version_id}", summary="回滚提示词版本", description="回滚提示词版本")
async def rollback_version_controller(
    prompt_id: int = Path(..., description="提示词ID"),
    version_id: int = Path(..., description="版本ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:rollback"]))
) -> JSONResponse:
    """
    回滚提示词版本
    
    参数:
    - prompt_id (int): 提示词ID
    - version_id (int): 版本ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 回滚结果
    """
    await PromptService.rollback_service(auth=auth, prompt_id=prompt_id, version_id=version_id)
    log.info(f"回滚提示词版本成功: {prompt_id} -> {version_id}")
    return SuccessResponse(msg="回滚提示词版本成功")

@PromptRouter.post("/push/{id}", summary="推送提示词到生产环境", description="推送提示词到生产环境")
async def push_to_production_controller(
    id: int = Path(..., description="提示词ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:push"]))
) -> JSONResponse:
    """
    推送提示词到生产环境
    
    参数:
    - id (int): 提示词ID
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 推送结果
    """
    await PromptService.push_to_production_service(auth=auth, id=id)
    log.info(f"推送提示词到生产环境成功: {id}")
    return SuccessResponse(msg="推送提示词到生产环境成功")

@PromptRouter.post("/evaluate", summary="评估提示词", description="评估提示词")
async def evaluate_prompt_controller(
    prompt: str = Body(..., embed=True, description="待评估提示词"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:evaluate"]))
) -> JSONResponse:
    """
    评估提示词
    
    参数:
    - prompt (str): 待评估提示词
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - JSONResponse: 评估结果
    """
    result = await PromptService.evaluate_prompt(prompt=prompt)
    return SuccessResponse(data=result, msg="评估提示词成功")

@PromptRouter.post("/optimize", summary="优化提示词", description="优化提示词")
async def optimize_prompt_controller(
    model: str = Body(..., description="模型名称"),
    original_content: str = Body(..., description="原始提示词"),
    suggestions: list = Body(..., description="改进建议"),
    auth: AuthSchema = Depends(AuthPermission(["module_application:prompt:optimize"]))
) -> StreamingResponse:
    """
    优化提示词
    
    参数:
    - model (str): 模型名称
    - original_content (str): 原始提示词
    - suggestions (list): 改进建议
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - StreamingResponse: 优化提示词流
    """
    return StreamingResponse(
        PromptService.optimize_prompt_with_suggestions(model=model, original_content=original_content, suggestions=suggestions),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
