#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/5/23 10:52
#Author  :Emcikem
@File    :file_service.py
"""
from typing import Tuple, BinaryIO

from fastapi import UploadFile

from app.application.errors.exception import NotFoundError
from app.domain.external.file_storage import FileStorage
from app.domain.models.file import File
from app.domain.repositories.file_repository import FileRepository


class FileService:
    """manus文件系统服务"""

    def __init__(
            self,
            file_storage: FileStorage,
            file_repository: FileRepository
    ) -> None:
        """构造函数，完成文件服务的初始化"""
        self.file_storage = file_storage
        self.file_repository = file_repository

    async def upload_file(self, upload_file: UploadFile) -> File:
        """将传递的文件上传到腾讯云cos并记录上传数据"""
        return await self.file_storage.upload_file(upload_file=upload_file)

    async def get_file_info(self, file_id: str) -> File:
        """根据传递的文件id获取文件消息"""
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            raise NotFoundError(f"该文件[{file_id}]不存在")
        return file

    async def download_file(self, file_id: str) -> Tuple[BinaryIO, File]:
        """根据传递的文件id下载文件"""
        return await self.file_storage.download_file(file_id=file_id)