#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/7 20:29
#Author  :Emcikem
@File    :base.py
"""
import asyncio
import logging
from abc import ABC
from typing import Optional, List, AsyncGenerator, Dict, Any

from app.domain.external.json_parser import JsonParser
from app.domain.external.llm import LLM
from app.domain.models.app_config import AgentConfig
from app.domain.models.event import Event
from app.domain.models.memory import Memory
from app.domain.services.tools.base import BaseTool

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """基础Agent智能体"""
    name: str = ""  # 智能体名字
    _system_prompt: str = ""  # 系统预设prompt
    _format: Optional[str] = None  # Agent的响应格式
    _retry_interval: float = 1.0  # 重试间隔
    _tool_choice: Optional[str] = None  # 强制选择工具

    def __init__(
            self,
            agent_config: AgentConfig,  # Agent配置
            llm: LLM,  # 语言模型协议
            memory: Memory,  # 记忆
            json_parser: JsonParser,  # JSON输出解释器
            tools: List[BaseTool],  # 工具列表
    ) -> None:
        """构造函数，完成Agent的初始化"""
        self._agent_config = agent_config
        self._llm = llm
        self._memory = memory
        self._json_parser = json_parser
        self._tools = tools

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """获取Agent所有可用的工具列表参数申明/Schema"""
        available_tools = []
        for tool in self._tools:
            available_tools.extend(tool.get_tools())
        return available_tools

    async def _invoke_llm(self, messages: List[Dict[str, Any]], format: Optional[str] = None) -> Dict[str, Any]:
        """调用语言模型并处理记忆内容"""
        # 1.将消息添加到记忆中
        await self._add_to_memory(messages)

        # 2.组装语言模型的响应格式
        response_format = {"type": format} if format else None

        # 3.循环向LLM发起提问知道最大重试次数
        for _ in range(self._agent_config.max_retries):
            try:
                # 4.调用语言模型获取响应内容
                message = await self._llm.invoke(
                    messages=messages,
                    tools=self._get_available_tools(),
                    response_format=response_format,
                    tool_choice=self._tool_choice,
                )

                # 5.处理AI响应内容避免空回复
                if message.get("role") == "assistant":
                    if not message.get("content") and not message.get("tool_calls"):
                        logger.warning(f"LLM回复了空内容，执行重试")
                        await self._add_to_memory([
                            {"role": "assistant", "content": ""},
                            {"role": "user", "content": "AI无响应内容，请继续。"}
                        ])
                        await asyncio.sleep(self._retry_interval)
                        continue

                    # 6.取出非空消息并处理工具调用
                    filtered_message = {"role": "assistant", "content": message.get("content")}
                    if message.get("tool_calls"):
                        # 7.取出工具调用的数据，限制LLM一次只能调用工具
                        filtered_message["tool_calls"] = message.get("tool_calls")[:1]
                else:
                    # 8.非AI消息则基类并存储message
                    logger.warning(f"LLM响应内容无法确认消息角色：{message.get('role')}")
                    filtered_message = message

                # 9.将消息添加到记忆
                await self._add_to_memory([filtered_message])
            except Exception as e:
                # 10.记录日志并睡眠制定的时间
                logger.error(f"调用语言模型发生错误：{str(e)}")
                await asyncio.sleep(self._retry_interval)
                continue

    async def _add_to_memory(self, messages: List[Dict[str, Any]]) -> None:
        """将对应的信息添加到记忆中"""
        # 1.检查记忆的消息列表是否为空，如果是空则需要添加预设prompt作为初始记忆
        if self._memory.empty:
            self._memory.add_message({
                "role": "system",
                "content": self._system_prompt
            })

        # 2.将正常消息添加到记忆中
        self._memory.add_messages(messages)

    async def invoke(self, query: str, format: Optional[str] = None) -> AsyncGenerator[Event, None]:
        """传递消息+响应格式调用层序生成异步迭代内容"""
        # 1.需要判断下是否传递了format
        format = format if format else self._format

        # 2.调用语言模型获取响应内容
        message = await self._invoke_llm(
            [{"role": "user", "content": query}],
            format,
        )

        # 3.
