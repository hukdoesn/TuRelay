from apps.utils import (
    APIView, AlertHistoryLog, CustomTokenAuthentication, 
    IsAuthenticated, status, Paginator, Response
)

class AlertHistoryLogView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 获取所有告警历史记录并按时间倒序排序
        alert_logs = AlertHistoryLog.objects.all().order_by('-alert_time')
        
        # 获取分页和筛选参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        alert_name = request.GET.get('alert_name', '')
        alert_contacts = request.GET.get('alert_contacts', '')
        
        # 应用筛选条件
        if alert_name:
            alert_logs = alert_logs.filter(alert_name__icontains=alert_name)
        if alert_contacts:
            alert_logs = alert_logs.filter(alert_contacts__icontains=alert_contacts)

        # 分页处理
        paginator = Paginator(alert_logs, page_size)
        current_page_data = paginator.get_page(page)
        
        # 构建响应数据
        data = []
        for log in current_page_data:
            data.append({
                'id': log.id,
                'alert_name': log.alert_name,
                'alert_rule': log.alert_rule,
                'alert_contacts': log.alert_contacts,
                'alert_time': log.alert_time.strftime('%Y-%m-%d %H:%M:%S'),
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