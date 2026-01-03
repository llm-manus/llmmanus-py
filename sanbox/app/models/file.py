#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/1/3 14:14
#Author  :Emcikem
@File    :file.py
"""
from typing import Optional

from pydantic import BaseModel, Field


class FileReadResult(BaseModel):
    """文件读取结果"""
    filepath: str = Field(..., description="要读取的文件路径")
    content: str = Field(..., description="读取的文件内容")


class FileWriteResult(BaseModel):
    """文件写入结果"""
    filepath: str = Field(..., description="要写入的文件绝对路径")
    bytes_written: Optional[int] = Field(default=None, description="写入文件内容的字节数")
