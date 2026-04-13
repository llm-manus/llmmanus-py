#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2026/4/13 23:12
#Author  :Emcikem
@File    :event.py
"""
from datetime import datetime
from typing import Optional, Any, Dict, Self, Type

from pydantic import BaseModel, Field, ConfigDict

from app.domain.models.event import Event


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