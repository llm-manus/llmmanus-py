#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/24 21:36
#Author  :Emcikem
@File    :session.py
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.models.session import SessionStatus


class CreateSessionResponse(BaseModel):
    """创建会话响应结构"""
    session_id: str # 会话id

class ListSessionItem(BaseModel):
    """会话列表条目基础信息"""
    session_id: str = ""
    title: str = ""
    latest_message: str = ""
    latest_message_at: Optional[datetime] = Field(default_factory=lambda :datetime.now())
    status: SessionStatus = SessionStatus.PENDING
    unread_message_count: int = 0

class ListSessionResponse(BaseModel):
    """获取会话列表基础信息响应结构"""
    sessions: List[ListSessionItem]