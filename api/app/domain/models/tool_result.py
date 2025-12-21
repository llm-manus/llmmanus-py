#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/7 15:12
#Author  :Emcikem
@File    :tool_result.py
"""
from typing import Optional, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T")


class ToolResult(BaseModel, Generic[T]):
    """根据结果Domain模型"""
    success: bool = True  # 是否成功调用
    message: Optional[str] = ""  # 额外的信息提示
    data: Optional[T] = None  # 根据的执行结果/数据
