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
from app.models.file import FileReadResult, FileWriteResult

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
        try:
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
        except Exception as e:
            # 13.判定异常类型执行不同操作
            if isinstance(e, BadRequestException) or isinstance(e, AppException):
                raise
            raise AppException(f"文件读取失败：{str(e)}")

    @classmethod
    async def write_file(
            cls,
            filepath: str,
            content: str,
            append: bool = False,
            leading_newline: bool = False,
            trailing_newline: bool = False,
            sudo: bool = False,
    ) -> FileWriteResult:
        """根据传递的文件路径+内容向指定文件写入内容"""
        try:
            # 1.组装实际写入的内容
            if leading_newline:
                content = "\n" + content
            if trailing_newline:
                content = content + "\n"

            # 2.判断是否是sudo权限，并且不是windows系统
            if sudo and sys.platform != "win32":
                # 3.使用命令的方式先向零食文件写入数据，计算追加模式
                mode = ">>" if append else ">"

                # 4.创建一个临时文件
                temp_file = f"/tmp/file_write_{os.getpid()}.tmp"

                # 5.厨行家一个内部函数使用asyncio创建新线程写入数据
                def async_write_temp_file() -> int:
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    return len(content.encode("utf-8"))

                # 6.使用asyncio创建子线程并写入
                bytes_written = await asyncio.to_thread(async_write_temp_file)

                # 7.使用命令行将临时文件写入到目标文件中
                command = f"sudo bash -c \"cat {temp_file} {mode} {filepath}\""
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # 8.等待子进程执行完毕
                stdout, stderr = await process.communicate()

                # 9.检测子进程是否正常执行
                if process.returncode != 0:
                    raise BadRequestException(f"文件内容写入失败：{stderr.decode()}")

                # 10.清除下临时文件
                os.unlink(temp_file)
            else:
                # 11.非sudo或者windows下使用Python方式写入，先确保文件路径存在
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                # 12.创建一个异步写入的函数
                def async_write_file() -> int:
                    write_mode = "a" if append else "w"
                    with open(filepath, write_mode, encoding="utf-8") as f:
                        return f.write(content)

                # 13.使用asyncio创建一个子线程写入内容
                bytes_written = await asyncio.to_thread(async_write_file)

            return FileWriteResult(
                filepath=filepath,
                bytes_written=bytes_written,
            )
        except Exception as e:
            # 14.根据不同的错误执行不同的操作
            logger.error(f"文件内容写入失败：{str(e)}")
            if isinstance(e, BadRequestException):
                raise
            raise AppException(f"文件内容写入失败：{str(e)}")
