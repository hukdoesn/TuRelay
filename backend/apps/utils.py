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
from apps.models import User, UserLock, Token, Role, Permission, RolePermission, LoginLog, OperationLog, Credential, DomainMonitor, Host
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
# json
import json

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