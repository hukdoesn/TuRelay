from django.apps import AppConfig
import os

class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        pass  # 删除所有定时任务相关代码
