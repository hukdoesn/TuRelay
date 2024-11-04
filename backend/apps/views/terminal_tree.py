from django.http import JsonResponse
from apps.models import Node, Host
from django.db.models import Prefetch

def get_tree_structure(request):
    """
    获取主机和节点的树结构，包含主机数量统计
    """
    try:
        # 查询所有节点，预取相关联的主机
        nodes = Node.objects.prefetch_related(
            Prefetch('hosts', queryset=Host.objects.all())
        ).all()

        # 定义计算节点及其子节点的主机总数的函数
        def count_total_hosts(node):
            # 获取当前节点的直接主机数量
            direct_hosts = node.hosts.count()
            # 获取所有子节点的主机数量
            child_hosts = sum(count_total_hosts(child) for child in node.children.all())
            # 返回总数
            return direct_hosts + child_hosts

        # 定义递归函数构建节点树
        def build_tree(node):
            # 获取子节点
            children = node.children.all()
            # 获取主机节点
            hosts = node.hosts.all()
            
            # 计算该节点下的所有主机数量
            total_hosts = count_total_hosts(node)

            # 构建当前节点
            node_data = {
                'key': str(node.id),
                'title': f"{node.name}({total_hosts})" if total_hosts > 0 else node.name,
                'children': [],
                'icon': 'folder',
                'isLeaf': False,
                'hostCount': total_hosts  # 添加主机数量字段
            }

            # 先添加主机作为叶子节点
            for host in hosts:
                host_icon = 'linux' if host.operating_system.lower() == 'linux' else 'windows'
                node_data['children'].append({
                    'key': str(host.id),
                    'title': host.name,
                    'isLeaf': True,
                    'icon': host_icon
                })

            # 递归处理子节点
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
