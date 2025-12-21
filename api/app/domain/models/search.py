#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/10 22:33
#Author  :Emcikem
@File    :search.py
"""
from typing import Optional, List

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """搜索结果条目数据类型"""
    url: str  # 搜索条目URL链接
    title: str  # 搜索条目标题
    snippet: str = ""  # 搜索条目摘要信息


class SearchResults(BaseModel):
    """搜索结果数据模型"""
    query: str  # 查询query
    date_range: Optional[str] = None  # 日期筛选范围
    total_results: int = 0  # 搜索结果条数
    results: List[SearchResultItem] = Field(default_factory=list)  # 搜索结果
