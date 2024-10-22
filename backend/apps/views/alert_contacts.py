from apps.utils import APIView, Response, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, AlertContact
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

class AlertContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertContact
        fields = '__all__'

class AlertContactView(APIView):
    """
    AlertContactView 类处理 AlertContact 模型的 CRUD 操作，
    并按名称和通知类型进行过滤。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回告警联系人列表，支持按名称和通知类型进行筛选，并提供分页功能。
        """
        name = request.GET.get('name', '')
        notify_type = request.GET.get('notify_type', '')

        alert_contacts = AlertContact.objects.all().order_by('-create_time')

        if name:
            alert_contacts = alert_contacts.filter(name__icontains=name)
        if notify_type:
            alert_contacts = alert_contacts.filter(notify_type__icontains=notify_type)

        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        paginator = Paginator(alert_contacts, page_size)

        try:
            current_page_data = paginator.page(page)
        except PageNotAnInteger:
            current_page_data = paginator.page(1)
        except EmptyPage:
            current_page_data = paginator.page(paginator.num_pages)

        data = []
        for alert_contact in current_page_data:
            data.append({
                'id': alert_contact.id,
                'name': alert_contact.name,
                'creator': alert_contact.creator,
                'notify_type': alert_contact.notify_type,
                'webhook': alert_contact.webhook,
                'create_time': alert_contact.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

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

    def post(self, request):
        """
        处理POST请求，创建新的告警联系人
        """
        serializer = AlertContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, name):
        """
        处理PUT请求，更新现有告警联系人
        """
        alert_contact = get_object_or_404(AlertContact, name=name)
        before_data = model_to_dict(alert_contact)
        serializer = AlertContactSerializer(alert_contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            after_data = model_to_dict(alert_contact)
            return Response(after_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, name):
        """
        处理DELETE请求，删除现有告警联系人
        """
        alert_contact = get_object_or_404(AlertContact, name=name)
        alert_contact_data = model_to_dict(alert_contact)
        alert_contact.delete()
        return Response(alert_contact_data, status=status.HTTP_204_NO_CONTENT)
