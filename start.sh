#!/bin/bash

# 启动前端服务
# cd /app/web
# PORT=8080 npm run prod &

# 启动后端服务
cd /app/backend
python3 manage.py runserver 0.0.0.0:8100
