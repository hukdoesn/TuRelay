from apps.utils import (
    APIView, AlertHistoryLog, CustomTokenAuthentication, 
    IsAuthenticated, status, Paginator, Response
)

class AlertHistoryLogView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 获取所有告警历史记录并按时间倒序排序
        alert_logs = AlertHistoryLog.objects.all()
        
        # 获取分页和筛选参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        username = request.GET.get('username', '')
        hostname = request.GET.get('hostname', '')
        
        # 应用筛选条件
        if username:
            alert_logs = alert_logs.filter(username__icontains=username)
        if hostname:
            alert_logs = alert_logs.filter(hostname__icontains=hostname)

        # 分页处理
        paginator = Paginator(alert_logs, page_size)
        current_page_data = paginator.get_page(page)
        
        # 构建响应数据
        data = []
        for log in current_page_data:
            data.append({
                'id': log.id,
                'username': log.username,
                'hostname': log.hostname,
                'match_type': log.match_type,
                'command': log.command,
                'alert_rule': log.alert_rule,
                'create_time': log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        # 构建分页信息
        pagination = {
            'current_page': current_page_data.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': int(page_size),
        }
        
        return Response({
            'results': data,
            'pagination': pagination
        }, status=status.HTTP_200_OK)