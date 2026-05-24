#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/29 22:24
#Author  :Emcikem
@File    :service_dependencies.py
"""
import logging
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_service import AgentService
from app.application.services.app_config_service import AppConfigService
from app.application.services.file_service import FileService
from app.application.services.session_service import SessionService
from app.application.services.status_service import StatusService
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.external.file_storage.cos_file_storage import COSFileStorage
from app.infrastructure.external.health_checker.mysql_health_checker import MysqlHealthChecker
from app.infrastructure.external.health_checker.redis_health_checker import RedisHealthChecker
from app.infrastructure.external.llm.openai_llm import OpenAILLM
from app.infrastructure.repositories.db_file_repository import DBFileRepository
from app.infrastructure.repositories.file_app_config_repository import FileAppConfigRepository
from app.infrastructure.storage.cos import Cos, get_cos
from app.infrastructure.storage.mysql import get_db_session
from app.infrastructure.storage.redis import RedisClient, get_redis
from app.interfaces.repository_dependencies import get_db_session_repository
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_app_config_service() -> AppConfigService:
    """获取应用配置服务"""
    # 1.获取数据仓库并打印日志
    logger.info("加载获取AppConfigService")
    file_app_config_repository = FileAppConfigRepository(settings.app_config_filepath)

    # 2.实例化AppConfigService
    return AppConfigService(app_config_repository=file_app_config_repository)


@lru_cache()
def get_status_service(
        db_session: AsyncSession = Depends(get_db_session),
        redis_client: RedisClient = Depends(get_redis),
) -> StatusService:
    """获取状态服务"""
    # 1.初始化MySQL和redis健康检查
    mysql_checker = MysqlHealthChecker(db_session)
    redis_checker = RedisHealthChecker(redis_client)

    # 2.创建服务并返回
    logger.info("加载获取StatusService")
    return StatusService(checkers=[mysql_checker, redis_checker])

@lru_cache()
def get_file_service(
        cos: Cos = Depends(get_cos),
        db_session: AsyncSession = Depends(get_db_session),
) -> FileService:
    # 1.初始化文件仓库和文件存储捅
    file_repository = DBFileRepository(db_session=db_session)
    file_storage = COSFileStorage(
        bucket=settings.cos_bucket,
        cos=cos,
        file_repository=file_repository,
    )

    # 2.构建服务并返回
    return FileService(
        file_storage=file_storage,
        file_repository=file_repository,
    )

@lru_cache()
def get_session_service(
        session_repository: SessionRepository = Depends(get_db_session_repository),
) -> SessionService:
    return SessionService(session_repository=session_repository)

@lru_cache()
def get_agent_service(
        cos: Cos = Depends(get_cos),
        db_session: AsyncSession = Depends(get_db_session),
        session_repository: SessionRepository = Depends(get_session_service),
) -> AgentService:
    # 1.获取应用配置信息（读取配置需要实时获取，所有不配置缓存）
    app_config_repository = FileAppConfigRepository(config_path=settings.app_config_filepath)
    app_config = app_config_repository.load()
    file_repository = DBFileRepository(db_session=db_session)

    # 2.构建依赖实例
    llm = OpenAILLM(app_config.llm_config)
    file_storage = COSFileStorage(
        bucket=settings.cos_bucket,
        cos=cos,
        file_repository=file_repository,
    )

    # 3.实例Agent服务并返回
    return AgentService(
        session_repository=session_repository,
        llm=llm,
        agent_config=app_config.agent_config,
        mcp_config=app_config.mcp_config,
        a2a_config=app_config.a2a_config,
        sandbox_cls=app_config.sandbox_cls,
        task_cls=app_config.task_cls,
        json_parser=app_config.json_parser,
        search_engine=app_config.search_engine,
        file_storage=file_storage,
        file_repository=file_repository,
    )