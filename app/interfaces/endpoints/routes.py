#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/23 20:29
#Author  :Emcikem
@File    :routes.py
"""
from fastapi import APIRouter

from . import status_router


def create_api_routes() -> APIRouter:
    """创建API路由，涵盖整个项目的所有管理器"""
    # 1.创建APIRouter实例
    api_router = APIRouter()

    # 2.将各个模块添加到api_router中
    api_router.include_router(status_router.router)

    # 3.返回api路由实例
    return api_router


router = create_api_routes()
