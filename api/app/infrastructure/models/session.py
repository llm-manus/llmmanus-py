#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/2 21:42
#Author  :Emcikem
@File    :session.py
"""
import uuid
from datetime import datetime
from typing import Dict, List, Any

from sqlalchemy import (
    PrimaryKeyConstraint, String, text, Integer, Text, DateTime, JSON
)
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from ...domain.models.session import Session, SessionStatus


class SessionModel(Base):
    """会话ORM模型"""
    __tablename__ = 'session'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_session_id'),
    )

    id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    ) # 会话id
    sandbox_id: Mapped[str] = mapped_column(String(255), nullable=True) # 沙箱id
    task_id: Mapped[str] = mapped_column(String(255), nullable=True) # 任务id
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        server_default=text("''::character varying"),
    ) # 会话标题
    unread_message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    ) # 未读消息数
    latest_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("''::text"),
    ) # 最后一条消息
    latest_message_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
    ) # 最后一条消息时间
    events: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        server_default=text("'[]'"),
    ) # 事件类型
    files: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        server_default=text("'[]'"),
    ) # 文件
    memories: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        server_default=text("'{}'"),
    ) # 会话两个Agent的记忆
    status: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        server_default=text("''::character varying"),
    ) # 会话状态
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        onupdate=datetime.now,
        server_default=text("CURRENT_TIMESTAMP(0)"),
    ) # 更新时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
    )  # 创建时间

    @classmethod
    def from_domain(cls, session: Session) -> "SessionModel":
        """从会话领域模型构建ORM模型"""
        return cls(
            # 1.基础字段：使用BaseModel提供的python字典转换格式
            **session.model_dump(
                mode="python",
                exclude={"memories", "files", "events", "updated_at", "created_at"},
            ),
            # 2.复杂字段：使用BaseModel提供的json字典转换格式
            **session.model_dump(
                mode="json",
                include={"memories", "files", "events"},
            )
        )

    def to_domain(self) -> Session:
        """将会话ORM模型转换成领域模型（终极修复版）"""
        import json

        # 核心：专门处理你的场景 —— 列表里的字符串转对象
        def parse_json_list(value):
            # 如果是列表，遍历把每个字符串转成字典
            if isinstance(value, list):
                return [json.loads(item) if isinstance(item, str) else item for item in value]
            # 如果是字符串，整体转成列表
            if isinstance(value, str):
                return json.loads(value)
            return value

        def parse_json_dict(value):
            if isinstance(value, str):
                return json.loads(value)
            return value

        return Session(
            id=self.id,
            sandbox_id=self.sandbox_id,
            task_id=self.task_id,
            title=self.title,
            unread_message_count=self.unread_message_count,
            latest_message=self.latest_message,
            latest_message_at=self.latest_message_at,
            # 关键：这里会把 ["{...}", "{...}"] 变成 [{}, {}]
            events=parse_json_list(self.events),
            files=parse_json_list(self.files),
            memories=parse_json_dict(self.memories),
            status=SessionStatus(self.status),
            updated_at=self.updated_at,
            created_at=self.created_at,
        )

    def update_from_domain(self, session: Session) -> None:
        """从传递的领域模型更新ORM数据"""
        # 1.基础字段：Python模式
        base_data = session.model_dump(
            mode="python",
            exclude={"memories", "files", "events", "updated_at", "created_at"},
        )

        # 2.复杂字段：JSON模式
        json_data = session.model_dump(
            mode="json",
            include={"memories", "files", "events"},
        )

        # 3.合并更新
        for field, value in {**base_data, **json_data}.items():
            setattr(self, field, value)