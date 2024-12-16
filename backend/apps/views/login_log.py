from apps.utils import APIView, LoginLog, CustomTokenAuthentication, IsAuthenticated, status, Paginator, Response

# 登录日志列表视图类，继承自APIView
class LoginLogView(APIView):
    # 配置认证类，使用自定义的令牌认证
    authentication_classes = [CustomTokenAuthentication]
    # 配置权限类，只有已认证用户才能访问此视图
    permission_classes = [IsAuthenticated]

    """
    处理GET请求，返回登录日志列表
    """
    def get(self, request):
        # 获取所有日志并且按照登录时间来排序，最新的登录日志在最前面
        login_logs = LoginLog.objects.all().order_by('-login_time')
        
        # 获取分页参数
        page = request.GET.get('page', 1)  # 获取当前页码，默认为第1页
        page_size = request.GET.get('page_size', 10)  # 获取每页显示的记录数，默认为10
        
        # 获取筛选参数
        username = request.GET.get('username', '')  # 获取用户名筛选参数，默认为空字符串
        client_ip = request.GET.get('client_ip', '')  # 获取客户端IP筛选参数，默认为空字符串
        
        # 根据筛选参数过滤日志
        if username:
            login_logs = login_logs.filter(username__icontains=username)  # 根据用户名进行模糊匹配筛选
            print(login_logs)
        if client_ip:
            login_logs = login_logs.filter(client_ip__icontains=client_ip)  # 根据客户端IP进行模糊匹配筛选

        # 实例化分页器
        paginator = Paginator(login_logs, page_size)
        
        # 获取当前页的数据
        current_page_data = paginator.get_page(page)
        
        # 构建响应数据
        data = []
        for log in current_page_data:
            data.append({
                'id': log.id,
                'username': log.username,
                'client_ip': log.client_ip,
                'login_status': int(log.login_status),
                'reason': log.reason,
                'browser_info': log.browser_info,
                'os_info': log.os_info,
                'login_time': log.login_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化登录时间
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
            'results': data,
            'pagination': pagination
        }, status=status.HTTP_200_OK)
