#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/9 22:01
#Author  :Emcikem
@File    :planner.py
"""
# 规划Agent系统预设prompt
PLANNER_SYSTEM_PROMPT = ""

# 创建Plan规划提示词模版，内部有message+attachments占位符
CREATE_PLANNER_PROMPT = "{message}\n{attachments}"

# 更新Plan规划提示词模板，内部有plan和step占位符
UPDATE_PLANNER_PROMPT = "{plan}\n{step}"
