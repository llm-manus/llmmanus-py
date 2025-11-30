#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/29 20:31
#Author  :Emcikem
@File    :app_config_router.py
"""
import logging

from fastapi import APIRouter, Depends

from app.application.services.app_config_service import AppConfigService
from app.domain.models.app_config import LLMConfig
from app.interfaces.dependencies import get_app_config_service
from app.interfaces.schemas.base import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/app_config", tags=["设置模块"])


@router.get(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="获取LLM配置信息",
    description="包含LLM提供商的base_url、temperature、model_name、max_tokens",
)
async def get_llm_config(
        app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[LLMConfig]:
    """获取LLM配置信息"""
    llm_config = app_config_service.get_llm_config()
    return Response.success(data=llm_config.model_dump(exclude={"api_key"}))


@router.post(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="获取LLM配置信息",
    description="更新LLM配置信息时，当api_key为空的时候表示不更新该字段"
)
async def update_llm_config(
        new_app_config: LLMConfig,
        app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[LLMConfig]:
    """更新LLM配置信息"""
    updated_llm_config = app_config_service.update_llm_config(new_app_config)
    return Response.success(
        msg="更新LLM信息配置成功",
        data=updated_llm_config.model_dump(exclude={"api_key"}),
    )
