#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/11/29 21:18
#Author  :Emcikem
@File    :app_config.py
"""
from enum import Enum
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LLMConfig(BaseModel):
    """语言模型配置"""
    base_url: str = "https://api.deepseek.com"  # 基础URL地址
    api_key: str = ""  # APi秘钥
    model_name: str = "deepseek-reasoner"  # 推理模型让给传递了tools底层会自动切换到deepseek-chat
    temperature: float = Field(default=0.7)  # 温度
    max_tokens: int = Field(default=8192, ge=0)  # 最大输出token数


class AgentConfig(BaseModel):
    """Agent通用配置"""
    max_iterations: int = Field(default=100, gt=0, le=100)  # 最大迭代次数
    max_retries: int = Field(default=3, ge=1, le=10)  # LLM/工具最大重试次数
    max_search_result: int = Field(default=10, ge=1, le=30)  # 最大搜索结果数


class MCPTransport(str, Enum):
    """MCP传输类型枚举"""
    STDIO = "stdio"  # 本地输入输出
    SSE = "sse"  # 流式事件传输
    STREAMABLE_HTTP = "streamable_htp"  # 可流式的HTTP


class MCPServerConfig(BaseModel):
    """MCP单条服务器配置"""
    # 通用字段配置
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP  # 传输协议
    enabled: bool = True  # 是否开启
    description: Optional[str] = None  # MCP服务的描述
    env: Optional[Dict[str, Any]] = None  # 环境变量

    # stdio配置
    command: Optional[str] = None  # 启动命令
    args: Optional[List[str]] = None  # 命令参数

    # streamable_http与sse配置
    url: Optional[str] = None  # MCP服务的URL地址
    headers: Optional[Dict[str, str]] = None  # headers请求头

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_cmp_server_config(self):
        """校验mcp_server_config的相关信息，包含url+command"""
        # 1.判断transport是否为sse/streamable_http
        if self.transport in [MCPTransport.SSE, MCPTransport.STREAMABLE_HTTP]:
            # 2.这两种传输方式需要判断url是否传递
            if not self.url:
                raise ValueError("在sse或streamable_http传输协议中必须传递url")

        # 3.判断transport是否为stdio类型
        if self.transport == MCPTransport.STDIO:
            # 4.判断command也就是启动命令是否传递
            if not self.command:
                raise ValueError("在stdio模式下必须传递command")

        return self


class MCPConfig(BaseModel):
    """应用MCP配置"""
    mcpServers: Dict[str, MCPServerConfig] = Field(default_factory=dict)  # mcp服务

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class AppConfig(BaseModel):
    """应用配置信息，包含Agent配置、LLM提供商、A2A网络、MCP服务配置等"""
    llm_config: LLMConfig  # 语言模型配置
    agent_config: AgentConfig  # Agent通用配置
    mcp_config: MCPConfig  # MCP服务配置

    # Pydantic配置，允许传递额外的字段初始化
    model_config = ConfigDict(extra="allow")
