#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/2/1 21:26
#Author  :Emcikem
@File    :middleware.py
"""
import logging

from starlette.requests import Request

from app.core.config import get_settings
from app.interfaces.service_dependencies import get_supervisor_service


async def auto_extend_time_middleware(request: Request, call_next):
    """使用中间件延长每次API请求是否超时摧毁时间"""
    # 1.获取系统配置与supervisor服务
    settings = get_settings()
    supervisor_service = get_supervisor_service()

    # 2.判断逻辑，仅在符合条件时延长超时摧毁时间3分钟
    ignore_paths = (
        "/api/supervisor/activate-timeout",
        "/api/supervisor/extend-timeout",
        "/api/supervisor/cancel-timeout",
        "/api/supervisor/timeout-status",
    )
    if (
            settings.server_timeout_minutes is not None
            and supervisor_service.timeout_active
            and request.url.path.startswith("/api/")
            and not request.url.path.startswith(ignore_paths)
            and supervisor_service.expand_enabled
    ):
        try:
            await supervisor_service.extend_timeout(3)
            logging.debug("调用API调用而自动延长超时摧毁时长：%s", request.url)
        except Exception as e:
            logging.warning("自动延长超时失败：%s", {str(e)})

    response = await call_next(request)
    return response
