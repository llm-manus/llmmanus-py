#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/21 15:28
#Author  :Emcikem
@File    :file.py
"""
from fastapi import APIRouter, Depends

from app.interfaces.schemas.base import Response
from app.interfaces.schemas.file import ReadFileRequest
from app.interfaces.service_dependencies import get_file_service
from app.models.file import FileReadResult
from app.services.file import FileService

router = APIRouter(prefix="/file", tags=["File模块"])


@router.post(
    path="/read-file",
    response_model=Response[FileReadResult],
)
async def read_file(
        request: ReadFileRequest,
        file_service: FileService = Depends(get_file_service),
) -> Response[FileReadResult]:
    """根据传递的数据读取沙箱中的文件内容"""
    result = await file_service.read_file(
        filepath=request.filepath,
        start_line=request.start_line,
        end_line=request.end_line,
        sudo=request.sudo,
        max_lenghth=request.max_lenghth,
    )

    return Response.success(
        msg="文件读取成功",
        data=result,
    )
