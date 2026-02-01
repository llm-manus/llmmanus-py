#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/2/1 15:17
#Author  :Emcikem
@File    :supervisor.py
"""
from typing import Optional

from pydantic import BaseModel, Field


class TimeoutRequest(BaseModel):
    """激活超时销毁请求"""
    minutes: Optional[int] = Field(default=None, description="分钟数")
