#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/30 15:17
#Author  :Emcikem
@File    :mysql_health_checker.py
"""
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus

logger = logging.getLogger(__name__)


class MysqlHealthChecker(HealthChecker):
    """MySQL健康检查器"""

    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def check(self) -> HealthStatus:
        """执行一段简单的sql，用于判断数据库服务是否正常"""
        try:
            await self._db_session.execute(text("select 1"))
            return HealthStatus(service="mysql", status="ok")
        except Exception as e:
            logger.error(f"MySQL健康检查失败：{str(e)}")
            return HealthStatus(
                service="mysql",
                status="error",
                details=str(e),
            )
