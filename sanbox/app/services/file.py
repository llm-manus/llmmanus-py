#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/1/3 14:22
#Author  :Emcikem
@File    :file.py
"""
import asyncio
import locale
import logging
import os.path
import sys
from typing import Optional

from app.interfaces.errors.exceptions import NotFoundException, BadRequestException, AppException
from app.models.file import FileReadResult

logger = logging.getLogger(__name__)


class FileService:
    """文件沙箱服务"""

    @classmethod
    async def read_file(
            cls,
            filepath: str,
            start_line: Optional[int] = None,
            end_line: Optional[int] = None,
            sudo: bool = False,
            max_length: Optional[int] = None,
    ) -> FileReadResult:
        """根据传递的文件路径+起始行号+权限+最大长度读取文件的内容"""
        # 1.检测在当前权限下能否获取该文件
        if not os.path.exists(filepath) and not sudo:
            logger.error(f"要读取的文件不存在或无权限：{filepath}")
            raise NotFoundException(f"要读取的文件不存在或无权限：{filepath}")

        # 2.获取系统编码
        encoding = locale.getpreferredencoding() if sys.platform == "win32" else "utf-8"

        # 3.判断是否提供sudo+非windows系统，如果是则使用命令行的方式读取文件
        if sudo and sys.platform != "win32":
            # 4.使用sudo cat命令读取文件内容
            command = f"sudo cat '{filepath}'"
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # 5.读取子进程的输出，并等待子进程结束
            stdout, stderr = await process.communicate()

            # 6.判断子进程的姿态是否正常结束
            if process.returncode != 0:
                raise BadRequestException(f"阅读文件失败：{stderr.decode()}")

            # 7.读取输出内容
            content = stdout.decode(encoding, errors="replace")
        else:
            # 8.创建一个内部读取函数
            def async_read_file() -> str:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    raise AppException(msg=f"读取文件失败：{str(e)}")

            # 9.使用asyncio创建线程读取文件
            content = await asyncio.to_thread(async_read_file)

        # 10.判断是否传递了读取范围
        if start_line is not None and end_line is not None:
            # 11.将内容切割成行，并且读取指定范围行号的数据
            lines = content.splitlines()
            start = start_line if start_line is not None else 0
            end = end_line if end_line is not None else len(content)
            content = "\n".join(lines[start:end])

        # 12.裁切下数据长度
        if max_length is not None and 0 < max_length < len(content):
            content = content[:max_length] + "(truncated)"

        return FileReadResult(filepath=filepath, content=content)
