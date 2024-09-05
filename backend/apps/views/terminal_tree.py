from django.http import JsonResponse
from apps.models import Node, Host

def build_tree_structure():
    """
    构建节点与主机的树结构数据
    """
    node_dict = {}

    # 查询所有节点
    nodes = Node.objects.all()

    # 构建节点的层次结构
    for node in nodes:
        node_path = node.name.split("/")  # 按照 / 分割节点路径
        current_level = node_dict

        for part in node_path:
            if part and part not in current_level:  # Ensure part is not empty
                current_level[part] = {"children": {}}
            current_level = current_level[part]["children"]

    # 查询主机并将其添加到相应的节点
    hosts = Host.objects.all()

    for host in hosts:
        node_id = host.node.id
        node = Node.objects.get(id=node_id)
        node_path = node.name.split("/")
        current_level = node_dict

        # Navigate to the correct node level for the host
        for part in node_path:
            if part:
                current_level = current_level[part]["children"]

        # 在对应的节点下添加主机
        current_level[host.name] = {"title": host.name, "key": host.name, "type": "host"}

    # 将字典转换为树形结构数组格式
    def dict_to_tree(data):
        tree = []
        for key, value in data.items():
            node = {"title": key, "key": key}  # Set title and key for each node
            if "children" in value and value["children"]:
                node["children"] = dict_to_tree(value["children"])
            tree.append(node)
        return tree

    return dict_to_tree(node_dict)

def get_tree_data(request):
    """
    API 端点，返回树结构数据
    """
    try:
        tree_data = build_tree_structure()
        return JsonResponse({"treeData": tree_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
