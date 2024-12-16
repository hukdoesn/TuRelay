from django.apps import AppConfig

class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        from .scheduler import start_scheduler, add_task
        from apps.views import HostMonitorTask
        
        # 启动调度器
        start_scheduler()
        
        # 添加主机监控任务（每10秒执行一次）
        add_task(
            HostMonitorTask,
            HostMonitorTask.monitor_hosts,
            'host_monitor',
            '主机连接探测',
            60
        )