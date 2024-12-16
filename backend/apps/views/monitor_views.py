from apps.utils import APIView, Response, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, DomainMonitor
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from rest_framework import serializers
from ..scheduler import add_task, remove_task, update_task, pause_task
from ..tasks import DomainMonitorTask
import json
import ssl
import socket
from urllib.parse import urlparse
import logging

logger = logging.getLogger('log')

# 域名监控序列化器，用于验证和序列化 DomainMonitor 模型的数据
class DomainMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainMonitor
        fields = '__all__'

    def validate_domain(self, value):
        """
        验证域名格式和HTTPS支持
        """
        try:
            # 标准化域名
            value = value.strip()
            if value.startswith('http://'):
                raise serializers.ValidationError("不支持HTTP协议，请使用HTTPS或直接输入域名")
            
            # 确保域名使用HTTPS
            if not value.startswith('https://'):
                value = 'https://' + value

            # 解析域名
            parsed_url = urlparse(value)
            hostname = parsed_url.netloc
            
            # 验证SSL证书
            context = ssl.create_default_context()
            try:
                with socket.create_connection((hostname, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        logger.info(f"域名 {value} SSL证书验证成功")
            except (socket.gaierror, socket.timeout) as e:
                logger.error(f"域名 {value} SSL连接失败: {str(e)}")
                raise serializers.ValidationError(f"SSL连接失败: {str(e)}")
            except ssl.SSLError as e:
                logger.error(f"域名 {value} SSL验证失败: {str(e)}")
                raise serializers.ValidationError(f"SSL证书验证失败: {str(e)}")
            
            return value
            
        except Exception as e:
            logger.error(f"域名验证失败: {str(e)}")
            raise serializers.ValidationError(f"域名验证失败: {str(e)}")

class DomainMonitorView(APIView):
    """
    DomainMonitorView 类处理 DomainMonitor 模型的 CRUD 操作，
    并管理域名监控的启用和禁用。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        处理GET请求，如果提供了pk则返回单个站点监控详情，否则返回站点监控列表
        """
        if pk:
            try:
                monitor = get_object_or_404(DomainMonitor, pk=pk)
                data = {
                    'id': monitor.id,
                    'name': monitor.name,
                    'domain': monitor.domain,
                    'connectivity': monitor.connectivity,
                    'status_code': monitor.status_code,
                    'redirection': monitor.redirection,
                    'time_consumption': monitor.time_consumption,
                    'tls_version': monitor.tls_version,
                    'http_version': monitor.http_version,
                    'certificate_days': monitor.certificate_days,
                    'enable': monitor.enable,
                    'alert': monitor.alert,
                    'monitor_frequency': monitor.monitor_frequency,
                    'create_time': monitor.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                return Response(data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"获取监控详情失败: {str(e)}")
                return Response({'error': f'获取监控详情失败: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
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
                    'page_size': int(page_size),
                }

                return Response({
                    'result': data,
                    'pagination': pagination
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"获取监控列表失败: {str(e)}")
                return Response({'error': f'获取监控列表失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        处理POST请求，创建新的域名监控
        """
        try:
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
                    logger.info(f"成功创建域名监控: {monitor.domain}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"创建域名监控失败: {serializer.errors}")
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"创建域名监控时发生错误: {str(e)}")
            return Response({'error': f'创建域名监控失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """
        处理PUT请求，更新现有域名监控
        """
        try:
            monitor = get_object_or_404(DomainMonitor, pk=pk)
            before_data = model_to_dict(monitor)
            
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
                    logger.info(f"成功更新域名监控: {monitor.domain}")
                else:
                    pause_task(str(monitor.id))
                    
                    # 禁用监控时清除特定字段
                    monitor.connectivity = False
                    monitor.status_code = None
                    monitor.redirection = None
                    monitor.time_consumption = None
                    monitor.tls_version = None
                    monitor.http_version = None
                    monitor.certificate_days = None
                    monitor.save()
                    
                    logger.info(f"已暂停域名监控: {monitor.domain}")

                after_data = model_to_dict(monitor)
                return Response(after_data, status=status.HTTP_200_OK)
            else:
                logger.error(f"更新域名监控失败: {serializer.errors}")
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"更新域名监控时发生错误: {str(e)}")
            return Response({'error': f'更新域名监控失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """
        处理DELETE请求，删除现有域名监控
        """
        try:
            monitor = get_object_or_404(DomainMonitor, pk=pk)
            monitor_data = model_to_dict(monitor)
            
            # 移除定时任务
            remove_task(str(monitor.id))
            
            # 删除监控对象
            monitor.delete()
            logger.info(f"成功删除域名监控: {monitor_data['domain']}")
            return Response(monitor_data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"删除域名监控时发生错误: {str(e)}")
            return Response({'error': f'删除域名监控失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
