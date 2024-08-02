from apps.utils import APIView, Response, User, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, Role, Permission, RolePermission, user_has_view_permission
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    def validate_status(self, value):
        # 将 True 转换为 0，将 False 转换为 1
        return 0 if value else 1

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

    def validate_status(self, value):
        # 将 True 转换为 0，将 False 转换为 1
        return 0 if value else 1

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

    def get(self, request, username):
        """
        处理GET请求，返回用户详细信息
        """
        try:
            user = User.objects.get(username=username)
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
            
            # 删除与用户相关的RolePermission记录
            RolePermission.objects.filter(user=user).delete()
            
            # 删除用户
            user.delete()
            return Response({"detail": "用户删除成功"}, status=status.HTTP_204_NO_CONTENT)
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
            # 获取新的状态值
            new_status = request.data.get('status')
            user.status = new_status  # 更新状态

            # 检查并删除用户的 token
            if new_status:  # 如果锁定用户，尝试清除其token
                if hasattr(user, 'token'):  # 检查用户是否有token属性
                    user.token.delete()
            user.save()  # 保存更改
            status_text = "禁用" if new_status else "启用"
            return Response({"detail": f"用户{status_text}成功"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 其他异常处理
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, username=None):
        """
        处理POST请求，用于创建新用户或重置密码
        """
        if username:
            return self.reset_password(request, username)
        else:
            return self.create_user(request)

    def reset_password(self, request, username):
        """
        处理重置密码的请求
        """
        try:
            user = User.objects.get(username=username)
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                new_password = serializer.validated_data.get('new_password')
                user.password = make_password(new_password)
                user.save()
                return Response({"detail": "密码重置成功"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        处理创建用户的请求
        """
        try:
            print(request.data)  # 打印请求数据以调试
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                role = Role.objects.get(id=validated_data['role'])
                permissions = Permission.objects.filter(id__in=validated_data['permissions'])
                user = User.objects.create(
                    username=validated_data['username'],
                    name=validated_data['name'],
                    mobile=validated_data['mobile'],
                    password=make_password(validated_data['password']),
                    email=validated_data['email'],
                    status=validated_data['status']  # 直接使用验证后的 status
                )
                for permission in permissions:
                    RolePermission.objects.create(user=user, role=role, permission=permission)
                return Response({"detail": "用户创建成功"}, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)  # 打印序列化器错误信息以调试
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))  # 打印异常信息以调试
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, username):
        """
        处理PUT请求，更新用户信息
        """
        try:
            # 查找用户
            user = User.objects.get(username=username)
            serializer = UserUpdateSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                user.username = validated_data['username']
                user.name = validated_data['name']
                user.mobile = validated_data['mobile']
                user.email = validated_data['email']

                # 更新用户角色
                role = Role.objects.get(id=validated_data['role'])

                # 更新用户权限
                RolePermission.objects.filter(user=user).delete()
                permissions = Permission.objects.filter(id__in=validated_data['permissions'])
                for permission in permissions:
                    RolePermission.objects.create(user=user, role=role, permission=permission)

                user.save()
                return Response({"detail": "用户信息更新成功"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Role.DoesNotExist:
            return Response({"detail": "角色未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
