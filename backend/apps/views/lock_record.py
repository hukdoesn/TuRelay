from apps.utils import APIView, UserLock, User, CustomTokenAuthentication, IsAuthenticated, status, Paginator, Response

# 用户锁定记录列表视图类，继承自APIView
class LockRecordView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回用户锁定记录列表
        """
        # 获取所有用户锁定记录并按最后尝试时间降序排序
        user_locks = UserLock.objects.all().order_by('-last_attempt_time')

        # 获取分页参数
        page = request.GET.get('page', 1)       # 获取当前页码，默认为第1页
        page_size = request.GET.get('page_size', 10)        # 获取每页显示的记录数，默认为10

        # 获取筛选参数
        username = request.GET.get('username', '')       # 获取操作用户名筛选参数，默认为空字符串
        status_filter = request.GET.get('status', '')    # 获取状态筛选参数，默认为空字符串
        

        # 根据筛选参数过滤用户
        if username:
            user_locks = user_locks.filter(user__username__icontains=username)
        # 根据状态筛选
        if status_filter != '':
            # 如果适用，将 status_filter 转换为整数
            try:
                status_filter = int(status_filter)
                user_locks = user_locks.filter(user__status=status_filter)
            except ValueError:
                # 处理 status_filter 不是有效整数的情况
                pass

        # 实例化分页器
        paginator = Paginator(user_locks, page_size)
        
        # 获取当前页的数据  
        current_page_data = paginator.get_page(page)
        
        # 构建响应数据
        data = []
        for user_lock in current_page_data:
            user_id = user_lock.user_id     # 获取用户的ID
            user = User.objects.get(id=user_id)     # 根据用户ID获取用户对象
            
            data.append({
                'id': user_lock.id,
                'username': user.username,
                'lock_count': user_lock.lock_count,
                'login_count': user_lock.login_count,
                'status': user.status,
                'last_attempt_time': user_lock.last_attempt_time.strftime('%Y-%m-%d %H:%M:%S'),
            })
            
            # 构建分页信息
            pagination = {
                'current_page': current_page_data.number,  # 当前页码
                'total_pages': paginator.num_pages,  # 总页数
                'total_items': paginator.count,  # 总记录数
                'page_size': page_size,  # 每页显示的记录数
            }

        return Response({
            'result': data,
            'pagination': pagination
            }, status=status.HTTP_200_OK)