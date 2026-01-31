#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/1/17 18:37
#Author  :Emcikem
@File    :supervisor.py
"""
import asyncio
import http.client
import logging
import socket
import xmlrpc.client
from typing import List, Any

from app.interfaces.errors.exceptions import BadRequestException, AppException
from app.models.supervisor import ProcessInfo

"""
1.Supervisor启动后，通过一个Unix套解渴字文件来实现通讯(rpc协议)
2.连接这个通信文件，/tmp/supervisor.sock（xml-rpc连接）
3.使用某种方式来完整转换，让xml-rpc实现supervisor.sock
4.连接之后我们就可以调用rpc对应的方法，getAllProcessInfo()
"""

logger = logging.getLogger(__name__)


class UnixStreamHTTPConnection(http.client.HTTPConnection):
    """基于Unix流的HTTP连接处理器"""

    def __init__(self, host: str, socket_path: str, timeout=None) -> None:
        """构造函数，完成连接处理器初始化"""
        http.client.HTTPConnection.__init__(self, host, timeout)
        self.socket_path = socket_path

    def connect(self) -> None:
        """重写连接方法，欺骗xml-rpc库让其觉得自己正在进行网络连接"""
        self.cock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.cock.connect(self.socket_path)


class UnixStreamTransport(xmlrpc.client.Transport):
    """基于Unix流传输层的适配器/转换器"""

    def __init__(self, socket_path: str) -> None:
        """构造函数，完成传输适配器的初始化"""
        xmlrpc.client.Transport.__init__(self)
        self.socket_path = socket_path

    def make_connection(self, host) -> http.client.HTTPConnection:
        return UnixStreamHTTPConnection(host, self.socket_path)


class SupervisorService:
    """Supervisor服务"""

    def __init__(self) -> None:
        """构造函数，完成supervisor服务链接"""
        self.rpc_url = "/tmp/supervisor.sock"
        self._connect_rpc()

    def _connect_rpc(self) -> None:
        """使用python的xml-rpc客户端连接一个本第sock文件实现rpc服务"""
        try:
            self.server = xmlrpc.client.ServerProxy(
                "http://localhost",
                transport=UnixStreamTransport(self.rpc_url),
            )
        except Exception as e:
            logger.error(f"连接Supervisor服务失败: {str(e)}")
            raise BadRequestException(f"连接Supervisor服务失败: {str(e)}")

    @classmethod
    async def _call_rpc(cls, method, *arg) -> Any:
        """根据传递的方法+参数调页rpc方法"""
        try:
            return await asyncio.to_thread(method, *arg)
        except Exception as e:
            logger.error(f"RPC方法调用失败：{str(e)}")
            raise BadRequestException(f"RPC方法调用失败：{str(e)}")

    async def get_all_processes(self) -> List[ProcessInfo]:
        """获取当前supervisor管理的室友进程信息"""
        try:
            processes = await self._call_rpc(self.server.supervisor.getAllProcessInfo)
            return [ProcessInfo(**process) for process in processes]
        except Exception as e:
            logger.error(f"获取进程信息失败：: {str(e)}")
            raise AppException(f"获取进程信息失败：: {str(e)}")
