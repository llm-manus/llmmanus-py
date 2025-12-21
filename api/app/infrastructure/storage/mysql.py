#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/23 18:08
#Author  :Emcikem
@File    :mysql.py
"""
import logging
from functools import lru_cache
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

logger = logging.getLogger(__name__)


class Mysql:
    """MySQL数据库基类，用于完成数据库连接等配置操作"""

    def __init__(self):
        """构造函数，完成MySQL数据库引擎、会话工厂的创建"""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._settings = get_settings()

    async def init(self) -> None:
        """初始化MySQL连接"""
        # 1.判断是否已经创建好引擎，如果连上则中断程序
        if self._engine is not None:
            logger.warning(f"MySQL引擎已经初始化，无需重复初始化")
            return

        try:
            # 2.创建异步引擎
            logger.info("正在初始化MySQL连接...")
            self._engine = create_async_engine(
                self._settings.sqlalchemy_database_uri,
                echo=True if self._settings.env == "development" else False,
            )

            # 3.创建会话工厂
            self._session_factory = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
            logger.info("MySQL会话工厂创建完成")

            # 4.连接MySQL并执行预操作
            async with self._engine.begin() as async_conn:
                # 5.检查是否安装了uuid扩展，如果没有的话则安装
                await async_conn.execute(text("SELECT DATABASE()"))
                logger.info("成功连接MySQL")
        except Exception as e:
            logger.error(f"连接MySQL失败：{str(e)}")
            raise

    async def shutdown(self) -> None:
        """关闭MySQL连接"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("成功关闭MySQL连接")

        get_mysql.cache_clear()

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """只读属性，返回已初始化的会话工厂"""
        if self._session_factory is None:
            raise RuntimeError("MySQL未初始化，请先调用init()函数初始化")
        return self._session_factory


@lru_cache()
def get_mysql() -> Mysql:
    """使用lru_cache实现单例模式，获取MySQL实例"""
    return Mysql()


async def get_db_session() -> AsyncSession:
    """FastAPI依赖项，用于在每个请求中异步获取数据库会话实例，确保会话在正确使用后背关闭"""
    # 1.获取引擎和会话工厂
    db = get_mysql()
    session_factory = db.session_factory

    # 2.创建会话上下文，在上下文内完成数据提交
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as _:
            await session.rollback()
            raise
