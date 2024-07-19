from apps.utils import APIView, Response, User, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, UserRole, Role

# 用户列表视图类，继承自APIView
class UserListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

# 用户列表视图类，继承自APIView
class UserListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回用户列表
        """
        # 获取所有用户并按创建时间排序
        users = User.objects.all().order_by('-create_time')

        # 获取分页参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

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
            user_role = UserRole.objects.filter(user=user).first()
            role_name = user_role.role.role_name if user_role else "无角色"
            description = user_role.role.description if user_role else ""
            role_display = f"{role_name} - {description}" if description else role_name

            data.append({
                'id': index,  # 前端生成的编号
                'username': user.username,
                'name': user.name,
                'role': role_display,  # 角色信息
                'email': user.email,
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
