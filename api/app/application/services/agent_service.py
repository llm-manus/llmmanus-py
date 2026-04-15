#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/3/31 21:22
#Author  :Emcikem
@File    :agent_service.py
"""
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional, List, Type

from json_repair.json_parser import JSONParser
from pydantic import TypeAdapter

from app.domain.external.llm import LLM
from app.domain.external.sandbox import Sandbox
from app.domain.external.search import SearchEngine
from app.domain.external.task import Task, TaskRunner
from app.domain.models.app_config import AgentConfig, MCPConfig
from app.domain.models.event import BaseEvent, ErrorEvent, MessageEvent, Event, DoneEvent, WaitEvent
from app.domain.models.file import File
from app.domain.models.session import Session, SessionStatus
from app.domain.repositories.session_repository import SessionRepository

logger = logging.getLogger(__name__)

class AgentService:
    """manus智能体服务"""

    def __init__(
            self,
            session_repository: SessionRepository,
            llm: LLM,
            agent_config: AgentConfig,
            mcp_config: MCPConfig,
            a2a_config: A2AConfig,
            sandbox_cls: Type[Sandbox],
            task_cls: Type[Task],
            json_parser: JSONParser,
            search_engine: SearchEngine,
            file_storage: FileStorage,
            file_repository: FileRepository,
    ) -> None:
        """构造函数，完成Agent服务初始化"""
        self._session_repository = session_repository
        self._llm = llm
        self._agent_config = agent_config
        self._mcp_config = mcp_config
        self._a2a_config = a2a_config
        self._sandbox_cls = sandbox_cls
        self._task_cls = task_cls
        self._json_parser = json_parser
        self._search_engine = search_engine
        self._file_storage = file_storage
        self._file_repository = file_repository
        logger.info(f"AgentService初始化成功")

    async def _get_task(self, session: Session) -> Optional[Task]:
        """根据传递的任务会话获取任务实例"""
        # 1.从会话中取出任务id
        task_id = session.task_id
        if not task_id:
            return None

        # 2.调用人物类的get方法获取对应的任务实例
        return self._task_cls.get(task_id)

    async def _create_task(self, session: Session) -> Task:
        """根据传递的会话创建一个新任务"""
        # 1.获取沙箱实例
        sandbox = None
        sandbox_id = session.sandbox_id
        if sandbox_id:
            sandbox = await self._sandbox_cls.get(sandbox_id)

        # 2.判断是否能获取到沙箱（如果没有则创建）
        if not sandbox:
            # 3.沙箱不存在则创建一个新的（有可能是被释放了）
            sandbox = await self._sandbox_cls.create()
            session.sandbox_id = sandbox.id
            await self._session_repository.save(session)

        # 4.从沙箱中获取浏览器实例
        browser = await sandbox.get_browser()
        if not browser:
            logger.error(f"获取沙箱[{sandbox.id}]中的浏览器")

        # 5.创建AgentTaskRunner
        task_runner = AgentTaskRunner(
            llm=self._llm,
            agent_config=self._agent_config,
            mcp_config=self._mcp_config,
            a2a_config=self._a2a_config,
            session_id=session.id,
            session_repository=self._session_repository,
            file_storage=self._file_storage,
            file_repository=self._file_repository,
            json_parser=self._json_parser,
            browser=browser,
            search_engine=self._search_engine,
            sandbox=sandbox,
        )

        # 6.创建任务Task更新会话中的信息
        task = self._task_cls.create(task_runner=task_runner)
        session.task_id = task
        await self._session_repository.save(session)

        return task

    async def chat(
            self,
            session_id: str,
            message: Optional[str] = None,
            attachments: Optional[List[str]] = None,
            latest_event_id: Optional[str] = None,
            timestamp: Optional[datetime] = None,
    ) -> AsyncGenerator[BaseEvent, None]:
        """根据传递的信息调用Agent服务发起对话请求"""
        try:
            # 1.检查会话是否存在
            session = await self._session_repository.get_by_id(session_id)
            if not session:
                logger.error(f"尝试与不存在的任务会话[{session_id}]会话")
                raise RuntimeError("任务会话不存在，请核实后重试")

            # 2.获取对应的会话
            task = await self._get_task(session)

            # 3.判断是否传递了message
            if message:
                # 4.判断会话的状态是什么，如果不是运行中则表示已完成或者空闲中
                if session.status != SessionStatus.RUNNING:
                    # 5.不在运行中需要创建一个新的task并启动
                    task = await self._create_task(session)
                    if not task:
                        logger.error(f"会话[{session}]创建任务失败")
                        raise RuntimeError(f"会话[{session}]创建任务失败")

                # 6.传递了消息则更新会话中的最后一条消息
                await self._session_repository.update_latest_message(
                    session_id=session_id,
                    message=message,
                    timestamp=timestamp,
                )

                # 7.创建一个人类消息事件
                message_event = MessageEvent(
                    role="user",
                    message=message,
                    attachments=[File(id=attachment) for attachment in attachments],
                )

                # 8.将事件添加到任务的输入流中，好让Agent获取到数据
                event_id = await task.input_stream.put(message_event.model_dump_json())
                message_event.id = event_id
                await self._session_repository.add_event(session_id, message_event)

                # 9.执行任务
                await task.invoke()
                logger.info(f"往会话[{session_id}]输入消息队列写入消息：{message[:50]}...")

            # 10.记录日志展示会话已启动
            logger.info(f"会话[{session_id}]已启动")
            logger.info(f"会话[{session_id}]任务实例：{task}")

            # 11.从任务的输出流中读取数据
            while task and not task.done:
                # 12.从输出消息队列中获取数据
                event_id, event_str = await task.output_stream.get(start_id=latest_event_id, block_ms=0)
                latest_event_id = event_id
                if event_str is None:
                    logger.debug(f"在会话[{session}]输出队列中未发现事件内容")
                    continue

                # 13.使用Pydantic提供的类型是配置器将event_str转换成指定类实例
                event = TypeAdapter(Event).validate_json(event_str)
                event.event_id = event_id
                logger.debug(f"从会话[{session_id}]中获取事件：{type(event).__name__}")

                # 14.将未读消息数重置为0
                await self._session_repository.update_unread_message_count(session_id, 0)

                # 15.将事件返回并判断事件类型是否为结束类型
                yield event
                if isinstance(event, (DoneEvent, ErrorEvent, WaitEvent)):
                    break

            # 16.循环外面表示这次任务AI端的已结束
            logger.info(f"会话[{session_id}]本轮运行结束")
        except Exception as e:
            # 17.记录日志并返回错误日志
            logger.error(f"任务会话[{session_id}]对话错误：{str(e)}")
            event = ErrorEvent(error=str(e))
            await self._session_repository.add_event(session_id, event)
            yield event
        finally:
            # 18.会话完整传递给前端后，表示至少用户肯定收到了这些消息，所以不应该有未读消息
            await self._session_repository.update_unread_message_count(session_id, 0)