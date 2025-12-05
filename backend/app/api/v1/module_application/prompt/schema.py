# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field, field_validator
from fastapi import Query

from app.core.validator import DateTimeStr
from app.core.base_schema import BaseSchema, UserBySchema


class PromptCreateSchema(BaseModel):
    """新增模型"""
    prompt_code: str = Field(..., max_length=255, description='提示词编码')
    prompt_title: str = Field(..., max_length=100, description='提示词标题')
    content: str = Field(..., max_length=5000, description='提示词内容')
    ability_tags: list[str] | None = Field(default=None, description='能力标签')
    evaluate_result: dict | None = Field(default=None, description='提示词评估结果')
    is_publish: int = Field(default=0, description='是否发布（0否 1是）')
    description: str | None = Field(default=None, max_length=500, description="备注")

    @field_validator('prompt_code', 'prompt_title', 'content')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """验证字段不为空"""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError('字段不能为空')
        return v


class PromptUpdateSchema(PromptCreateSchema):
    """更新模型"""
    pass


class PromptOutSchema(PromptCreateSchema, BaseSchema, UserBySchema):
    """响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    version_id: int | None = Field(default=None, description='当前版本ID')


class PromptQueryParam:
    """提示词查询参数"""

    def __init__(
        self,
        prompt_title: str | None = Query(None, description="提示词标题"),
        prompt_code: str | None = Query(None, description="提示词编码"),
        is_publish: int | None = Query(None, description="是否发布"),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", example=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", example=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        created_id: int | None = Query(None, description="创建人"),
        updated_id: int | None = Query(None, description="更新人"),
    ) -> None:
        
        # 模糊查询字段
        self.prompt_title = ("like", prompt_title)
        self.prompt_code = ("like", prompt_code)

        # 精确查询字段
        self.is_publish = is_publish
        self.created_id = created_id
        self.updated_id = updated_id

        # 时间范围查询
        if created_time and len(created_time) == 2:
            self.created_time = ("between", (created_time[0], created_time[1]))
        if updated_time and len(updated_time) == 2:
            self.updated_time = ("between", (updated_time[0], updated_time[1]))


class PromptVersionCreateSchema(BaseModel):
    """版本新增模型"""
    prompt_id: int = Field(..., description='提示词ID')
    version: int = Field(..., description='版本号')
    content: str = Field(..., description='提示词内容')
    ability_tags: list[str] | None = Field(default=None, description='能力标签')
    is_archived: int = Field(default=0, description='是否归档（0否 1是）')
    description: str | None = Field(default=None, max_length=500, description="备注")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('提示词内容不能为空')
        return v


class PromptVersionOutSchema(PromptVersionCreateSchema, BaseSchema, UserBySchema):
    """版本响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    version: int = Field(..., description='版本号')
