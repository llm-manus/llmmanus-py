#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/21 15:28
#Author  :Emcikem
@File    :shell.py
"""
import os.path

from fastapi import APIRouter
from fastapi.params import Depends

from app.interfaces.errors.exceptions import BadRequestException
from app.interfaces.schemas.base import Response
from app.interfaces.schemas.shell import ExecCommandRequest, ViewShellRequest
from app.interfaces.service_dependencies import get_shell_service
from app.models.shell import ShellExecResult, ShellViewResult
from app.services.shell import ShellService

router = APIRouter(prefix="/shell", tags=["Shell模块"])


@router.post(
    path="/exec-command",
    response_model=Response[ShellExecResult],
)
async def exec_command(
        request: ExecCommandRequest,
        shell_service: ShellService = Depends(get_shell_service),
) -> Response[ShellExecResult]:
    """在指定的Shell会话中运行命令"""
    # 1.判断下是否传递了session_id，如果不存在则新建一个session_id
    if not request.session_id or request.session_id == "":
        request.session_id = shell_service.create_session_id()

    # 2.判断下是否传递了执行目录，如果为传递则使用根目录作为执行路径
    if not request.exec_dir or request.exec_dir == "":
        request.exec_dir = os.path.expanduser("~")

    # 3.调用服务执行命令获取结果
    result = await shell_service.exec_command(
        session_id=request.session_id,
        exec_dir=request.exec_dir,
        command=request.command,
    )

    return Response.success(data=result)


@router.post(
    path="/view-shell",
    response_model=Response[ShellViewResult],
)
async def view_shell(
        request: ViewShellRequest,
        shell_service: ShellService = Depends(get_shell_service),
) -> Response[ShellViewResult]:
    """根据传递的会话id+是否返回控制台标识获取Shell命令执行结果"""
    # 1.判断下Shell会话id是否存在
    if not request.session_id or request.session_id == "":
        raise BadRequestException("Shell会话ID为空，请核实后重试")

    # 2.调页服务获取命令执行结果
    result = await shell_service.view_shell(request, request.session_id, request)

    return Response.success(data=result)
