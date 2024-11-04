from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.models import Node
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class AssetNodesView(APIView):
    """
    资产节点管理视图
    提供节点的增删改查功能
    """
    
    def get(self, request):
        """获取所有节点"""
        try:
            nodes = Node.objects.all()
            node_list = []
            
            # 创建一个函数来计算节点及其子节点的主机总数
            def count_total_hosts(node):
                # 获取当前节点的直接主机数量
                direct_hosts = node.hosts.count()
                # 获取所有子节点的主机数量
                child_hosts = sum(count_total_hosts(child) for child in node.children.all())
                # 返回总数
                return direct_hosts + child_hosts
            
            for node in nodes:
                # 计算该节点下的所有主机数量（包括子节点的主机）
                total_hosts = count_total_hosts(node)
                
                node_data = {
                    'id': str(node.id),  # UUID需要转换为字符串
                    'name': node.name,
                    'parent': str(node.parent.id) if node.parent else None,
                    'create_time': node.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'host_count': total_hosts  # 添加主机数量字段
                }
                node_list.append(node_data)
            return Response(node_list)
        except Exception as e:
            logger.error(f"获取节点列表失败: {str(e)}")
            return Response({'error': '获取节点列表失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """创建新节点"""
        try:
            with transaction.atomic():
                name = request.data.get('name')
                parent_id = request.data.get('parent_id')
                
                if not name:
                    return Response({'error': '节点名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 如果提供了父节点ID,验证父节点是否存在
                parent_node = None
                if parent_id:
                    try:
                        parent_node = Node.objects.get(id=parent_id)
                    except ObjectDoesNotExist:
                        return Response({'error': '父节点不存在'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 创建新节点
                node = Node.objects.create(
                    name=name,
                    parent=parent_node
                )
                
                return Response({
                    'id': str(node.id),
                    'name': node.name,
                    'parent': str(node.parent.id) if node.parent else None,
                    'create_time': node.create_time.strftime('%Y-%m-%d %H:%M:%S')
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"创建节点失败: {str(e)}")
            return Response({'error': '创建节点失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk=None):
        """更新节点"""
        try:
            with transaction.atomic():
                if not pk:
                    return Response({'error': '未提供节点ID'}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    node = Node.objects.get(id=pk)
                except ObjectDoesNotExist:
                    return Response({'error': '节点不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                name = request.data.get('name')
                if not name:
                    return Response({'error': '节点名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
                
                node.name = name
                node.save()
                
                return Response({
                    'id': str(node.id),
                    'name': node.name,
                    'parent': str(node.parent.id) if node.parent else None,
                    'create_time': node.create_time.strftime('%Y-%m-%d %H:%M:%S')
                })
                
        except Exception as e:
            logger.error(f"更新节点失败: {str(e)}")
            return Response({'error': '更新节点失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        """删除节点及其所有子节点"""
        try:
            with transaction.atomic():
                if not pk:
                    return Response({'error': '未提供节点ID'}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    node = Node.objects.get(id=pk)
                except ObjectDoesNotExist:
                    return Response({'error': '节点不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                # 检查是否有关联的主机
                if node.hosts.exists():
                    return Response({'error': '该节点或其子节点下存在主机,无法删除'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 获取所有子节点
                def get_child_nodes(parent_node):
                    children = list(parent_node.children.all())
                    for child in children:
                        children.extend(get_child_nodes(child))
                    return children
                
                # 检查所有子节点是否有关联的主机
                child_nodes = get_child_nodes(node)
                for child_node in child_nodes:
                    if child_node.hosts.exists():
                        return Response({'error': f'子节点 {child_node.name} 下存在主机,无法删除'}, 
                                     status=status.HTTP_400_BAD_REQUEST)
                
                # 如果没有关联的主机，执行删除操作
                # Django会自动处理级联删除(因为在模型中使用了CASCADE)
                node.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
                
        except Exception as e:
            logger.error(f"删除节点失败: {str(e)}")
            return Response({'error': '删除节点失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
