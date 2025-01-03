from apps.utils import APIView, Response, User, UserLock, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, Role, Permission, RolePermission, user_has_view_permission, Token
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.forms.models import model_to_dict
# from django.contrib.auth.models import Token

# 用户创建序列化器，用于验证创建用户的请求数据
class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    name = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)
    mobile = serializers.CharField(max_length=11)
    email = serializers.EmailField()
    role = serializers.IntegerField()
    permissions = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True
    )
    status = serializers.BooleanField()
    mfa_level = serializers.IntegerField(default=0)

    def validate_status(self, value):
        # 将 True 转换为 0，将 False 转换为 1
        return 0 if value else 1

    def validate_mfa_level(self, value):
        if value not in [0, 1]:
            raise ValidationError("MFA认证等级必须是0或1")
        return value

# 用户序列化器，用于验证创建和更新用户的请求数据
class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    name = serializers.CharField(max_length=150)
    mobile = serializers.CharField(max_length=11)
    email = serializers.EmailField()
    role = serializers.IntegerField()
    permissions = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True
    )
    
    status = serializers.BooleanField(required=False)  # 设置为可选字段
    mfa_level = serializers.IntegerField(default=0)

    def validate_status(self, value):
        # 将 True 转换为 0，将 False 转换为 1
        return 0 if value else 1

    def validate_mfa_level(self, value):
        if value not in [0, 1]:
            raise ValidationError("MFA认证等级必须是0或1")
        return value

# 定义新的APIView类，用于获取角色和权限数据
class RolesPermissionsView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回角色和权限数据
        """
        roles = Role.objects.all().values('id', 'role_name')
        permissions = Permission.objects.all().values('id', 'name')
        return Response({
            'roles': list(roles),
            'permissions': list(permissions)
        }, status=status.HTTP_200_OK)

# 重置密码序列化器，用于验证重置密码的请求数据
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=128)

# 用户列表视图类，继承自APIView
class UserListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回用户列表
        """
        # 获取所有用户并按创建时间升序排序
        users = User.objects.all().order_by('create_time')

        # 获取分页参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        
        # 获取筛选参数
        username = request.GET.get('username', '')
        email = request.GET.get('email', '')
        
        # 根据筛选参数过滤用户
        if username:
            users = users.filter(username__icontains=username)
        if email:
            users = users.filter(email__icontains=email)

        # 实例化分页器
        paginator = Paginator(users, page_size)
        try:
            users_page = paginator.page(page)
        except PageNotAnInteger:
            users_page = paginator.page(1)
        except EmptyPage:
            users_page = paginator.page(paginator.num_pages)

        # 构建响应数据
        data = []
        for index, user in enumerate(users_page, start=1):
            # 获取用户的角色信息
            role_permissions = RolePermission.objects.filter(user=user)
            role_display = role_permissions[0].role.role_name if role_permissions.exists() else "无角色"
            description = role_permissions[0].role.description if role_permissions.exists() else ""
            role_display = f"{role_display} - {description}" if description else role_display
            
            # 获取与角色关联的权限信息
            permission_details = [{'id': rp.permission.id, 'name': rp.permission.name} for rp in role_permissions]

            data.append({
                'id': index,  # 前端生成的编号
                'username': user.username,
                'name': user.name,
                'role': role_display,  # 角色信息
                'permissions': permission_details,  # 权限信息
                'email': user.email,
                'mobile': user.mobile,
                'status': user.status,
                'create_time': user.create_time,
                'mfa_level': user.mfa_level,
            })

        # 返回分页后的响应数据
        return Response({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': users_page.number,
            'results': data
        }, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        """
        处理GET请求，返回用户详细信息
        如果提供了username参数，则通过username查找
        如果没有提供username，则返回当前登录用户的信息
        """
        try:
            if username:
                user = User.objects.get(username=username)
            else:
                # 获取当前登录用户
                user = request.user
                
            role_permissions = RolePermission.objects.filter(user=user)
            role_display = role_permissions[0].role.role_name if role_permissions.exists() else "无角色"
            description = role_permissions[0].role.description if role_permissions.exists() else ""
            role_display = f"{role_display} - {description}" if description else role_display

            permission_details = [{'id': rp.permission.id, 'name': rp.permission.name} for rp in role_permissions]

            user_data = {
                'username': user.username,
                'name': user.name,
                'role': role_display,
                'permissions': permission_details,
                'email': user.email,
                'mobile': user.mobile,
                'status': user.status,
                'create_time': user.create_time,
                'mfa_level': user.mfa_level,
                'last_login': user.login_time,  # 添加最后登录时间
            }
            return Response(user_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, username):
        """
        处理DELETE请求，根据用户名删除用户
        """
        try:
            # 查找用户
            user = User.objects.get(username=username)
            user_data = model_to_dict(user)     # 将用户数据转换为字典，记录删除前的状态
            
            # 删除与用户相关的RolePermission记录
            RolePermission.objects.filter(user=user).delete()
            
            # 删除用户
            user.delete()
            return Response(user_data, status=status.HTTP_204_NO_CONTENT)  # 返回完整的用户信息
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, username):
        """
        处理PATCH请求，根据用户名切换用户状态
        """
        try:
            # 查找用户
            user = User.objects.get(username=username)
            before_data = model_to_dict(user)  # 记录更新前的数据
            # 获取新的状态值
            new_status = request.data.get('status')
            user.status = new_status  # 更新状态
            
            # 获取或创建用户锁定记录
            user_lock, created = UserLock.objects.get_or_create(user=user)
            
            # 解锁用户时重置登录尝试次数
            user_lock.login_count = 0
            user_lock.save()

            # 检查并删除用户的 token
            if new_status:  # 如果锁定用户，尝试清除其token
                if hasattr(user, 'token'):  # 检查用户是否有token属性
                    user.token.delete()
            user.save()  # 保存更改
            status_text = "禁用" if new_status else "启用"
            after_data = model_to_dict(user)  # 记录更新后的数据
            return Response(after_data, status=status.HTTP_200_OK)  # 返回完整的更新后用户信息
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 其他异常处理
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, username=None):
        """
        处理POST请求，用于重置密码
        如果提供了username参数，则重置指定用户的密码
        如果没有提供username，则重置当前登录用户的密码
        """
        try:
            if username:
                target_user = User.objects.get(username=username)
            else:
                # 获取当前登录用户
                target_user = request.user

            # 验证新密码
            new_password = request.data.get('new_password')
            if not new_password:
                return Response({"detail": "必须提供新密码"}, status=status.HTTP_400_BAD_REQUEST)
            if len(new_password) < 6:
                return Response({"detail": "密码长度不能小于6个字符"}, status=status.HTTP_400_BAD_REQUEST)

            # 更新密码
            target_user.password = make_password(new_password)
            target_user.save()

            # 清除目标用户的所有token和会话
            from apps.utils import session_manager
            tokens = Token.objects.filter(user=target_user)
            for token in tokens:
                # 删除Redis中的会话
                session_manager.remove_session(token.token)
                # 删除数据库中的token
                token.delete()

            # 如果是用户修改自己的密码，返回特殊标记
            is_self_update = target_user == request.user
            return Response({
                "detail": "密码重置成功",
                "is_self_update": is_self_update
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(APIView):
    def post(self, request):
        """
        处理创建用户的请求
        """
        try:
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                role = Role.objects.get(id=validated_data['role'])

                # 检查角色是否为"管理员"
                if role.role_name.lower() == 'administrator':
                    permissions = Permission.objects.filter(id=1)
                else:
                    permissions = Permission.objects.filter(id__in=validated_data['permissions'])
                
                # 创建用户，只设置 mfa_level
                user = User.objects.create(
                    username=validated_data['username'],
                    name=validated_data['name'],
                    mobile=validated_data['mobile'],
                    password=make_password(validated_data['password']),
                    email=validated_data['email'],
                    status=validated_data['status'],
                    mfa_level=validated_data['mfa_level']  # 只设置 mfa_level
                )
                
                # 分配角色和权限
                for permission in permissions:
                    RolePermission.objects.create(user=user, role=role, permission=permission)

                # 移除 otp_secret_key 后返回用户信息
                user_data = model_to_dict(user)
                if 'otp_secret_key' in user_data:
                    del user_data['otp_secret_key']
                    
                return Response(user_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(APIView):
    def put(self, request, username):
        """
        处理PUT请求，更新用户信息
        """
        try:
            user = User.objects.get(username=username)
            serializer = UserUpdateSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                
                # 更新基本信息
                user.username = validated_data['username']
                user.name = validated_data['name']
                user.mobile = validated_data['mobile']
                user.email = validated_data['email']
                user.mfa_level = validated_data['mfa_level']  

                # 如果MFA等级设置为0（关闭），清空otp_secret_key
                if validated_data['mfa_level'] == 0:
                    user.otp_secret_key = None

                # 更新用户角色和权限
                role = Role.objects.get(id=validated_data['role'])
                RolePermission.objects.filter(user=user).delete()

                if role.role_name.lower() == 'administrator':
                    permissions = Permission.objects.filter(id=1)
                else:
                    permissions = Permission.objects.filter(id__in=validated_data['permissions'])
                
                for permission in permissions:
                    RolePermission.objects.create(user=user, role=role, permission=permission)

                user.save()
                
                # 移除 otp_secret_key 后返回用户信息
                user_data = model_to_dict(user)
                if 'otp_secret_key' in user_data:
                    del user_data['otp_secret_key']
                    
                return Response(user_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Role.DoesNotExist:
            return Response({"detail": "角色未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
