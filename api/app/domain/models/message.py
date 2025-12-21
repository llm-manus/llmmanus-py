#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/8 22:06
#Author  :Emcikem
@File    :message.py
"""
from typing import List

from pydantic import BaseModel, Field


class Message(BaseModel):
    """用户传递的消息"""
    message: str = ""  # 用户发送的消息
    attachments: List[str] = Field(default_factory=list)  # 用户发送的附件
