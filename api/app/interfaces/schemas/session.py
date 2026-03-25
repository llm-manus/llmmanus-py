#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/24 21:36
#Author  :Emcikem
@File    :session.py
"""

from pydantic import BaseModel

class CreateSessionResponse(BaseModel):
    """创建会话响应结构"""
    session_id: str # 会话id
