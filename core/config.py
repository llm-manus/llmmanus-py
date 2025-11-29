#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/23 17:56
#Author  :Emcikem
@File    :config.py
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Manus后端中控配置信息，从.env或者环境变量中加载数据"""

    # 项目基础配置
    env: str = "development"
    log_level: str = "INFO"
    app_config_filepath: str = "config.yaml"

    # 数据库相关配置
    sqlalchemy_database_uri: str = ""

    # Redis缓存配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Cos腾讯云对象村粗配置
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_region: str = ""
    cos_scheme: str = "https"
    cos_bucket: str = ""
    cos_domain: str = ""

    # 使用pydantic v2的写法来完成环境变量信息的告知
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """获取当前manus项目的配置信息，并对内容进行缓存，避免重复读取"""
    settings = Settings()
    return settings
