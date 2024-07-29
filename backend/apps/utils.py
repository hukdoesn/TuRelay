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
from apps.models import User, UserLock, Token, UserRole, Role, Permission, RolePermission, LoginLog
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

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
