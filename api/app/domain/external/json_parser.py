#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/7 14:47
#Author  :Emcikem
@File    :json_parser.py
"""
from typing import Protocol, Optional, Any, Union, List, Dict


class JsonParser(Protocol):
    """JSON解析器，用于解析Json字符串并修复"""

    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]:
        """调用函数，用于将传递过来的文本进行解析并返回"""
        ...
