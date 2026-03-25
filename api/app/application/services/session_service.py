#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/24 21:46
#Author  :Emcikem
@File    :session_service.py
"""
import logging

from app.domain.models.session import Session
from app.domain.repositories.session_repository import SessionRepository

logging = logging.getLogger(__name__)

class SessionService:
    """会话服务"""

    def __init__(self, session_repository: SessionRepository) -> None:
        """构造函数，完成会话服务初始化"""
        self._session_repository = session_repository

    async def create_session(self) -> Session:
        """创建一个空白的新任务会话"""
        logging.info(f"创建一个空白新任务会话")
        session = Session(title="新对话")
        await self._session_repository.save(session)
        logging.info(f"成功创建一个新任务会话:{session.id}")
        return session