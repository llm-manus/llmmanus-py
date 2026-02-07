#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/2/2 21:34
#Author  :Emcikem
@File    :docker_sandbox.py
"""
import logging
from typing import Optional

import httpx

from app.domain.external.sandbox import Sandbox

logger = logging.getLogger(__name__)

class DockerSandbox(Sandbox):
    """基于Docker的沙箱服务"""

    def __init__(
            self,
            ip: Optional[str] = None,
            container_name: Optional[str] = None,
    ) -> None:
        """构造函数，完成Docker沙箱扩展创建"""
        self.client = httpx.AsyncClient(timeout=600)
        self._ip = ip
        self._container_name = container_name
        self._base_url = f"http://{ip}:8080"
        self._vnc_url = f"ws://{ip}:5901"
        self._cdp_url = f"http://{ip}:9222"

    @property
    def ip(self) -> str:
        """获取沙箱的唯一id，使用容器帽子作为唯一id
        """
