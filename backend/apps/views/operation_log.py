from apps.utils import APIView, OperationLog, Response, User, status, Paginator, CustomTokenAuthentication, IsAuthenticated, json

# 操作日志列表视图类，继承自APIView
class OperationLogView(APIView):
    # 配置认证类，使用自定义的令牌认证
    authentication_classes = [CustomTokenAuthentication]
    # 配置权限类，只有已认证用户才能访问此视图
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回操作日志列表
        """
        # 获取所有操作日志并按创建时间降序排序
        operation_logs = OperationLog.objects.all().order_by('-create_time')

        # 获取分页参数
        page = request.GET.get('page', 1)       # 获取当前页码，默认为第1页
        page_size = request.GET.get('page_size', 10)        # 获取每页显示的记录数，默认为10

        # 获取筛选参数
        username = request.GET.get('username', '')      # 获取操作用户名筛选参数，默认为空字符串
        request_method = request.GET.get('request_method', '')     # 获取操作类型筛选参数，默认为空字符串

        # 根据筛选参数过滤操作日志
        if username:
            operation_logs = operation_logs.filter(user__username__icontains=username)        # 根据操作用户名进行筛选，不区分大小写
        if request_method:
            # 使用 iregex 进行不区分大小写的正则匹配，确保完全匹配
            operation_logs = operation_logs.filter(request_method__iregex=f'^{request_method}$')     # 使用正则表达式进行不区分大小写的精确匹配

        # 实例化分页器
        paginator = Paginator(operation_logs, page_size)

        # 获取当前页的数据
        current_page_data = paginator.get_page(page)

        # 构建响应数据
        data = []
        for operation_log in current_page_data:
            user_id = operation_log.user_id  # 获取用户的ID
            user = User.objects.get(id=user_id)  # 根据用户ID获取用户对象
            

            data.append({
                'id': operation_log.id,
                'username': user.username,  # 根据用户ID获取用户名
                'module': operation_log.module,
                'request_interface': operation_log.request_interface,
                'request_method': operation_log.request_method,
                'ip_address': operation_log.ip_address,
                'before_change': operation_log.before_change,
                'after_change': operation_log.after_change,
                'create_time': operation_log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # 构建分页信息
        pagination = {
            'current_page': current_page_data.number,  # 当前页码
            'total_pages': paginator.num_pages,  # 总页数
            'total_items': paginator.count,  # 总记录数
            'page_size': page_size,  # 每页显示的记录数
        }

        # 返回响应数据
        return Response({
            'result': data, 
            'pagination': pagination
        }, status=status.HTTP_200_OK)
