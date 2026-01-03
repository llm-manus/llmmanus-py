#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/21 15:28
#Author  :Emcikem
@File    :file.py
"""
from fastapi import APIRouter, Depends

from app.interfaces.schemas.base import Response
from app.interfaces.schemas.file import ReadFileRequest, WriteFileRequest
from app.interfaces.service_dependencies import get_file_service
from app.models.file import FileReadResult, FileWriteResult
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
        max_length=request.max_length,
    )

    return Response.success(
        msg="文件读取成功",
        data=result,
    )


@router.get(
    path="/write-file",
    response_model=Response[FileWriteResult],
)
async def write_file(
        request: WriteFileRequest,
        file_service: FileService = Depends(get_file_service),
) -> Response[FileWriteResult]:
    """根据传递的数据向指定文件写入内容"""
    result = await file_service.write_file(
        filepath=request.filepath,
        content=request.content,
        append=request.append,
        leading_newline=request.leading_newline,
        trailing_newline=request.trailing_newline,
        sudo=request.sudo,
    )

    return Response.success(
        msg="文件内容写入成功",
        data=result,
    )
