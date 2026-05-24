#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/24 21:34
#Author  :Emcikem
@File    :session_router.py
"""
import asyncio
from datetime import datetime
from typing import Optional, Dict, AsyncGenerator

from fastapi import Depends
import logging

from fastapi import APIRouter
from sse_starlette import EventSourceResponse, ServerSentEvent

from app.application.errors.exception import NotFoundError
from app.application.services import session_service
from app.application.services.agent_service import AgentService
from app.application.services.session_service import SessionService
from app.interfaces.schemas import Response
from app.interfaces.schemas.event import EventMapper
from app.interfaces.schemas.session import CreateSessionResponse, ListSessionResponse, ListSessionItem, ChatRequest, \
    GetSessionResponse, GetSessionFilesResponse
from app.interfaces.service_dependencies import get_session_service, get_agent_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/session", tags=["会话模块"])

# 流式获取会话详情睡眠间隔
SESSION_SLEEP_INTERVAL = 5

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

@router.post(
    path="/stream",
    summary="流式获取所有会话基础信息列表",
    description="间隔指定时间流式获取所有会话基础信息列表",
)
async def stream_session(
        session_service: SessionService = Depends(get_session_service),
) -> EventSourceResponse:
    """间隔指定时间流式获取所有会话基础信息列表"""
    async def event_generator() -> AsyncGenerator[ServerSentEvent, None]:
        """定义一个异步迭代器，用于获取所有会话列表"""
        # 1.获取所有会话列表
        sessions = await session_service.get_all_sessions()

        # 2.循环遍历并组装数据
        session_items = [
            ListSessionItem(
                session_id=session.id,
                title=session.title,
                latest_message=session.latest_message,
                latest_message_at=session.latest_message_at,
                status=session.status,
                unread_message_count=session.unread_message_count,
            )
            for session in sessions
        ]

        # 3.将会话列表转换为流式事件数据并返回
        yield ServerSentEvent(
            event="sessions",
            data=ListSessionResponse(sessions=session_items).model_dump_json(),
        )

        # 4.睡眠制定事件避免高频返回
        await asyncio.sleep(SESSION_SLEEP_INTERVAL)

    return EventSourceResponse(event_generator())

@router.get(
    path="",
    response_model=Response[ListSessionResponse],
    summary="获取会话列表基础信息",
    description="获取Manus项目中所有任务会话基础信息列表"
)
async def get_all_session(
        session_service: SessionService = Depends(get_session_service),
) -> Response[ListSessionResponse]:
    """获取Manus项目中所有任务会话基础信息列表"""
    sessions = await session_service.get_all_sessions()
    session_items = [
        ListSessionItem(
            session_id=session.id,
            title=session.title,
            latest_message=session.latest_message,
            latest_message_at=session.latest_message_at,
            status=session.status,
            unread_message_count=session.unread_message_count,
        )
        for session in sessions
    ]
    return Response.success(
        msg="获取任务会话列表成功",
        data=ListSessionResponse(sessions=session_items),
    )

@router.post(
    path="/{session_id}/clear-unread-message-count",
    response_model=Response[Optional[Dict]],
    summary="清除指定任务会话未读消息数",
    description="清除指定任务会话未读消息数"
)
async def clear_unread_message_count(
        session_id: str,
        session_service: SessionService = Depends(get_session_service),
) -> Response[Optional[Dict]]:
    """根据传递的会话id清空未读消息数"""
    await session_service.clear_unread_message_count(session_id)
    return Response.success(msg="清除未读消息数成功")

@router.post(
    path="/{session_id}/delete",
    response_model=Response[Optional[Dict]],
    summary="删除指定任务会话",
    description="根据传递的会话id删除指定任务会话",
)
async def delete_session(
        session_id: str,
        session_service: SessionService = Depends(get_session_service),
) -> Response[Optional[Dict]]:
    """根据传递的会话id删除指定任务会话"""
    await session_service.delete_session(session_id)
    return Response.success(msg="删除任务会话成功")

@router.post(
    path="/{session_id}/chat",
    summary="向指定任务会话发起聊天请求",
    description="向指定任务会话发起聊天请求"
)
async def chat(
        session_id: str,
        request: ChatRequest,
        agent_service: AgentService = Depends(get_agent_service),
) -> EventSourceResponse:
    """根据传递的会议id+chat请求数据向指定会话发起聊天请求"""

    async def event_generator() -> AsyncGenerator[ServerSentEvent, None]:
        """定义事件生成器，用于配合EventSourceResponse生成流式响应数据"""
        # 1.调用Agent服务发起聊天
        async for event in agent_service.chat(
            session_id=session_id,
            message=request.message,
            attachments=request.attachments,
            latest_event_id=request.event_id,
            timestamp=datetime.fromtimestamp(request.timestamp) if request.timestamp else None,
        ):
            # 2.将Agent事件转换为sse数据（因为普通的event没法提供流式事件传输）
            sse_event = EventMapper.event_to_sse_event(event)
            if sse_event:
                yield ServerSentEvent(
                    event=sse_event.type,
                    data=sse_event.data.model_dump_json()
                )

    return EventSourceResponse(event_generator())

@router.get(
    path="/{session_id}",
    response_model=Response[GetSessionResponse],
    summary="获取指定会话详情信息",
    description="根据传递的会话id获取该会话的对话详情",
)
async def get_session(
        session_id: str,
        session_service: SessionService = Depends(get_session_service),
) -> Response[GetSessionResponse]:
    """传递指定会话id获取该会话的对话详情"""
    session = await session_service.get_session(session_id)
    if not session:
        raise NotFoundError("该会话不存在，请核实后重试")
    return Response.success(
        msg="获取会话详情成功",
        data=GetSessionResponse(
            session_id=session.id,
            title=session.title,
            status=session.status,
            events=EventMapper.events_to_sse_events(session.events),
        )
    )

@router.post(
    path="{session_id}/stop",
    response_model=Response[Optional[Dict]],
    summary="停止指定任务会话",
    description="根据传递的指定会话id停止对应任务会话",
)
async def stop_session(
        session_id: str,
        agent_service: AgentService = Depends(get_agent_service),
) -> Response[Optional[Dict]]:
    """根据传递的指定会话id对应任务会话"""
    await agent_service.stop_session(session_id)
    return Response.success(msg="停止任务会话成功")

@router.get(
    path="{session_id}/files",
    response_model=Response[GetSessionFilesResponse],
    summary="获取指定会话文件列表信息",
    description="获取指定会话文件列表信息"
)
async def get_session_files(
        session_id: str,
        session_service: SessionService = Depends(get_session_service),
) -> Response[GetSessionFilesResponse]:
    """获取指定会话文件列表信息"""
    files = await session_service.get_session_files(session_id)
    return Response.success(
        msg="获取会话文件列表成功",
        data=GetSessionFilesResponse(files=files)
    )