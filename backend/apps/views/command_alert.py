from apps.utils import APIView, Response, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, CommandAlert, Host, AlertContact
from rest_framework import serializers
from django.shortcuts import get_object_or_404
import json

class CommandAlertSerializer(serializers.ModelSerializer):
    hosts = serializers.ListField(child=serializers.CharField(), required=False)
    alert_contacts = serializers.CharField(required=False)  # 改为 CharField
    command_rule = serializers.ListField(child=serializers.CharField(), required=False)
    host_names = serializers.SerializerMethodField()
    alert_contact_names = serializers.SerializerMethodField()
    match_type = serializers.ChoiceField(choices=[('exact', '精准匹配'), ('fuzzy', '模糊匹配')], default='exact')

    class Meta:
        model = CommandAlert
        fields = ['id', 'name', 'command_rule', 'hosts', 'alert_contacts', 'is_active', 'create_time', 'host_names', 'alert_contact_names', 'match_type']

    def get_host_names(self, obj):
        host_ids = obj.hosts.split(',') if obj.hosts else []
        hosts = Host.objects.filter(id__in=host_ids)
        return [host.name for host in hosts]

    def get_alert_contact_names(self, obj):
        contact_ids = obj.alert_contacts.split(',') if obj.alert_contacts else []
        contacts = AlertContact.objects.filter(id__in=contact_ids)
        return [contact.name for contact in contacts]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['hosts'] = instance.hosts.split(',') if instance.hosts else []
        representation['alert_contacts'] = instance.alert_contacts  # 直接返回字符串
        representation['command_rule'] = json.loads(instance.command_rule) if instance.command_rule else []
        return representation

    def create(self, validated_data):
        hosts = validated_data.pop('hosts', [])
        validated_data['hosts'] = ','.join(str(host) for host in hosts)
        
        # alert_contacts 已经是字符串，不需要处理
        
        command_rules = validated_data.get('command_rule', [])
        validated_data['command_rule'] = json.dumps(command_rules)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'hosts' in validated_data:
            hosts = validated_data.pop('hosts')
            validated_data['hosts'] = ','.join(str(host) for host in hosts)
        
        # alert_contacts 已经是字符串，不需要处理
        
        if 'command_rule' in validated_data:
            command_rules = validated_data['command_rule']
            validated_data['command_rule'] = json.dumps(command_rules)
        
        return super().update(instance, validated_data)

class CommandAlertView(APIView):
    """
    CommandAlertView 类处理 CommandAlert 模型的 CRUD 操作，
    并按主机名和规则名称进行过滤。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            command_alert = get_object_or_404(CommandAlert, id=id)
            serializer = CommandAlertSerializer(command_alert)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            """
            处理GET请求，返回命令告警规则列表，支持按主机名和规则名称进行筛选，并提供分页功能。
            """
            host = request.GET.get('host', '')
            name = request.GET.get('name', '')

            command_alerts = CommandAlert.objects.all().order_by('-create_time')

            if host:
                host_ids = Host.objects.filter(name__icontains=host).values_list('id', flat=True)
                command_alerts = command_alerts.filter(hosts__in=host_ids)
            if name:
                command_alerts = command_alerts.filter(name__icontains=name)

            page = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 10)

            paginator = Paginator(command_alerts, page_size)

            try:
                current_page_data = paginator.page(page)
            except PageNotAnInteger:
                current_page_data = paginator.page(1)
            except EmptyPage:
                current_page_data = paginator.page(paginator.num_pages)

            serializer = CommandAlertSerializer(current_page_data, many=True)

            pagination = {
                'current_page': current_page_data.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': int(page_size),
            }

            return Response({
                'results': serializer.data,
                'pagination': pagination
            }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        处理POST请求，创建新的命令告警规则
        """
        serializer = CommandAlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """
        处理PUT请求，更新现有命令告警规则
        """
        command_alert = get_object_or_404(CommandAlert, id=id)
        serializer = CommandAlertSerializer(command_alert, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """
        处理DELETE请求，删除现有命令告警规则
        """
        command_alert = get_object_or_404(CommandAlert, id=id)
        command_alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class HostListView(APIView):
    """
    HostListView 类用于获取主机列表
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回主机列表
        """
        hosts = Host.objects.all()
        data = [{'id': host.id, 'name': host.name} for host in hosts]
        return Response(data, status=status.HTTP_200_OK)

class AlertContactList(APIView):
    """
    AlertContactListView 类用于获取告警联系人列表
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回告警联系人列表
        """
        alert_contacts = AlertContact.objects.all()
        data = [{'id': contact.id, 'name': contact.name} for contact in alert_contacts]
        return Response({"results": data}, status=status.HTTP_200_OK)  # 将数据包装在 results 字段中
