#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/1/17 16:54
#Author  :Emcikem
@File    :supervisor.py
"""
from typing import Optional, Any

from pydantic import BaseModel, Field


class ProcessInfo(BaseModel):
    """进程消息模型"""
    name: str = Field(..., description="进程名字")
    group: str = Field(..., description="进程分组")
    description: str = Field(..., description="进程描述")
    start: int = Field(..., description="进程开始时间戳")
    stop: int = Field(..., description="进程结束时间戳")
    now: int = Field(..., description="当前时间戳")
    state: int = Field(..., description="状态代码")
    statename: str = Field(..., description="状态名字")
    spawnerr: str = Field(..., description="Spawn错误")
    exitstatus: int = Field(..., description="退出状态")
    logfile: str = Field(..., description="日志文件")
    stdout_logfile: str = Field(..., description="标准输出日志文件")
    stderr_logfile: str = Field(..., description="标准错误日志文件")
    pid: str = Field(..., description="进程id(Process ID)")


class SupervisorActionResult(BaseModel):
    """Supervisor动作/执行结果"""
    status: str = Field(..., description="执行状态")
    result: Optional[Any] = Field(default=None, description="执行结果")
    stop_result: Optional[Any] = Field(default=None, description="停止结果")
    start_result: Optional[Any] = Field(default=None, description="开始结果")
    shutdown_result: Optional[Any] = Field(default=None, description="关闭结果")
