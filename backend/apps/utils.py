# 公共模块
import hashlib
import jwt
import datetime
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken  # 引入 Simple JWT 的 RefreshToken
from django.contrib.auth.hashers import check_password  # 使用 Django 的密码校验函数
from rest_framework import serializers
from django.views import View
from django.utils import timezone
from django.conf import settings
from apps.models import User, UserLock, Token, Role, Permission, RolePermission, LoginLog, OperationLog, Credential, DomainMonitor, Host, Node, CommandLog, AlertContact, CommandAlert
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
# json
import json
import ipaddress

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
        user.is_authenticated = True  # 手动添加is_authenticated属性
        return (user, None)


# 添加函数用于检查用户是否具有只读权限
def user_has_view_permission(user):
    # 判断用户是否拥有只读权限
    role_permissions = RolePermission.objects.filter(user_id=user.id)
    for rp in role_permissions:
        if rp.permission.code == 'view':
            return True
    return False

from apps.utils import CustomTokenAuthentication
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
import urllib.parse

@database_sync_to_async
def get_user(token_key):
    # Use your CustomTokenAuthentication to get the user
    auth = CustomTokenAuthentication()
    try:
        validated_token = auth.get_validated_token(token_key)
        user = auth.get_user(validated_token)
        return user
    except Exception as e:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract the token from the query string
        query_string = scope['query_string'].decode()
        query_params = urllib.parse.parse_qs(query_string)
        token_list = query_params.get('token', [])
        token = token_list[0] if token_list else None

        if token:
            # Authenticate the user using your CustomTokenAuthentication
            user = await get_user(token)
            scope['user'] = user
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

def is_ip_in_list(ip, ip_list_str):
    """
    检查 IP 是否在 IP 列表中
    支持 IP 地址和 CIDR 格式
    """
    if not ip_list_str:
        return False
    
    ip_addr = ipaddress.ip_address(ip)
    ip_list = [x.strip() for x in ip_list_str.split(',')]
    
    for item in ip_list:
        if item == '*':  # 允许所有 IP
            return True
        try:
            if '/' in item:  # CIDR 格式
                if ip_addr in ipaddress.ip_network(item, strict=False):
                    return True
            else:  # 单个 IP 地址
                if ip_addr == ipaddress.ip_address(item):
                    return True
        except ValueError:
            continue
    return False
