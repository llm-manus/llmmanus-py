#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/30 16:09
#Author  :Emcikem
@File    :task.py
"""
from abc import ABC, abstractmethod
from optparse import Option
from typing import Protocol

from app.domain.external.message_queue import MessageQueue


class TaskRunner(ABC):
    """任务运行器，负责任务的执行、关心的是如何执行任务、摧毁任务释放资源"""

    @abstractmethod
    async def invoke(self, task: "Task") -> None:
        """调用任务并执行"""
        raise NotImplementedError

    @abstractmethod
    async def destroy(self) -> None:
        """崔欢任务并释放资源，包括：关闭网络连接、释放内存、清理临时内存、清理后台进程等"""
        raise NotImplementedError

    @abstractmethod
    async def on_done(self, task: "Task") -> None:
        """执行任务完成时对应的回调函数"""
        raise NotImplementedError


class Task(Protocol):
    """定义任务相关的操作接口协议"""

    async def run(self) -> None:
        """运行当前任务"""
        ...

    async def cancel(self) -> None:
        """取消当前任务"""
        ...

    @property
    def input_stream(self) -> MessageQueue:
        """只读属性，返回任务的输入流"""
        ...

    @property
    def output_stream(self) -> MessageQueue:
        """只读属性，返回任务的输出流"""
        ...

    @property
    def id(self) -> str:
        """只读属性，返回任务的id"""
        ...

    @property
    def done(self) -> bool:
        """只读属性，返回任务是否结束"""
        ...

    @classmethod
    def get(cls, task_id: str) -> Option["Task"]:
        """类方法，根据任务id获取对应任务"""
        ...

    @classmethod
    def create(cls, task_runner: TaskRunner) -> "Task":
        """根据传递的任务运行器创建任务"""
        ...

    @classmethod
    def destroy(cls) -> None:
        """摧毁所有任务实例"""
        ...
