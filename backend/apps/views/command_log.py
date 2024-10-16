from django.core.paginator import Paginator
from apps.utils import APIView, CustomTokenAuthentication, IsAuthenticated, CommandLog
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

class CommandLogView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        username = request.GET.get('username', '')
        hostname = request.GET.get('hostname', '')

        # 构建查询条件
        query = Q()
        if username:
            query &= Q(username__icontains=username)
        if hostname:
            query &= Q(hosts__icontains=hostname)

        # 查询数据库
        command_logs = CommandLog.objects.filter(query).order_by('-create_time')

        # 分页
        paginator = Paginator(command_logs, page_size)
        current_page = paginator.page(page)

        # 序列化数据
        data = [{
            'id': log.id,
            'username': log.username,
            'command': log.command,
            'hosts': log.hosts,
            'network': log.network,
            'credential': log.credential,
            'create_time': log.create_time.strftime('%Y-%m-%d %H:%M:%S')
        } for log in current_page]

        # 返回结果
        return Response({
            'code': 200,
            'message': '获取命令日志成功',
            'data': {
                'items': data,
                'total': paginator.count,
                'page': page,
                'page_size': page_size
            }
        })
