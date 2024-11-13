from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.models import SystemSettings, User
from django.db.models import Q

class SystemSettingsView(APIView):
    def get(self, request):
        settings = SystemSettings.objects.first()
        if not settings:
            settings = SystemSettings.objects.create()
        
        # 检查MFA状态
        total_users = User.objects.count()
        mfa_enabled_users = User.objects.filter(mfa_level=1).count()
        
        # 确定MFA状态
        if mfa_enabled_users == 0:
            mfa_status = 'disabled'
        elif mfa_enabled_users == total_users:
            mfa_status = 'enabled'
        else:
            mfa_status = 'partial'
        
        # 如果是部分用户状态，获取未启用MFA的用户列表
        disabled_mfa_users = []
        if mfa_status == 'partial':
            users = User.objects.filter(mfa_level=0)
            disabled_mfa_users = [{'username': user.username, 'name': user.name} for user in users]
        
        return Response({
            'watermark_enabled': settings.watermark_enabled,
            'ip_whitelist': settings.ip_whitelist,
            'ip_blacklist': settings.ip_blacklist,
            'mfa_enabled': mfa_status,
            'disabled_mfa_users': disabled_mfa_users
        })
    
    def post(self, request):
        settings = SystemSettings.objects.first()
        if not settings:
            settings = SystemSettings.objects.create()
        
        # 处理MFA设置
        new_mfa_status = request.data.get('mfa_enabled')
        if new_mfa_status in ['enabled', 'disabled']:
            # 全局启用或关闭MFA
            mfa_level = 1 if new_mfa_status == 'enabled' else 0
            User.objects.all().update(mfa_level=mfa_level)
        
        settings.watermark_enabled = request.data.get('watermark_enabled', settings.watermark_enabled)
        settings.ip_whitelist = request.data.get('ip_whitelist', settings.ip_whitelist)
        settings.ip_blacklist = request.data.get('ip_blacklist', settings.ip_blacklist)
        settings.save()
        
        return Response({'message': '设置已更新'}, status=status.HTTP_200_OK) 