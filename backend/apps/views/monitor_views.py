from apps.utils import APIView, Response, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, DomainMonitor
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from rest_framework import serializers
from ..scheduler import add_task, remove_task, update_task, pause_task
from ..tasks import DomainMonitorTask
import json

# 域名监控序列化器，用于验证和序列化 DomainMonitor 模型的数据
class DomainMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainMonitor
        fields = '__all__'

class DomainMonitorView(APIView):
    """
    DomainMonitorView 类处理 DomainMonitor 模型的 CRUD 操作，
    并管理域名监控的启用和禁用。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回域名监控列表，支持筛选并提供分页功能。
        """
        # 获取筛选参数
        name = request.GET.get('name', '')
        domain = request.GET.get('domain', '')

        # 获取所有域名监控并按创建时间升序排序
        monitors = DomainMonitor.objects.all().order_by('create_time')

        # 根据筛选参数过滤
        if name:
            monitors = monitors.filter(name__icontains=name)
        if domain:
            monitors = monitors.filter(domain__icontains=domain)

        # 获取分页参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        # 实例化分页器
        paginator = Paginator(monitors, page_size)
        
        # 获取当前页的数据
        current_page_data = paginator.get_page(page)

        # 构建响应数据
        data = []
        for monitor in current_page_data:
            data.append({
                'id': monitor.id,
                'name': monitor.name,
                'domain': monitor.domain,
                'connectivity': monitor.connectivity,
                'status_code': monitor.status_code,
                'redirection': monitor.redirection,
                'time_consumption': monitor.time_consumption,
                # 'dns': monitor.dns,
                'tls_version': monitor.tls_version,
                'http_version': monitor.http_version,
                'certificate_days': monitor.certificate_days,
                'enable': monitor.enable,
                'alert': monitor.alert,
                'monitor_frequency': monitor.monitor_frequency,
                'create_time': monitor.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # 构建分页信息
        pagination = {
            'current_page': current_page_data.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
        }

        # 返回分页后的响应数据
        return Response({
            'result': data,
            'pagination': pagination
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        处理POST请求，用于创建新的域名监控
        """
        serializer = DomainMonitorSerializer(data=request.data)
        if serializer.is_valid():
            monitor = serializer.save()

            # 如果启用了监控，则添加定时任务
            if monitor.enable:
                add_task(
                    DomainMonitorTask,
                    DomainMonitorTask.monitor_domain,
                    str(monitor.id),
                    monitor.name,
                    monitor.monitor_frequency,
                    monitor.id
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        处理PUT请求，更新现有域名监控
        """
        # 根据主键获取域名监控对象，如果不存在则返回404
        monitor = get_object_or_404(DomainMonitor, pk=pk)

        # 使用model_to_dict记录更新前的数据
        before_data = model_to_dict(monitor)

        # 序列化并验证更新的数据
        serializer = DomainMonitorSerializer(monitor, data=request.data, partial=True)
        if serializer.is_valid():
            monitor = serializer.save()

            # 更新定时任务
            if monitor.enable:
                update_task(
                    DomainMonitorTask,
                    DomainMonitorTask.monitor_domain,
                    str(monitor.id),
                    monitor.name,
                    monitor.monitor_frequency,
                    monitor.id
                )
            else:
                pause_task(str(monitor.id))
                
                # 禁用监控时清除特定字段
                monitor.connectivity = False
                monitor.status_code = None
                monitor.redirection = None
                monitor.time_consumption = None
                # monitor.dns = None
                monitor.tls_version = None
                monitor.http_version = None
                monitor.certificate_days = None
                monitor.save()

            # 使用model_to_dict记录更新后的数据
            after_data = model_to_dict(monitor)
            # 返回更新后的数据
            return Response(after_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        处理DELETE请求，删除现有域名监控
        """
        # 根据主键获取域名监控对象，如果不存在则返回404
        monitor = get_object_or_404(DomainMonitor, pk=pk)

        # 使用model_to_dict记录删除前的数据
        monitor_data = model_to_dict(monitor)

        # 移除定时任务
        remove_task(str(monitor.id))

        # 删除监控对象
        monitor.delete()
        # 返回删除前的数据
        return Response(monitor_data, status=status.HTTP_204_NO_CONTENT)
