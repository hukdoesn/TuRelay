<template>
  <div class="node-tree-container">
    <a-tree
      :tree-data="treeData"
      :selectedKeys="selectedKeys"
      :expandedKeys="expandedKeys"
      @select="onSelect"
      @rightClick="onRightClick"
      @expand="onExpand"
      :autoExpandParent="autoExpandParent"
      :showLine="{ showLeafIcon: false }"
    >
      <template #switcherIcon="{ expanded }">
        <CaretDownOutlined v-if="expanded" />
        <CaretRightOutlined v-else />
      </template>
      <template #title="{ title, key }">
        <span v-if="editingKey !== key" class="node-title">
          <IconFont 
            :type="expandedKeys.includes(key) ? 'icon-wenjianjia3' : 'icon-folder111'" 
            class="folder-icon" 
          />
          {{ title }}
          <span class="host-count" v-if="findNode(treeData, key)?.hostCount > 0">
            ({{ findNode(treeData, key)?.hostCount }})
          </span>
        </span>
        <a-input
          v-else
          v-model:value="editingName"
          size="small"
          @pressEnter="handleInputConfirm"
          @blur="handleInputBlur"
          ref="inputRef"
          :autoFocus="true"
        />
      </template>
    </a-tree>

    <!-- 右键菜单 -->
    <a-menu
      v-if="contextMenuVisible"
      :style="contextMenuStyle"
      class="context-menu"
    >
      <a-menu-item key="1" @click="handleAddNode">
        <PlusOutlined /> 新建子节点
      </a-menu-item>
      <a-menu-item key="2" @click="handleEditNode">
        <EditOutlined /> 修改节点
      </a-menu-item>
      <a-menu-item key="3" @click="handleDeleteNode">
        <DeleteOutlined /> 删除节点
      </a-menu-item>
    </a-menu>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { message, Modal } from 'ant-design-vue';
import axios from 'axios';
import IconFont from '@/icons';
import {
  CaretDownOutlined,
  CaretRightOutlined,
  EditOutlined,
  DeleteOutlined,
  PlusOutlined
} from '@ant-design/icons-vue';

const treeData = ref([]);
const selectedKeys = ref([]);
const expandedKeys = ref([]);
const autoExpandParent = ref(true);
const contextMenuVisible = ref(false);
const contextMenuStyle = ref({
  position: 'fixed',
  top: '0px',
  left: '0px',
  display: 'none'
});

const currentNode = ref(null);
const editingKey = ref(null);
const editingName = ref('');
const inputRef = ref(null);

// 添加一个变量来跟踪是否已经处理过输入
const isProcessing = ref(false);

// 添加一个变量来保存新建节点时的父节点信息
const addingParentNode = ref(null);

// 修改处理输入框失焦的函数
const handleInputBlur = () => {
  // 添加延时，避免立即触发
  setTimeout(() => {
    if (!isProcessing.value && editingName.value.trim() !== '') {
      handleInputConfirm();
    }
  }, 100);
};

// 处理展开/折叠
const onExpand = (keys) => {
  expandedKeys.value = keys;
  autoExpandParent.value = false;
};

// 获取节点数据并构建树结构
const fetchNodes = async () => {
  try {
    // 保存当前展开的节点
    const currentExpandedKeys = [...expandedKeys.value];
    
    const response = await axios.get('/api/asset_nodes/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
      }
    });
    const nodes = response.data;
    treeData.value = buildTree(nodes);
    
    // 恢复之前展开的节点状态
    expandedKeys.value = currentExpandedKeys;
    
    // 如果是首次加载，才展开根节点
    if (currentExpandedKeys.length === 0) {
      const rootKeys = treeData.value.map(node => node.key);
      expandedKeys.value = rootKeys;
      autoExpandParent.value = true;
    }
  } catch (error) {
    message.error('获取节点数据失败');
  }
};

// 获取所有节点的key，用于默认展开
const getAllKeys = (nodes) => {
  const keys = [];
  const getKeys = (nodes) => {
    nodes.forEach(node => {
      keys.push(node.key);
      if (node.children && node.children.length > 0) {
        getKeys(node.children);
      }
    });
  };
  getKeys(nodes);
  return keys;
};

// 构建树结构
const buildTree = (nodes) => {
  const nodeMap = new Map();
  const tree = [];

  // 首先创建所有节点的映射
  nodes.forEach(node => {
    nodeMap.set(node.id, {
      key: node.id,
      title: node.name,
      children: [],
      parentId: node.parent,
      hostCount: node.host_count // 添加主机数量
    });
  });

  // 构建树结构
  nodes.forEach(node => {
    const currentNode = nodeMap.get(node.id);
    if (node.parent && nodeMap.get(node.parent)) {
      // 如果有父节点且父节点存在，将当前节点添加到父节点的children中
      const parentNode = nodeMap.get(node.parent);
      parentNode.children.push(currentNode);
    } else {
      // 如果没有父节点，则作为根节点
      tree.push(currentNode);
    }
  });

  return tree;
};

// 修改处理右键点击的函数
const onRightClick = ({ event, node }) => {
  event.preventDefault();
  currentNode.value = node;
  selectedKeys.value = [node.key];
  
  contextMenuStyle.value = {
    position: 'fixed',
    top: `${event.clientY}px`,
    left: `${event.clientX}px`,
    display: 'block'
  };
  contextMenuVisible.value = true;
};

// 处理节点选择
const onSelect = (selectedKeys, { node }) => {
  currentNode.value = node;
};

// 修改处理新建节点的函数
const handleAddNode = async () => {
  // 保存当前选中的节点作为父节点
  addingParentNode.value = currentNode.value;
  
  editingKey.value = 'new';
  editingName.value = '';
  isProcessing.value = true; // 防止blur立即触发
  
  // 展开父节点
  if (addingParentNode.value) {
    const currentExpandedKeys = new Set(expandedKeys.value);
    currentExpandedKeys.add(addingParentNode.value.key);
    expandedKeys.value = Array.from(currentExpandedKeys);
  }
  
  // 创建新节点的临时显示
  const parentKey = addingParentNode.value ? addingParentNode.value.key : null;
  const newNode = {
    key: 'new',
    title: '',
    parentId: parentKey,
    children: []
  };
  
  // 找到父节点并添加新节点
  if (parentKey) {
    const updateTreeData = (data) => {
      return data.map(node => {
        if (node.key === parentKey) {
          return {
            ...node,
            children: [...(node.children || []), newNode]
          };
        }
        if (node.children) {
          return {
            ...node,
            children: updateTreeData(node.children)
          };
        }
        return node;
      });
    };
    
    treeData.value = updateTreeData(treeData.value);
  } else {
    treeData.value = [...treeData.value, newNode];
  }

  await nextTick();
  if (inputRef.value) {
    inputRef.value.focus();
    // 重置处理状态
    setTimeout(() => {
      isProcessing.value = false;
    }, 200);
  }
};

// 处理编辑节点
const handleEditNode = async () => {
  if (!currentNode.value) return;
  editingKey.value = currentNode.value.key;
  editingName.value = currentNode.value.title;
  
  // 使用导入的nextTick
  await nextTick();
  if (inputRef.value) {
    inputRef.value.focus();
  }
};

// 修改处理删除节点的函数
const handleDeleteNode = async () => {
  if (!currentNode.value) return;
  
  // 添加确认对话框
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除该节点吗？如果该节点下有子节点，所有子节点也将被删除。',
    okText: '确认',
    cancelText: '取消',
    async onOk() {
      try {
        const response = await axios.delete(`/api/asset_nodes/${currentNode.value.key}/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`
          }
        });
        
        if (response.status === 204) {
          message.success('节点删除成功');
          await fetchNodes();
        }
      } catch (error) {
        if (error.response) {
          const errorMessage = error.response.data.error;
          if (errorMessage) {
            message.error(errorMessage);
          } else {
            message.error('删除节点失败');
          }
        } else {
          message.error('删除节点失败');
        }
      }
    }
  });
};

// 修改处理输入确认的函数
const handleInputConfirm = async () => {
  if (isProcessing.value) return;
  
  const name = editingName.value.trim();
  if (!name) {
    return; // 如果名称为空，直接返回，不显示错误信息
  }

  try {
    isProcessing.value = true;

    if (editingKey.value === 'new') {
      // 使用保存的父节点信息
      const parentId = addingParentNode.value && addingParentNode.value.key !== 'new' 
        ? addingParentNode.value.key 
        : null;
      
      // 保存当前展开状态
      const currentExpandedKeys = new Set(expandedKeys.value);
      if (parentId) {
        currentExpandedKeys.add(parentId);
      }

      const response = await axios.post('/api/asset_nodes/', {
        name: name,
        parent_id: parentId
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`
        }
      });
      
      if (response.status === 201) {
        message.success('节点创建成功');
        await fetchNodes();
        // 恢复展开状态
        expandedKeys.value = Array.from(currentExpandedKeys);
      }
    } else {
      // 更新节点
      const response = await axios.put(`/api/asset_nodes/${editingKey.value}/`, {
        name: name
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`
        }
      });
      
      if (response.status === 200) {
        message.success('节点更新成功');
        // 保存当前展开状态
        const currentExpandedKeys = new Set(expandedKeys.value);
        await fetchNodes();
        // 恢复展开状态
        expandedKeys.value = Array.from(currentExpandedKeys);
      }
    }

    // 重置编辑状态
    editingKey.value = null;
    editingName.value = '';
    addingParentNode.value = null; // 重置保存的父节点信息
    
  } catch (error) {
    console.error('操作失败:', error);
    message.error(error.response?.data?.error || '操作失败');
  } finally {
    setTimeout(() => {
      isProcessing.value = false;
    }, 100);
  }
};

// 查找节点的辅助函数
const findNode = (nodes, key) => {
  for (const node of nodes) {
    if (node.key === key) return node;
    if (node.children) {
      const found = findNode(node.children, key);
      if (found) return found;
    }
  }
  return null;
};

// 点击其他地方关闭右键菜单
const handleClickOutside = (e) => {
  if (contextMenuVisible.value) {
    contextMenuVisible.value = false;
  }
};

onMounted(() => {
  fetchNodes();
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

// 导出刷新方法供父组件调用
const refresh = async () => {
  await fetchNodes();
};

// 暴露方法给父组件
defineExpose({
  refresh
});
</script>

<style scoped>
.node-tree-container {
  padding: 16px;
  background: #fff;
}

.context-menu {
  position: fixed;
  z-index: 1000;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  overflow: hidden;
}

.context-menu :deep(.ant-menu-item) {
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.context-menu :deep(.ant-menu-item:hover) {
  background-color: #f5f5f5;
}

:deep(.ant-input) {
  width: auto;
  min-width: 100px;
}

.node-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.folder-icon {
  color: #1890ff;
  font-size: 18px;
}

:deep(.ant-tree-switcher) {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.ant-tree-switcher .anticon) {
  font-size: 14px;
}

.host-count {
  /* margin-left: 0px; */
  color: #7f7f7f;
  font-size: 12px;
}
</style>
