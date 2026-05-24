#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/5/24 15:35
#Author  :Emcikem
@File    :db_uow.py
"""
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.domain.repositories.uow import IUnitOfWork, T
from .db_file_repository import DBFileRepository
from .db_session_repository import DBSessionRepository

class DBUnitOfWork(IUnitOfWork):
    """基于MySQL数据库的UoW实例"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """构造函数，完成UoW类初始化"""
        self.session_factory = session_factory
        self.db_session: Optional[AsyncSession] = None

    async def commit(self):
        """提交数据库持久化"""
        await self.db_session.commit()

    async def rollback(self):
        """数据库回退操作"""
        await self.db_session.rollback()

    async def __aenter__(self) -> "DBUnitOfWork":
        """进入UoW操作上下文管理器的逻辑"""
        # 1.为每个上下文开启一个新的会话
        self.db_session = self.session_factory()

        # 2.初始化所有数据仓库
        self.file = DBFileRepository(db_session=self.db_session)
        self.session = DBSessionRepository(db_session=self.db_session)

        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时执行的逻辑，如果出现异常则回滚，否则提交"""
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.db_session.close()