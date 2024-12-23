# 使用 Python 3.9.6 作为基础镜像
FROM python:3.9.6

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    NODE_VERSION=16.16.0 \
    DEBIAN_FRONTEND=noninteractive

# 更换 apt 源为阿里云源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
        && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 Node.js
RUN wget https://nodejs.org/dist/v16.16.0/node-v16.16.0-linux-x64.tar.xz \
    && tar -xf node-v16.16.0-linux-x64.tar.xz -C /usr/local --strip-components=1 \
    && rm node-v16.16.0-linux-x64.tar.xz

# 设置 npm 镜像
RUN npm config set registry http://registry.npmmirror.com

# 设置 pip 镜像
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 复制整个项目
# .dockerignore 文件会自动排除 node_modules 和 migrations
COPY . /app/

# 安装后端依赖
WORKDIR /app/backend
RUN pip install -r requirements.txt

# 安装前端依赖
WORKDIR /app/web
RUN npm install

# 设置启动脚本权限
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 8100 8080

# 设置工作目录
WORKDIR /app

# 启动服务
CMD ["/app/start.sh"]
