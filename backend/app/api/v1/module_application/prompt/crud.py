# -*- coding: utf-8 -*-

from collections.abc import Sequence
from sqlalchemy import select, update, func
from app.core.base_crud import CRUDBase
from app.core.base_params import PaginationQueryParam

from app.api.v1.module_system.auth.schema import AuthSchema
from .model import PromptModel, PromptVersionModel
from .schema import PromptCreateSchema, PromptUpdateSchema, PromptOutSchema, PromptVersionCreateSchema, PromptVersionOutSchema


class PromptCRUD(CRUDBase[PromptModel, PromptCreateSchema, PromptUpdateSchema]):
    """提示词数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=PromptModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: list[str] | None = None) -> PromptModel | None:
        return await self.get(id=id, preload=preload)
    
    async def list_crud(self, search: dict | None = None, order_by: list[dict] | None = None, preload: list[str] | None = None) -> Sequence[PromptModel]:
        return await self.list(search=search, order_by=order_by, preload=preload)
    
    async def create_crud(self, data: PromptCreateSchema) -> PromptModel | None:
        """创建提示词并自动创建初始版本"""
        # 1. 创建提示词主表记录
        prompt = await self.create(data=data)
        if not prompt:
            return None
            
        # 2. 创建初始版本
        version_data = PromptVersionCreateSchema(
            prompt_id=prompt.id,
            version=1,
            content=data.content,
            ability_tags=data.ability_tags,
            description=data.description
        )
        version_crud = PromptVersionCRUD(self.auth)
        version = await version_crud.create_crud(version_data)
        
        # 3. 更新主表的当前版本ID
        if version:
            await self.update(id=prompt.id, data={"version_id": version.id})
            # 重新获取以包含更新后的version_id
            return await self.get(id=prompt.id)
            
        return prompt
    
    async def update_crud(self, id: int, data: PromptUpdateSchema) -> PromptModel | None:
        """更新提示词并创建新版本"""
        # 1. 更新主表信息
        prompt = await self.update(id=id, data=data)
        if not prompt:
            return None
            
        # 2. 获取当前最大版本号
        version_crud = PromptVersionCRUD(self.auth)
        max_version = await version_crud.get_max_version(prompt_id=id)
        
        # 3. 创建新版本
        version_data = PromptVersionCreateSchema(
            prompt_id=id,
            version=max_version + 1,
            content=data.content,
            ability_tags=data.ability_tags,
            description=data.description
        )
        version = await version_crud.create_crud(version_data)
        
        # 4. 更新主表的当前版本ID
        if version:
            await self.update(id=id, data={"version_id": version.id})
            return await self.get(id=id)
            
        return prompt
    
    async def delete_crud(self, ids: list[int]) -> None:
        return await self.delete(ids=ids)
    
    async def page_crud(self, page: PaginationQueryParam, search: dict | None = None, preload: list | None = None) -> dict:
        return await self.page(
            page=page,
            search=search or {},
            out_schema=PromptOutSchema,
            preload=preload
        )

    async def get_by_code(self, code: str) -> PromptModel | None:
        """根据编码获取提示词"""
        stmt = select(self.model).where(self.model.prompt_code == code)
        result = await self.auth.db.execute(stmt)
        return result.scalars().first()

    async def set_publish_status(self, id: int, is_publish: int) -> None:
        """设置发布状态"""
        await self.update(id=id, data={"is_publish": is_publish})


class PromptVersionCRUD(CRUDBase[PromptVersionModel, PromptVersionCreateSchema, PromptVersionCreateSchema]):
    """提示词版本数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=PromptVersionModel, auth=auth)

    async def create_crud(self, data: PromptVersionCreateSchema) -> PromptVersionModel | None:
        return await self.create(data=data)

    async def get_list_by_prompt_id(self, prompt_id: int) -> Sequence[PromptVersionModel]:
        """获取指定提示词的所有版本"""
        stmt = select(self.model).where(
            self.model.prompt_id == prompt_id,
            self.model.is_archived == 0
        ).order_by(self.model.version.desc())
        result = await self.auth.db.execute(stmt)
        return result.scalars().all()

    async def get_max_version(self, prompt_id: int) -> int:
        """获取指定提示词的最大版本号"""
        stmt = select(func.max(self.model.version)).where(self.model.prompt_id == prompt_id)
        result = await self.auth.db.execute(stmt)
        return result.scalar() or 0

    async def rollback_version(self, prompt_id: int, target_version_id: int) -> None:
        """回滚版本"""
        # 获取目标版本信息
        target_version = await self.get(id=target_version_id)
        if not target_version:
            return

        # 将大于目标版本的版本标记为归档
        stmt = update(self.model).where(
            self.model.prompt_id == prompt_id,
            self.model.version > target_version.version
        ).values(is_archived=1)
        await self.auth.db.execute(stmt)

        # 将小于等于目标版本的版本标记为未归档
        stmt = update(self.model).where(
            self.model.prompt_id == prompt_id,
            self.model.version <= target_version.version
        ).values(is_archived=0)
        await self.auth.db.execute(stmt)
