#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/21 21:22
#Author  :Emcikem
@File    :shell.py
"""
import asyncio
import getpass
import logging
import os.path
import socket
import uuid
from typing import Dict

from app.interfaces.errors.exceptions import BadRequestException, AppException
from app.models.shell import ShellExecResult, Shell, ConsoleRecord

logger = logging.getLogger(__name__)


class ShellService:
    """Shell命令服务"""
    active_shells: Dict[str, Shell] = {}

    @classmethod
    def _get_display_path(cls, path: str) -> str:
        """获取显示路径，将~替换成用户主目录"""
        # 1.使用程序获取跨平台下用户的主目录
        home_dir = os.path.expanduser("~")
        logger.debug(f"主目录：{home_dir}, 路径：{path}")

        # 2.判断传递进来的路径是否是主路径，如果是则替换成~
        if path.startswith(home_dir):
            return path.replace(home_dir, "~", 1)
        return path

    def _format_ps1(self, exec_dir: str) -> str:
        """格式化命令结构提示，增强交互体验，例如：root@myserver:/var/log $"""
        username = getpass.getuser()
        hostname = socket.gethostname()
        display_dir = self._get_display_path(exec_dir)
        return f"{username}@{hostname}:{display_dir}"

    @classmethod
    def create_session_id(cls) -> str:
        """创建会话id，使用uuid4生成唯一值"""
        session_id = str(uuid.uuid4())
        logger.info(f"创建一个新的Shell会话ID：{session_id}")
        return session_id

    async def exec_command(
            self,
            session_id: str,
            exec_dir: str,
            command: str,
    ) -> ShellExecResult:
        """传递会话id+执行目录+命令在沙箱中执行后返回"""
        # 1.记录日志并判断执行目录是否存在
        logger.info(f"正在会话：{session_id} 中执行命令：{command}")
        if not exec_dir or exec_dir == "":
            exec_dir = os.path.expanduser("~")
        if not os.path.exists(exec_dir):
            logger.error(f"当前目录不存在：{exec_dir}")
            raise BadRequestException(f"当前目录不存在：{exec_dir}")

        try:
            # 2.格式话生成ps1格式
            ps1 = self._format_ps1(exec_dir)

            # 3.判断当前Shell会话是否存在
            if session_id not in self.active_shells:
                # 4.创建一个新的进程
                logger.debug(f"创建一个新的Shell会话：{session_id}")
                process = await self._create_process(exec_dir, command)
                self.active_shells[session_id] = Shell(
                    process=process,
                    exec_dir=exec_dir,
                    output="",
                    console_records=[ConsoleRecord(ps1=ps1, command=command, output="")],
                )

                # 5.创建后台任务来运行输出读取器
                asyncio.create_task(self._start_output_reader(session_id, process))

            else:
                # 6.该会话已存在则读取数据
                logger.debug(f"使用现有的Shell会话：{session_id}")
                shell = self.active_shells[session_id]
                old_process = shell.process

                # 7.判断旧进程是否还在运行，如果是则先停止旧进程执行新命令
                if old_process.returncode is None:
                    logger.debug(f"正在终止会话中的上一个进程：{session_id}")
                    try:
                        # 8.结束旧进程并优雅等待1s
                        old_process.terminate()
                        await asyncio.wait_for(old_process.wait(), timeout=1)
                    except Exception as e:
                        # 9.结束旧进程出现错误并记录日志调用kill强制关闭进程
                        logger.warning(f"强制终止Shell会话中的进程 {session_id} 失败：{str(e)}")
                        old_process.kill()

                # 10.关闭之后创建一个新的进程
                process = await self._create_process(exec_dir, command)

                # 11.更新会话信息
                shell.process = process
                shell.exec_dir = exec_dir
                shell.output = ""
                shell.console_records.append(ConsoleRecord(ps1=ps1, command=command, output=""))

                # 12.创建后台来运行输出读取器
                asyncio.create_task(self._start_output_reader(session_id, process))

            try:
                # 13.尝试等待子进程执行(最多等待5s)
                logger.debug(f"正在等待会话中的进程完成：{session_id}")
                wait_result = await self.wait_for_process(session_id, second=5)

                # 14.判断返回代码是否非空（已结束）则同步返回执行结果
                if wait_result.returncode is None:
                    # 15.记录日志并查看结果
                    logger.debug(f"Shell会话进程已结束，代码：{wait_result.returncode}")
                    view_result = await self.view_shell(session_id)

                    return ShellExecResult(
                        session_id=session_id,
                        command=command,
                        status="completed",
                        returncode=wait_result.returncode,
                        output=view_result.output,
                    )
            except BadRequestException as _:
                # 16.等待超时，记录日志不做额外处理让命令在后台继续运行
                logger.warning(f"进程在会话超时后仍在运行：{session_id}")
                pass
            except Exception as e:
                # 17.其他异常忽略并让程序继续进行
                logger.warning(f"等待进程时出现异常：{str(e)}")
                pass

            return ShellExecResult(
                session_id=session_id,
                command=command,
                status="running",
            )

        except Exception as e:
            # 18.执行过程中出现异常并记录日志后返回自定义异常
            logger.error(f"命令执行失败：{str(e)}", exc_info=True)
            raise AppException(
                msg=f"命令执行失败：{str(e)}",
                data={"session_id": session_id, "command": command},
            )
