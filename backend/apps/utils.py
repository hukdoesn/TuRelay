# 现有的导入
import hashlib
import jwt
import datetime
import redis
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from django.views import View
from django.utils import timezone
from django.conf import settings
from apps.models import (
    User, UserLock, Token, Role, Permission, RolePermission, 
    LoginLog, OperationLog, Credential, DomainMonitor, 
    Host, Node, CommandLog, AlertContact, CommandAlert
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import json
import ipaddress
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
import urllib.parse
from datetime import timedelta

# 会话管理类
class SessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_SESSION_DB,
            decode_responses=True
        )
    
    def set_session(self, token, user_id):
        """
        设置会话，同时设置两个过期时间：
        1. 会话超时时间（短期，用于检测用户活动）
        2. Token 过期时间（长期，用于控制登录有效期）
        """
        # 设置会话数据
        session_key = f"session:{token}"
        token_key = f"token:{token}"
        
        # 存储用户会话信息，设置会话超时时间
        self.redis_client.setex(
            session_key,
            timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES),
            user_id
        )
        
        # 存储 token 信息，设置 token 过期时间
        self.redis_client.setex(
            token_key,
            timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
            user_id
        )
    
    def update_session(self, token):
        """
        更新会话活动时间
        只更新会话超时时间，不更新 token 过期时间
        """
        session_key = f"session:{token}"
        token_key = f"token:{token}"
        
        # 检查 token 是否已过期
        if not self.redis_client.exists(token_key):
            return False
            
        # 检查并更新会话时间
        if self.redis_client.exists(session_key):
            self.redis_client.expire(
                session_key,
                timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
            )
            return True
        return False
    
    def get_session(self, token):
        """
        获取会话信息
        同时检查 token 和会话是否有效
        """
        session_key = f"session:{token}"
        token_key = f"token:{token}"
        
        # 首先检查 token 是否有效
        if not self.redis_client.exists(token_key):
            return None
            
        # 然后检查会话是否有效
        return self.redis_client.get(session_key)
    
    def remove_session(self, token):
        """
        删除会话和 token
        """
        self.redis_client.delete(f"session:{token}", f"token:{token}")
    
    def get_active_sessions_count(self):
        """
        获取活跃会话数量
        只统计有效的会话数量
        """
        return len(self.redis_client.keys("session:*"))

# 创建全局会话管理器实例
session_manager = SessionManager()

# 自定义Token认证类
class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('未提供Token')

        try:
            token_obj = Token.objects.get(token=token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('无效的Token')

        user = token_obj.user
        user.is_authenticated = True
        return (user, None)

# 检查用户权限函数
def user_has_view_permission(user):
    role_permissions = RolePermission.objects.filter(user_id=user.id)
    for rp in role_permissions:
        if rp.permission.code == 'view':
            return True
    return False

@database_sync_to_async
def get_user(token_key):
    auth = CustomTokenAuthentication()
    try:
        validated_token = auth.get_validated_token(token_key)
        user = auth.get_user(validated_token)
        return user
    except Exception as e:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        query_params = urllib.parse.parse_qs(query_string)
        token_list = query_params.get('token', [])
        token = token_list[0] if token_list else None

        if token:
            user = await get_user(token)
            scope['user'] = user
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

def is_ip_in_list(ip, ip_list_str):
    """检查 IP 是否在 IP 列表中"""
    if not ip_list_str:
        return False
    
    ip_addr = ipaddress.ip_address(ip)
    ip_list = [x.strip() for x in ip_list_str.split(',')]
    
    for item in ip_list:
        if item == '*':
            return True
        try:
            if '/' in item:
                if ip_addr in ipaddress.ip_network(item, strict=False):
                    return True
            else:
                if ip_addr == ipaddress.ip_address(item):
                    return True
        except ValueError:
            continue
    return False
