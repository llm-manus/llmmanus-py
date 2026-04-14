#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/4/13 23:12
#Author  :Emcikem
@File    :event.py
"""
from datetime import datetime
from typing import Optional, Any, Dict, Self, Type, Literal, List, Union

from pyasn1_modules.rfc5280 import CommonName
from pydantic import BaseModel, Field, ConfigDict

from app.domain.models.event import Event, StepEvent, PlanEvent, ToolEventStatus, ToolEvent, WaitEvent
from app.domain.models.file import File
from app.domain.models.plan import ExecutionStatus


class BaseEventData(BaseModel):
    """基础事件数据"""
    id: Optional[str] = None # 事件id
    created_at: datetime = Field(default_factory=datetime.now) # 事件时间

    # pydantic v2写法，序列化时将datetime转换为时间戳
    model_config = ConfigDict(json_encoders={
        datetime: lambda v: int(v.timestamp()),
    })

    @classmethod
    def base_event_data(cls, event: Event) -> Dict[str, Any]:
        """类方法，用于将事件Domain模型转换成基础事件数据字典"""
        return {
            "id": event.id,
            "created_at": int(event.created_at.timestamp()),
        }

    @classmethod
    def from_event(cls, event: Event) -> Self:
        """从事件Domain模型中构建基础事件数据"""
        return cls(
            **cls.base_event_data(event),
            **event.model_dump(mode="json", exclude={"id", "type", "created_at"})
        )

class BaseSSEEvent(BaseModel):
    """基础流式事件数据类型"""
    event: str # 事件类型
    data: BaseEventData # 数据

    @classmethod
    def from_event(cls, event: Event) -> Self:
        """将事件Domain模型转换成基础流式事件"""
        # 1.获取事件数据类型，如果没有则使用基础事件数据BaseEventData
        data_class = Type[BaseEventData] = cls.__annotations__.get("data", BaseEventData)

        # 2.调用构造函数完成初始化
        return cls(
            event=event.type,
            data=data_class.from_event(event),
        )

class CommonEventData(BaseEventData):
    """通用事件数据，让结构允许填充额外的数据"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: int(v.timestamp()),
        },
        extra="allow",
    )

class CommonSSEEvent(BaseSSEEvent):
    """通用事件"""
    event: str
    data: CommonEventData

class MessageEventData(BaseEventData):
    """消息事件数据"""
    role: Literal["user", "assistant"] = "assistant"
    message: str = ""
    attachments: List[File] = Field(default_factory=list)

class MessageSSEEvent(BaseSSEEvent):
    """流式消息事件数据响应结构"""
    event: Literal["message"] = "message"
    data: MessageEventData

    @classmethod
    def from_event(cls, event: Event) -> Self:
        return cls(
            data=MessageEventData(
                **BaseEventData.base_event_data(event),
                role=event.role,
                message=event.message,
                attachments=event.attachments
            )
        )

class TitleEventData(BaseEventData):
    """标题事件数据"""
    title: str

class TitleSSEEvent(BaseSSEEvent):
    """标题流式事件"""
    event: Literal["title"] = "title"
    data: TitleEventData

class StepEventData(BaseEventData):
    """步骤事件数据"""
    id: str # 步骤id
    status: ExecutionStatus # 步骤执行状态
    description: str # 步骤描述

class StepSSEEvent(BaseSSEEvent):
    """步骤流式事件"""
    event: Literal["step"] = "step"
    data: StepEventData

class PlanEventData(BaseEventData):
    """计划事件数据"""
    steps: List[StepEventData]

class PlanSSEEvent(BaseSSEEvent):
    """计划流式事件"""
    event: Literal["plan"] = "plan"
    data: PlanEventData

    @classmethod
    def from_event(cls, event: PlanEvent) -> Self:
        return cls(
            data=PlanEventData(
                **BaseEventData.base_event_data(event),
                steps=[
                    StepEventData(
                        **BaseEventData.base_event_data(event),
                        id=step.id,
                        status=step.status,
                        description=step.description
                    )
                    for step in event.plan.steps
                ]
            )
        )

class ToolEventData(BaseEventData):
    """工具事件数据"""
    tool_call_id: str # 工具调用id
    name: str # 工具箱名字
    status: ToolEventStatus # 工具状态
    function: str # 工具名字
    args: Dict[str, Any] # 工具参数
    content: Optional[Any] = None

class ToolSSEEvent(BaseSSEEvent):
    """工具流式事件"""
    event: Literal["tool"] = "tool"
    data: ToolEventData

    @classmethod
    def from_event(cls, event: ToolEvent) -> Self:
        return cls(
            data=ToolEventData(
                **BaseEventData.base_event_data(event),
                tool_call_id=event.tool_call_id,
                name=event.tool_name,
                status=event.status,
                function=event.function_name,
                args=event.function_args,
                content=event.function_result,
            )
        )

class DoneSSEEvent(BaseSSEEvent):
    """停止流式输入流式事件"""
    event: Literal["done"] = "done"

class WaitSSEEvent(BaseSSEEvent):
    """等待人类流式输入流式事件"""
    event: Literal["wait"] = "wait"


class ErrorEventData(BaseSSEEvent):
    """错误事件数据"""
    error: str

class ErrorSSEEvent(BaseSSEEvent):
    """错误流式事件"""
    event: Literal["error"] = "error"
    data: ErrorEventData

# 定义Agent流式事件类型集合
AgentSSEEvent = Union[
    CommonSSEEvent,
    MessageSSEEvent,
    TitleSSEEvent,
    StepSSEEvent,
    PlanSSEEvent,
    ToolSSEEvent,
    DoneSSEEvent,
    ErrorSSEEvent,
    WaitSSEEvent,
]

