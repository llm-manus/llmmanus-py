#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/23 17:57
#Author  :Emcikem
@File    :main.py
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.logging import setup_logging
from app.interfaces.endpoints.routes import router
from core.config import get_settings

# 1.加载配置信息
settings = get_settings()

# 2.初始化日志系统
setup_logging()
logger = logging.getLogger()

# 3.定义FastAPI路由tags标签
openapi_tags = [
    {
        "name": "状态模块",
        "description": "包含 **状态** 等API 接口，用于监测系统的运行状态。"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """创建FastAPI要用层序生命周期上下文管理"""
    # 1.打印日志表示程序开始了
    logger.info("manus正在初始化")

    # todo内容
    try:
        # lifespan节点/分界
        yield
    finally:
        logger.info("manus正在关闭")


# 4.创建Manus应用实例
app = FastAPI(
    title="Manus通用智能体",
    description="Manus是一个通用的AI Agent系统，可以完全私有部署，使用A2A+MCP连接Agent/Tool，同时支持在沙箱中运行各种内置工具和操作",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    version="1.0.0",
)

# 5.配置CORS中间件，解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5.集成路由
app.include_router(router, prefix="/api")
