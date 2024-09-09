from django.http import JsonResponse
from apps.models import Node, Host
from django.db.models import Prefetch

def get_tree_structure(request):
    """
    获取主机和节点的树结构，并根据主机的操作系统类型返回相应的图标信息
    :param request: HTTP请求对象
    :return: 包含节点和主机的树形结构的JSON响应
    """
    try:
        # 查询所有节点，预取相关联的主机
        nodes = Node.objects.prefetch_related(
            Prefetch('hosts', queryset=Host.objects.all())
        ).all()

        # 定义递归函数构建节点树
        def build_tree(node):
            # 获取子节点
            children = node.children.all()
            # 获取主机节点
            hosts = node.hosts.all()

            # 构建当前节点
            node_data = {
                'key': str(node.id),  # 作为唯一标识
                'title': node.name,  # 显示节点名称
                'children': [],  # 初始化children为空
                'icon': 'folder',  # 为文件夹节点设置图标
                'isLeaf': False  # 确保所有文件夹节点（非主机节点）是非叶子节点
            }

            # 先添加主机作为叶子节点，并根据操作系统类型选择图标
            for host in hosts:
                host_icon = 'linux' if host.operating_system.lower() == 'linux' else 'windows'
                node_data['children'].append({
                    'key': str(host.id),
                    'title': f"{host.name}",
                    'isLeaf': True,  # 设置为叶子节点
                    'icon': host_icon  # 返回操作系统图标信息
                })

            # 递归处理子节点，子节点在叶子节点后添加
            for child in children:
                node_data['children'].append(build_tree(child))

            return node_data

        # 查找根节点（无父节点的节点）
        root_nodes = nodes.filter(parent__isnull=True)

        # 构建树结构
        tree_data = [build_tree(root) for root in root_nodes]

        return JsonResponse({'treeData': tree_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
