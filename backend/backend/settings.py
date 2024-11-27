from pathlib import Path
import os
import logging
import time
from datetime import timedelta

# 设置基础目录，通常用于构建项目内的其他路径，如静态文件、数据库文件等
BASE_DIR = Path(__file__).resolve().parent.parent

# 生产环境中应保密的 Django 密钥
SECRET_KEY = 'django-insecure-aq1$o05s3&m=0)yq-j1z_7xu7nk)0v_dp9^(9b9048n&1!^e+^'

# 是否启用调试模式，在生产环境中应设置为False
DEBUG = True

# 允许的主机名列表，对于公开的生产环境需要设置具体的域名或IP地址
ALLOWED_HOSTS = ['172.17.102.132', 'localhost', '192.168.5.29', '192.168.222.86', '127.0.0.1']  # 添加允许的主机名

# Guacamole 服务器配置
GUACAMOLE_URL = 'http://172.17.102.132:8081/guacamole'  # Guacamole 服务器的 URL，需根据实际情况修改
GUACAMOLE_USERNAME = 'guacadmin'  # Guacamole 管理员用户名，默认是 'guacadmin'
GUACAMOLE_PASSWORD = 'guacadmin'  # Guacamole 管理员密码，默认是 'guacadmin'



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

GUACD_HOST = '172.17.103.106'
GUACD_PORT = 4822

# Django 中间件配置，处理请求和响应的钩子框架
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', # 安全相关的中间件
    'django.contrib.sessions.middleware.SessionMiddleware', # 管理网站的会话
    'corsheaders.middleware.CorsMiddleware',        # 将 CorsMiddleware 添加到中间件列表，用于处理跨域请求
    'django.middleware.common.CommonMiddleware', # 管理各种通用任务
    # 'django.middleware.csrf.CsrfViewMiddleware', # 管理跨站请求伪造保护
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 用于用户认证
    'django.contrib.messages.middleware.MessageMiddleware', # 消息中间件，用于cookie和session的消息标签
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # 防止点击劫持
    'apps.middleware_log.OperationLogMiddleware',
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
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}



# 数据库配置，定义了使用的数据库和连接方式
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 指定使用MySQL作为数据库
        'OPTIONS': {
            'read_default_file': str(BASE_DIR / 'conf' / 'config.txt'),  # 从文件读取数据库配置
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

# 默认的自动字段类型，Django 3.2后默认为BigAutoField
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'http://172.17.102.132:8080',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://192.168.5.82:8080',
    'http://192.168.5.29:8080',
    'http://192.168.5.13:8081',
    'http://192.168.222.86:8080',
    'http://192.168.0.104:8080'
]
CSRF_TRUSTED_ORIGINS = [
    'http://172.17.102.132:8080',
    'http://localhost:8080', 
    'http://127.0.0.1:8080',
    'http://172.17.102.34:8080',
    'http://192.168.5.82:8080',
    'http://192.168.5.29:8080',
    'http://192.168.5.13:8081',
    'http://192.168.222.86:8080',
    'http://192.168.0.104:8080'
    ]

# 日志配置，用于应用程序的日志管理
cur_path = os.path.dirname(os.path.realpath(__file__))  # 当前文件的路径
log_path = os.path.join(os.path.dirname(cur_path), 'Log')  # 日志文件存放路径


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,  # 禁用所有已经存在的日志记录器
#     'formatters': {
#         'standard': {
#             'format': '[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] '
#                       '[%(levelname)s]- %(message)s'  # 定义日志输出格式
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'  # 简化的日志输出格式
#         },
#     },
#     'filters': {
#         # 这里可以定义过滤器，目前为空
#     },
#     'handlers': {
#         'default': {
#             'level': 'INFO',  # 记录DEBUG及以上级别的日志
#             'class': 'logging.handlers.RotatingFileHandler',  # 日志轮转方式，当文件满时自动轮转
#             'filename': os.path.join(log_path, 'turelay.log'),  # 日志文件位置
#             'maxBytes': 1024 * 1024 * 5,  # 日志文件大小，这里设置为5MB
#             'backupCount': 5,  # 日志文件备份数量
#             'formatter': 'standard',  # 使用标准格式化器
#             'encoding': 'utf-8',  # 文件编码
#         },
#         'error': {
#             'level': 'ERROR',  # 只记录ERROR级别及以上的日志
#             'class': 'logging.handlers.RotatingFileHandler',  # 日志轮转方式
#             'filename': os.path.join(log_path, 'error-{}.log'.format(time.strftime('%Y-%m'))),  # 日志文件位置
#             'maxBytes': 1024 * 1024 * 5,  # 文件大小为5MB
#             'backupCount': 5,  # 备份数量为5
#             'formatter': 'standard',  # 使用标准格式器
#             'encoding': 'utf-8',  # 设置文件编码
#         },
#         'console': {
#             'level': 'INFO',  # 控制台输出所有DEBUG级别及以上的日志
#             'class': 'logging.StreamHandler',  # 使用流处理器，输出到控制台
#             'formatter': 'standard'  # 使用标准格式器
#         },
#         'info': {
#             'level': 'INFO',  # 记录INFO级别及以上的日志
#             'class': 'logging.handlers.RotatingFileHandler',  # 使用文件轮转方式
#             'filename': os.path.join(log_path, 'info-{}.log'.format(time.strftime('%Y-%m'))),  # 日志文件位置
#             'maxBytes': 1024 * 1024 * 5,  # 文件大小为5MB
#             'backupCount': 5,  # 备份数量为5
#             'formatter': 'standard',  # 使用标准格式器
#             'encoding': 'utf-8',  # 设置文件编码
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['default', 'console'],  # django日志使用默认和控制台handler
#              'level': 'DEBUG',  # 记录DEBUG及以上级别的日志
#             'propagate': False  # 不向上级传播日志
#         },
#         'log': {
#             'handlers': ['error', 'info', 'console', 'default'],  # 自定义日志记录器，包括错误、信息、控制台和默认
#             'level': 'DEBUG',  # 记录DEBUG级别及以上的日志
#             'propagate': True  # 向上级传播日志
#         },
#         'apscheduler': {
#             'handlers': ['default', 'console'],
#             'level': 'INFO',  # 确保捕获APScheduler日志
#             'propagate': False
#         },
#     }
# }

# 命令告警配置
COMMAND_ALERT = {
    'ENABLED': True,
    'LOG_LEVEL': 'WARNING',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'log': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
