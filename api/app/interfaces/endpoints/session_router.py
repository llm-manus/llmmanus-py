#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/24 21:34
#Author  :Emcikem
@File    :session_router.py
"""
from fastapi import APIRouter, Depends
import logging

from fastapi import APIRouter

from app.application.services.session_service import SessionService
from app.interfaces.schemas import Response
from app.interfaces.schemas.session import CreateSessionResponse
from app.interfaces.service_dependencies import get_session_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/session", tags=["会话模块"])

@router.post(
    path="",
    response_model=Response[CreateSessionResponse],
    summary="创建新任务会话",
    description="创建一个空白的新任务会话",
)
async def create_session(
    session_service: SessionService = Depends(get_session_service),
) -> Response[CreateSessionResponse]:
    """创建一个空白的新任务会话"""
    session = await session_service.create_session()
    return Response.success(
        msg="创建任务会话成功",
        data=CreateSessionResponse(session_id=session.id),
    )