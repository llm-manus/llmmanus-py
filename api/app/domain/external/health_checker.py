#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/30 15:04
#Author  :Emcikem
@File    :health_checker.py
"""
from typing import Protocol

from app.domain.models.health_status import HealthStatus


class HealthChecker(Protocol):
    """服务健康检查协议"""

    async def check(self) -> HealthStatus:
        """用于检查对应的服务是否健康"""
        ...
