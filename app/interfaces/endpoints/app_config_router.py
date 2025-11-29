#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/29 20:31
#Author  :Emcikem
@File    :app_config_router.py
"""
import logging

from fastapi import APIRouter

from app.domain.models.app_config import LLMConfig
from app.interfaces.schemas.base import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/app_config", tags=["设置模块"])


@router.get(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="获取LLM配置信息",
    description="包含LLM提供商的base_url、temperature、model_name、max_tokens",
)
async def get_llm_config() -> Response[LLMConfig]:
    """获取LLM配置信息"""
    pass


@router.get(
    path="/llm",
    response_model=None,
    summary="获取LLM配置信息",
    description="更新LLM配置信息时，当api_key为空的时候表示不更新该字段"
)
async def update_llm_config():
    """更新LLM配置信息"""
    pass
