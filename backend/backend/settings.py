from pathlib import Path
import os
import logging
import time
import datetime
from datetime import timedelta
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read(str(Path(__file__).resolve().parent.parent / 'conf' / 'config.txt'))

# 设置基础目录，通常用于构建项目内的其他路径，如静态文件、数据库文件等
BASE_DIR = Path(__file__).resolve().parent.parent

# 生产环境中应保密的 Django 密钥
SECRET_KEY = 'django-insecure-aq1$o05s3&m=0)yq-j1z_7xu7nk)0v_dp9^(9b9048n&1!^e+^'

# 是否启用调试模式，在生产环境中应设置为False
DEBUG = True

# 允许的主机名列表，对于公开的生产环境需要设置具体的域名或IP地址
ALLOWED_HOSTS = ['admin.ext4.cn', 'localhost', '127.0.0.1', '172.17.103.22']

# Django 应用配置，包括Django自身和第三方应用
INSTALLED_APPS = [
    'django.contrib.admin',   # 管理界面
    'django.contrib.auth',    # 认证系
    'django.contrib.contenttypes', # 内容类型框架
    'django.contrib.sessions', # 会话框架
    'django.contrib.messages', # 消息框架
    'daphne',
    'django.contrib.staticfiles', # 静态文件处理
    'corsheaders',      # 添加 corsheaders 应用，用于处理跨域请求
    'rest_framework', # Django REST framework
    'rest_framework.authtoken', # Token 认证
    'django_apscheduler',
    'apps', # 本地应用
    'channels',     # 添加支持WebSocket的频道
    'channels_redis',
]

# Django 中间件配置，处理请求和响应的钩子框架
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', # 安全相关的中间件
    'django.contrib.sessions.middleware.SessionMiddleware', # 管理网站的会话
    'corsheaders.middleware.CorsMiddleware',        # 将 CorsMiddleware 添加到中间件列表，用于处理跨域请求
    'django.middleware.common.CommonMiddleware', # 管理各种通用任务
    # 'django.middleware.csrf.CsrfViewMiddleware', # 管理跨站请求伪造保护
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 用于用户认证
    'django.contrib.messages.middleware.MessageMiddleware', # 消息中间件，用于cookie和session的消息标签
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # 防点击劫持
    'apps.middleware_log.OperationLogMiddleware',
    'apps.middleware.TokenAuthenticationMiddleware',  # Token 认证中间件
    'apps.middleware.PermissionMiddleware',  # 权限控制中间件，必须在 TokenAuthenticationMiddleware 之后
]

# 项目的URL配置路径
ROOT_URLCONF = 'backend.urls'

# 模板配置，定义了如何加载和渲染模板
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI应用配置，是Python标准的Web服务器网关接口
WSGI_APPLICATION = 'backend.wsgi.application'

# ASGI应用配置
ASGI_APPLICATION = 'backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(config.get('redis', 'host'), config.getint('redis', 'port'))],
        },
    },
}



# 数据库配置，定义了使用的数据库和连接方式
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 指定使用MySQL作为数据库
        'OPTIONS': {
            'read_default_file': str(BASE_DIR / 'conf' / 'config.txt'),  # 从文件取数据库配置
        }
    }
}

# 密码验证器配置，用于增强账户安全性
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST框架的配置，用于控制API认证和权限
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# 基础设置，包括语言、时区等
LANGUAGE_CODE = 'en-us'  # 语言代码
TIME_ZONE = 'Asia/Shanghai' # 设置时区
USE_I18N = True  # 启用Django的国际化支持
USE_L10N = True # 启用本地化

# 启时区支持，USE_TZ 设置为 True 时，django 会使用默认时区 America/Chicago，设置为 False 时，需要配置 TIME_ZONE
USE_TZ = False

# 静态文件服务的URL前缀
STATIC_URL = 'static/'
APPEND_SLASH=False

# 默认的自动段类型，Django 3.2后默认为BigAutoField
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'https://admin.ext4.cn',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://172.17.103.22:8080'
]
CSRF_TRUSTED_ORIGINS = [
    'https://admin.ext4.cn',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://172.17.103.22:8080'
]

# 日志配置，用于应用程序的日志管理
cur_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(os.path.dirname(cur_path), 'logs')  # 修改为logs目录

# 确保日志目录存在
if not os.path.exists(log_path):
    os.makedirs(log_path)

# 命令告警配置
COMMAND_ALERT = {
    'ENABLED': True,
    'LOG_LEVEL': 'WARNING',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {module} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',        # 日志级别，只记录大于等于INFO级别的日志
            'class': 'logging.handlers.TimedRotatingFileHandler',       # 处理器类型按时间切割日志文件
            'filename': os.path.join(log_path, 'turelay.log'),      # 日志文件路径
            'formatter': 'verbose',     # 日志格式
            'when': 'midnight',     # 0点切割
            'interval': 1,      # 切割间隔
            'backupCount': 15,      # 备份天数，超过的文件将被删除
            'encoding': 'utf-8',
            'atTime': datetime.time(0, 0),      # 指定在0点0分进行日志切割
        }
    },
    'loggers': {
        '': {  # 根记录器，捕获所有日志
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apscheduler': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}

# Redis配置
REDIS_HOST = config.get('redis', 'host')
REDIS_PORT = config.getint('redis', 'port')
REDIS_PASSWORD = config.get('redis', 'password')
REDIS_DB = config.getint('redis', 'db')
REDIS_SESSION_DB = config.getint('redis', 'session_db')
REDIS_CHANNEL_LAYER_DB = config.getint('redis', 'channel_layer_db')

# Token相关配置
TOKEN_EXPIRE_MINUTES = 120  # token有效期2小时 (120分钟)
SESSION_TIMEOUT_MINUTES = 60  # 会话超时时间60分钟

# 文件传输相关配置
FILE_TRANSFER = {
    'MAX_UPLOAD_SIZE': 10 * 1024 * 1024 * 1024,  # 10GB 最大上传大小
    'CHUNK_SIZE': 256 * 1024 * 1024,  # 改为 256MB 的传输块大小
    'BUFFER_SIZE': 64 * 1024 * 1024,  # 改为 64MB 的缓冲区大小
    'PROGRESS_UPDATE_INTERVAL': 2,  # 每2%更新一次进度
    'TIMEOUT': SESSION_TIMEOUT_MINUTES * 60,  # 使用会话超时时间作为传输超时时间(秒)
}
