from apps.utils import APIView, Response, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, Credential
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from rest_framework import serializers
import json

# 凭据序列化器，用于验证和序列化 Credential 模型的数据
class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'

class CredentialView(APIView):
    """
    CredentialView 类处理 Credential 模型的 CRUD 操作，
    并按帐户名称和类型进行过滤。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回凭据列表，支持按账户名和类型进行筛选，并提供分页功能。
        """
        # 获取筛选参数
        account = request.GET.get('account', '')  # 获取账户名的筛选参数，默认为空字符串
        type = request.GET.get('type', '')   # 获取凭据类型的筛选参数，默认为空字符串

        # 获取所有凭据并按创建时间升序排序
        credentials = Credential.objects.all().order_by('create_time')

        # 根据筛选参数过滤凭据
        if account:
            credentials = credentials.filter(account__icontains=account)
        if type:
            credentials = credentials.filter(type__icontains=type)

        # 获取分页参数
        page = request.GET.get('page', 1)  # 获取当前页码，默认为第1页
        page_size = request.GET.get('page_size', 10)  # 获取每页显示的记录数，默认为10

        # 实例化分页器
        paginator = Paginator(credentials, page_size)

        # 获取当前页的数据
        current_page_data = paginator.get_page(page)

        # 构建响应数据
        data = []
        for credential in current_page_data:

            data.append({
                'id': credential.id,
                'name': credential.name,
                'type': credential.type,
                'account': credential.account,
                # 'password': credential.password,
                # 'key': credential.key,
                # 'key_password': credential.key_password,
                'KeyId': credential.KeyId,
                'notes': credential.notes,
                'create_time': credential.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # 构建分页信息
        pagination = {
            'current_page': current_page_data.number,  # 当前页码
            'total_pages': paginator.num_pages,  # 总页数
            'total_items': paginator.count,  # 总记录数
            'page_size': page_size,  # 每页显示的记录数
        }

        # 返回分页后的响应数据
        return Response({
            'result': data,
            'pagination': pagination
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        处理POST请求，用于创建新的凭据
        """
        serializer = CredentialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        处理PUT请求，更新现有凭据
        """
        # 根据主键获取凭据对象，如果不存在则返回404
        credential = get_object_or_404(Credential, pk=pk)

        # 使用model_to_dict记录更新前的数据
        before_data = model_to_dict(credential)

        # 序列化并验证更新的数据
        serializer = CredentialSerializer(credential, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # 使用model_to_dict记录更新后的数据
            after_data = model_to_dict(credential)

            # 返回更新后的凭据数据
            return Response(after_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        处理DELETE请求，删除现有凭据
        """
        # 根据主键获取凭据对象，如果不存在则返回404
        credential = get_object_or_404(Credential, pk=pk)

        # 使用model_to_dict记录删除前的数据
        credential_data = model_to_dict(credential)

        # 删除凭据
        credential.delete()

        # 返回删除前的凭据数据
        return Response(credential_data, status=status.HTTP_204_NO_CONTENT)
