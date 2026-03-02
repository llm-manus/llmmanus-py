#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/2 23:46
#Author  :Emcikem
@File    :repository_dependencies.py
"""
import logging
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.db_session_repository import DBSessionRepository
from app.infrastructure.storage.mysql import get_db_session

logger = logging.getLogger(__name__)

@lru_cache()
def get_db_session_repository(
        db_session: AsyncSession = Depends(get_db_session),
) -> DBSessionRepository:
    """基于数据库的会话数据仓库"""
    logger.info("加载获取DBSessionRepository")
    return DBSessionRepository(db_session=db_session)