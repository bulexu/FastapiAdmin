# -*- coding: utf-8 -*-

from sqlalchemy import String, Integer, Text, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.base_model import ModelMixin, UserMixin


class PromptModel(ModelMixin, UserMixin):
    """
    AI助手提示词表
    """
    __tablename__: str = 'prompt'
    __table_args__: dict[str, str] = ({'comment': 'AI助手提示词表'})
    __loader_options__: list[str] = ["created_by", "updated_by", "current_version"]

    prompt_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment='提示词编码')
    prompt_title: Mapped[str] = mapped_column(String(100), nullable=False, comment='提示词标题')
    version_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment='当前版本ID')
    content: Mapped[str] = mapped_column(Text, nullable=False, comment='提示词内容')
    ability_tags: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True, comment='能力标签')
    evaluate_result: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True, comment='提示词评估结果')
    is_publish: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='是否发布（0否 1是）')

    # 关系定义：当前版本
    current_version: Mapped["PromptVersionModel"] = relationship(
        "PromptVersionModel",
        foreign_keys=[version_id],
        primaryjoin="PromptModel.version_id == PromptVersionModel.id",
        uselist=False,
        lazy="joined"
    )

    # 关系定义：所有版本
    versions: Mapped[list["PromptVersionModel"]] = relationship(
        "PromptVersionModel",
        back_populates="prompt",
        order_by="desc(PromptVersionModel.created_time)",
        foreign_keys="[PromptVersionModel.prompt_id]"
    )


class PromptVersionModel(ModelMixin, UserMixin):
    """
    AI助手提示词版本表
    """
    __tablename__: str = 'prompt_version'
    __table_args__: dict[str, str] = ({'comment': 'AI助手提示词版本表'})
    __loader_options__: list[str] = ["created_by", "updated_by"]

    prompt_id: Mapped[int] = mapped_column(Integer, ForeignKey('prompt.id'), nullable=False, comment='提示词ID')
    version: Mapped[int] = mapped_column(Integer, nullable=False, comment='版本号')
    content: Mapped[str] = mapped_column(Text, nullable=False, comment='提示词内容')
    ability_tags: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True, comment='能力标签')
    is_archived: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='是否归档（0否 1是）')

    # 关系定义：所属提示词
    prompt: Mapped["PromptModel"] = relationship(
        "PromptModel", 
        back_populates="versions", 
        foreign_keys=[prompt_id]
    )
