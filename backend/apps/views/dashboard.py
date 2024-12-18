from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from collections import defaultdict
from django.db import models
from django.conf import settings

from ..models import (
    Host, 
    User, 
    CommandAlert, 
    UserLock,
    LoginLog,
    DomainMonitor,
    Token,
    AlertHistoryLog
)
# from apps.utils.session import session_manager
from apps.utils import session_manager

@api_view(['GET'])
def dashboard_statistics(request):
    """
    获取仪表盘统计数据的视图函数
    """
    try:
        # 获取在线会话数量
        online_sessions = session_manager.get_active_sessions_count()

        # 获取基础统计数据
        statistics = {
            'hostCount': Host.objects.count(),
            'userCount': User.objects.count(),
            'alertCount': CommandAlert.objects.count(),
            'lockedUserCount': UserLock.objects.filter(lock_count__gt=0).count(),
            'onlineSessionCount': online_sessions,
            'failedLoginCount': LoginLog.objects.filter(login_status=False).count(),
            'assetCount': Host.objects.count(),  # 可以加上其他资产类型
            'websiteCount': DomainMonitor.objects.count(),
        }
        
        # 获取主机类型分布 - 只统计Linux和Windows
        host_types = {
            'linux': Host.objects.filter(operating_system='Linux').count(),
            'windows': Host.objects.filter(operating_system='Windows').count()
        }
        
        # 获取最近7天的登录统计 - 使用聚合查询优化
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        # 使用Django ORM的聚合功能按日期分组统计
        daily_logins = LoginLog.objects.filter(
            login_time__date__gte=start_date,
            login_time__date__lte=end_date,
            login_status=True
        ).annotate(
            date=TruncDate('login_time')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # 构建包含所有日期的数据(包括没有登录记录的日期)
        date_counts = {item['date']: item['count'] for item in daily_logins}
        dates = []
        counts = []
        
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%m-%d'))
            counts.append(date_counts.get(current_date, 0))
            current_date += timedelta(days=1)
            
        login_stats = {
            'dates': dates,
            'counts': counts
        }
        
        # 获取最近登录失败记录
        recent_logins = LoginLog.objects.filter(
            login_status=False  # 只获取失败记录
        ).order_by('-login_time')[:5].values(
            'username', 
            'login_time', 
            'client_ip',
            'reason'  # 添加失败原因字段
        )
        
        # 格式化时间
        for record in recent_logins:
            if record['login_time']:
                record['login_time'] = record['login_time'].strftime('%Y-%m-%d %H:%M:%S')
            if not record['reason']:
                record['reason'] = '未知原因'  # 如果reason为空，显示默认值
                
        # 获取最近告警记录
        recent_alerts = AlertHistoryLog.objects.order_by(
            '-create_time'
        )[:5].values(
            'username',    # 执行用户
            'hostname',    # 执行主机
            'command',     # 执行命令
            'create_time'   # 执行时间
        )
        # 处理可能的空值
        for alert in recent_alerts:
            if not alert['username']:
                alert['username'] = '未知用户'
            if not alert['hostname']:
                alert['hostname'] = '未知主机'
            if not alert['command']:
                alert['command'] = '未知命令'
            # 格式化时间
            if alert['create_time']:
                alert['create_time'] = alert['create_time'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                alert['create_time'] = '未知时间'
        
        # 添加网站连通性统计
        website_status = {
            'connected': DomainMonitor.objects.filter(connectivity=True).count(),
            'disconnected': DomainMonitor.objects.filter(connectivity=False).count()
        }
        
        return Response({
            'statistics': statistics,
            'hostTypes': host_types,
            'loginStats': login_stats,
            'recentLogins': list(recent_logins),  # 添加最近失败登陆记录
            'recentAlerts': list(recent_alerts),  # 添加最近告警记录
            'websiteStatus': website_status  # 添加网站连通性数据
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 

@api_view(['GET'])
def login_statistics(request, days):
    """
    获取指定天数内的用户登录统计
    """
    try:
        days = int(days)
        if days not in [7, 14, 30]:
            return Response(
                {'error': '无效的天数参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 获取所有登录记录
        login_records = LoginLog.objects.filter(
            login_time__date__gte=start_date,
            login_time__date__lte=end_date,
            login_status=True
        ).annotate(
            date=TruncDate('login_time')
        ).values('date', 'username').annotate(
            count=Count('id')
        ).order_by('date', 'username')
        
        # 获取所有有登录记录的用户
        users = list(set(record['username'] for record in login_records))
        
        # 初始化每个用户的登录数据
        login_data = defaultdict(lambda: [0] * days)
        dates = []
        
        # 生成日期列表
        current_date = start_date
        date_index = {}
        while current_date <= end_date:
            dates.append(current_date.strftime('%m-%d'))
            date_index[current_date] = len(dates) - 1
            current_date += timedelta(days=1)
        
        # 填充登录数据
        for record in login_records:
            user = record['username']
            date = record['date']
            count = record['count']
            if date in date_index:
                login_data[user][date_index[date]] = count
        
        return Response({
            'dates': dates,
            'users': users,
            'loginData': dict(login_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 