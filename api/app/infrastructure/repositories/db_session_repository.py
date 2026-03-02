#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/2 23:42
#Author  :Emcikem
@File    :db_session_repository.py
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_extensions.uuid7 import timestamp_ns

from app.domain.models.message import Message
from app.domain.models.session import Session
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.models import SessionModel


class DBSessionRepository(SessionRepository):
    """基于MySQL数据库的会话仓库"""

    def __init__(self, db_session: AsyncSession) -> None:
        """构造函数，完成数据库会话初始化"""
        self.db_session = db_session


    async def save(self, session: Session) -> None:
        """根据传递的领域模型更新或新增会话"""
        # 1.根据id查询会话是否存在
        stmt = select(SessionModel).where(SessionModel.id == session.id)
        result = await self.db_session.execute(stmt)
        record = result.scalar_one_or_none()

        # 2.如果会话不存在则新建会话
        if not record:
            record = SessionModel.from_domain(session)
            self.db_session.add(record)
            return

        # 3.会话存在则更新会话
        record.update_from_domain(session)

    async def get_all(self) -> List[Session]:
        """获取所有会话列表"""
        # 1.构建sql查询所有记录
        stmt = select(SessionModel).order_by(SessionModel.latest_message_at.desc())
        result = await self.db_session.execute(stmt)
        records = result.scalars().all()

        # 2.将数据循环读取转换成Domain模型
        return [record.to_domain() for record in records]

    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """根据会话id获取会话数据"""
        # 1.构建sql查询数据是否存在
        stmt = select(SessionModel).where(SessionModel.id == session_id)
        result = await self.db_session.execute(stmt)
        record = result.scalar_one_or_none()

        # 2.判断会话记录是否存在并返回
        return record.to_domain() if record is not None else None

    async def delete_by_id(self, session_id: str) -> None:
        """根据会话id删除会话"""
        # 1.构建sql删除数据
        stmt = delete(SessionModel).where(SessionModel.id == session_id)

        # 2.执行sql同时无需检查是否删除成功
        await self.db_session.execute(stmt)

    async def update_title(self, session_id: str, title: str) -> None:
        """更新会话标题"""
        # 1.构建sql更新会话并执行
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(title=title)
        )
        result = await self.db_session.execute(stmt)

        # 2.检查是否更新成功
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")

    async def update_latest_message(self, session_id: str, message: Message, timestamp: datetime) -> None:
        """更新会话最新消息"""
        # 1.构建sql更新会话消息并执行
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(
                last_message=message,
                last_message_at=timestamp,
            )
        )
        result = await self.db_session.execute(stmt)

        # 2.检查是否更新成功
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")

    async def update_status(self, session_id: str, status: SessionStatus) -> None:
        """更新会话状态"""
        # 1.构建sql更新会话消息并执行
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(status=status.value)
        )
        result = await self.db_session.execute(stmt)

        # 2.检查是否更新成功
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")

    async def update_unread_message_count(self, session_id: str, count: int) -> None:
        """更新会话的未读消息数"""
        # 1.构建sql更新会话消息并执行
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(unread_message_count=count)
        )
        result = await self.db_session.execute(stmt)

        # 2.检查是否更新成功
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")
