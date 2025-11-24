#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/23 20:25
#Author  :Emcikem
@File    :status_router.py
"""
import logging

from fastapi import APIRouter

from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["状态模块"])


@router.get(
    path="",
    response_model=Response,
    summary="系统健康检查",
    description="检查系统的MySQL，Redis，FastAPI等组件的状态信息"
)
async def get_status():
    """系统健康检查，检查MySQL/Redis/cos等服务"""
    # todo：等待mysql/redis等服务接入后补全代码
    return Response.success()
