#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/4/16 23:34
#Author  :Emcikem
@File    :planner_react.py
"""
import logging
from typing import AsyncGenerator, Optional

from app.domain.external.browser import Browser
from app.domain.external.json_parser import JSONParser
from app.domain.external.llm import LLM
from app.domain.external.sandbox import Sandbox
from app.domain.external.search import SearchEngine
from app.domain.models.app_config import AgentConfig
from app.domain.models.event import BaseEvent
from app.domain.models.message import Message
from app.domain.models.plan import Plan
from app.domain.repositories.session_repository import SessionRepository
from app.domain.services.agents.planner import PlannerAgent
from app.domain.services.agents.react import ReActAgent
from app.domain.services.flows.base import BaseFlow, FlowStatus
from app.domain.services.tools.A2ATool import A2ATool
from app.domain.services.tools.browser import BrowserTool
from app.domain.services.tools.file import FileTool
from app.domain.services.tools.mcp import MCPTool
from app.domain.services.tools.message import MessageTool
from app.domain.services.tools.search import SearchTool
from app.domain.services.tools.shell import ShellTool

logger = logging.getLogger(__name__)

class PlannerReActFlow(BaseFlow):
    """规划与执行流"""

    def __init__(
            self,
            llm: LLM, # 大语言模型
            agent_config: AgentConfig, # 智能体配置
            session_id: str, # 会话id
            session_repository: SessionRepository, # 会话仓库
            json_parser: JSONParser, # JSON解析器
            browser: Browser, # 浏览器
            sandbox: Sandbox, # 沙箱
            search_engine: SearchEngine, # 搜索引擎
            mcp_tool: MCPTool, # mcp工具
            a2a_tool: A2ATool, # a2a远程agent
    ) -> None:
        """构造函数，完成规划与执行流的初始化"""
        # 1.流初始化数据配置
        self._session_id = session_id
        self._session_repository = session_repository
        self.status = FlowStatus.IDLE
        self.plan: Optional[Plan] = None

        # 2.初始化Agent预设工具列表
        tools = [
            FileTool(sandbox=sandbox),
            ShellTool(sandbox=sandbox),
            BrowserTool(browser=browser),
            SearchTool(search_engine=search_engine),
            MessageTool(),
            mcp_tool,
            a2a_tool,
        ]

        # 3.创建规划Agent
        self.planner = PlannerAgent(
            session_id=session_id,
            session_repository=session_repository,
            agent_config=agent_config,
            llm=llm,
            json_parser=json_parser,
            tools=tools,
        )
        logger.debug(f"创建规划Agent成功，会话id：{self._session_id}")

        # 4.创建执行Agent
        self.react = ReActAgent(
            session_id=session_id,
            session_repository=session_repository,
            agent_config=agent_config,
            llm=llm,
            json_parser=json_parser,
            tools=tools,
        )
        logger.debug(f"创建执行Agent成功，会话id：{self._session_id}")

    async def invoke(self, message: Message) -> AsyncGenerator[BaseEvent, None]:
        pass

    @property
    def done(self) -> bool:
        """只读属性，返回流是否运行结束"""
        return self.status == FlowStatus.IDLE
