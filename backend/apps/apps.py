from django.apps import AppConfig
import os

class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        if os.environ.get('RUN_MAIN'):  # 确保只在主进程中运行
            try:
                from .scheduler import scheduler, start_scheduler
                from .tasks import cleanup_expired_tokens
                
                # 添加清理token的定时任务
                scheduler.add_job(
                    cleanup_expired_tokens, 
                    'interval', 
                    minutes=1,
                    id='cleanup_expired_tokens',
                    name='清理过期会话',
                    replace_existing=True
                )
                
                # 启动调度器
                start_scheduler()
            except Exception as e:
                print(f"定时任务启动失败: {str(e)}")
