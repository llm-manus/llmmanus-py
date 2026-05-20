#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/5/20 23:54
#Author  :Emcikem
@File    :file_repository.py
"""
from typing import Protocol, Optional

from app.domain.models.file import File


class FileRepository(Protocol):
    """文件模型数据仓库"""

    async def save(self, file: File) -> None:
        """新增或更新文件"""
        ...

    async def get_by_id(self, file_id: str) -> Optional[File]:
        """根据传递的文件id获取文件信息"""
        ...