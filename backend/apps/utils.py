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
from rest_framework_simplejwt.tokens import RefreshToken  # 再次确保导入了这个模块
from django.conf import settings
from apps.models import User, UserLock, Token
# from rest_framework.authtoken.models import Token