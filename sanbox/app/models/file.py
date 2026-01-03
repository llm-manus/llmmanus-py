#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/1/3 14:14
#Author  :Emcikem
@File    :file.py
"""
from pydantic import BaseModel, Field


class FileReadResult(BaseModel):
    """文件读取结果"""
    filepath: str = Field(..., description="要读取的文件路径")
    content: str = Field(..., description="读取的文件内容")
