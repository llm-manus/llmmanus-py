#!/bin/bash

# 启动uvicorn运行服务（使用exec让uvicorn成为主线程）
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 5