# -*- coding: utf-8 -*-

import json
from typing import Any

from app.core.exceptions import CustomException
from app.core.base_params import PaginationQueryParam
from app.core.logger import log

from app.api.v1.module_system.auth.schema import AuthSchema
from app.client.openai.client import ai_client
from app.client.langfuse.client import langfuse
from app.utils.prompt_util import PromptUtil

from .schema import (
    PromptCreateSchema, 
    PromptUpdateSchema, 
    PromptOutSchema, 
    PromptQueryParam,
    PromptVersionOutSchema
)
from .crud import PromptCRUD, PromptVersionCRUD


class PromptService:
    """
    提示词管理模块服务层
    """
    
    @classmethod
    async def detail_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - id (int): 提示词ID
        
        返回:
        - dict: 提示词模型实例字典
        """
        obj = await PromptCRUD(auth).get_by_id_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return PromptOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def list_service(cls, auth: AuthSchema, search: PromptQueryParam | None = None, order_by: list[dict[str, str]] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - search (PromptQueryParam | None): 查询参数
        - order_by (list[dict[str, str]] | None): 排序参数
        
        返回:
        - list[dict]: 提示词模型实例字典列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await PromptCRUD(auth).list_crud(search=search_dict, order_by=order_by)
        return [PromptOutSchema.model_validate(obj).model_dump() for obj in obj_list]
    
    @classmethod
    async def page_service(cls, auth: AuthSchema, page: PaginationQueryParam, search: PromptQueryParam | None = None) -> dict:
        """
        分页查询
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - page (PaginationQueryParam): 分页查询参数模型
        - search (PromptQueryParam | None): 查询参数
        
        返回:
        - dict: 分页数据
        """
        search_dict = search.__dict__ if search else {}
        
        return await PromptCRUD(auth).page_crud(
            page=page,
            search=search_dict
        )
    
    @classmethod
    async def create_service(cls, auth: AuthSchema, data: PromptCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - data (PromptCreateSchema): 提示词创建模型
        
        返回:
        - dict: 提示词模型实例字典
        """
        # 检查编码是否重复
        exist_obj = await PromptCRUD(auth).get_by_code(code=data.prompt_code)
        if exist_obj:
            raise CustomException(msg='创建失败，提示词编码已存在')

        # 检查标题是否重复
        exist_title_obj = await PromptCRUD(auth).get(prompt_title=data.prompt_title)
        if exist_title_obj:
            raise CustomException(msg='创建失败，提示词标题已存在')
            
        obj = await PromptCRUD(auth).create_crud(data=data)
        return PromptOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def update_service(cls, auth: AuthSchema, id: int, data: PromptUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - id (int): 提示词ID
        - data (PromptUpdateSchema): 提示词更新模型
        
        返回:
        - dict: 提示词模型实例字典
        """
        # 检查数据是否存在
        obj = await PromptCRUD(auth).get_by_id_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')
        
        # 检查编码是否重复
        exist_obj = await PromptCRUD(auth).get_by_code(code=data.prompt_code)
        if exist_obj and exist_obj.id != id:
            raise CustomException(msg='更新失败，提示词编码重复')

        # 检查标题是否重复
        exist_title_obj = await PromptCRUD(auth).get(prompt_title=data.prompt_title)
        if exist_title_obj and exist_title_obj.id != id:
            raise CustomException(msg='更新失败，提示词标题重复')
            
        obj = await PromptCRUD(auth).update_crud(id=id, data=data)
        return PromptOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def delete_service(cls, auth: AuthSchema, ids: list[int]) -> None:
        """
        删除
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - ids (list[int]): 提示词ID列表
        
        返回:
        - None
        """
        if len(ids) < 1:
            raise CustomException(msg='删除失败，删除对象不能为空')
        
        # 检查所有要删除的数据是否存在
        for id in ids:
            obj = await PromptCRUD(auth).get_by_id_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
                
        await PromptCRUD(auth).delete_crud(ids=ids)

    @classmethod
    async def get_version_list_service(cls, auth: AuthSchema, prompt_id: int) -> list[dict]:
        """
        获取版本列表
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - prompt_id (int): 提示词ID
        
        返回:
        - list[dict]: 版本列表
        """
        obj_list = await PromptVersionCRUD(auth).get_list_by_prompt_id(prompt_id=prompt_id)
        return [PromptVersionOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def rollback_service(cls, auth: AuthSchema, prompt_id: int, version_id: int) -> None:
        """
        回滚版本
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - prompt_id (int): 提示词ID
        - version_id (int): 版本ID
        
        返回:
        - None
        """
        prompt_crud = PromptCRUD(auth)
        version_crud = PromptVersionCRUD(auth)
        
        prompt = await prompt_crud.get_by_id_crud(id=prompt_id)
        if not prompt:
            raise CustomException(msg='回滚失败，提示词不存在')
            
        version = await version_crud.get(id=version_id)
        if not version:
            raise CustomException(msg='回滚失败，版本不存在')
            
        if version.prompt_id != prompt_id:
            raise CustomException(msg='回滚失败，版本不属于该提示词')

        # 更新主表内容（不创建新版本，而是恢复到旧版本状态）
        update_data = {
            "content": version.content,
            "ability_tags": version.ability_tags,
            "version_id": version.id
        }
        
        # 使用基类 update 方法，避开 PromptCRUD.update_crud 的自动版本逻辑
        await prompt_crud.update(id=prompt_id, data=update_data)
        
        # 处理版本归档
        await version_crud.rollback_version(prompt_id=prompt_id, target_version_id=version_id)

    @classmethod
    async def push_to_production_service(cls, auth: AuthSchema, id: int) -> None:
        """
        推送到生产环境
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - id (int): 提示词ID
        
        返回:
        - None
        """
        prompt_crud = PromptCRUD(auth)
        prompt = await prompt_crud.get_by_id_crud(id=id)
        if not prompt:
            raise CustomException(msg='推送失败，提示词不存在')
            
        if not langfuse:
            raise CustomException(msg="Langfuse 客户端未启用，无法推送提示词")
            
        try:
            langfuse.create_prompt(
                name=prompt.prompt_code,
                type="text",
                prompt=prompt.content,
                labels=["production"]
            )
            # 更新发布状态
            await prompt_crud.set_publish_status(id=id, is_publish=1)
        except Exception as e:
            log.error(f'推送提示词失败: {e}')
            raise CustomException(msg=f'推送失败: {str(e)}')

    @staticmethod
    async def evaluate_prompt(prompt: str) -> dict:
        """
        评估提示词
        
        参数:
        - prompt (str): 待评估提示词
        
        返回:
        - dict: 评估结果
        """
        prompt_evaluator = PromptUtil.get_prompt_evaluator()
        
        messages = [
            {"role": "system", "content": prompt_evaluator},
            {"role": "user", "content": f"待评估提示词: ```{prompt}```，请基于上述信息对该提示词进行评估"}
        ]

        try:
            return await ai_client.achat(messages, json_format=True)
        except Exception as e:
            log.error(f"评估提示词失败: {e}")
            return {}

    @staticmethod
    async def optimize_prompt_with_suggestions(model: str, original_content: str, suggestions: list):
        """
        优化提示词（流式）
        
        参数:
        - model (str): 模型名称
        - original_content (str): 原始提示词
        - suggestions (list): 改进建议
        """
        suggestions_text = "\n".join([f"- {suggestion}" for suggestion in suggestions])
        prompt_optimizer = PromptUtil.get_prompt_optimizer()
        
        messages = [
            {"role": "system", "content": prompt_optimizer},
            {"role": "user", "content": f"""
              原始提示词：
              ```
              {original_content}
              ```

              改进建议：
              ```
              {suggestions_text}
              ```

              请根据以上建议优化原始提示词，确保输出符合提示词工程的最佳实践。
              """
            }
        ]

        async for chunk in ai_client.achat_stream(messages, model=model):
            yield f"data: {chunk.model_dump_json()}\n\n"
