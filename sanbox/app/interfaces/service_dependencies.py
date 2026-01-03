#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/21 15:32
#Author  :Emcikem
@File    :service_dependencies.py
"""
from functools import lru_cache

from app.services.file import FileService
from app.services.shell import ShellService


@lru_cache
def get_shell_service() -> ShellService:
    return ShellService()


@lru_cache
def get_file_service() -> FileService:
    return FileService()
