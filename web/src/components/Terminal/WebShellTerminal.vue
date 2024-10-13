<template>
  <a-layout>
    <!-- 顶部布局，用于显示标题 -->
    <a-layout-header class="terminal-header">
      <img src="@/assets/svg/turelay_logo.svg" alt="Logo" class="logo-img" />
    </a-layout-header>
    <a-layout>
      <!-- 侧边栏布局，包含树形结构 -->
      <a-layout-sider :width="250" :collapsedWidth="30" class="terminal-sidebar" :collapsible="true"
        :collapsed="collapsed" @collapse="handleCollapse">
        <!-- 树形结构显示的内容，支持折叠 -->
        <div class="sidebar-content">
          <a-tree v-if="!collapsed" :treeData="treeData" @select="handleSelect" :expandedKeys="expandedKeys"
            :selectedKeys="selectedKeys" @expand="handleExpand" class="tree-view">
            <!-- 使用图标来区分叶子节点和非叶子节点 -->
            <template #title="{ title, dataRef }">
              <span class="tree-title">
                <!-- 如果是叶子节点，使用根据操作系统选择的图标，否则根据展开状态选择图标 -->
                <icon-font
                  :type="dataRef.isLeaf ? getLeafNodeIcon(dataRef) : expandedKeys.includes(dataRef.key) ? 'icon-folder-open' : 'icon-folder'" />
                <span class="title-text">{{ title }}</span>
              </span>
            </template>
            <template #switcherIcon="{ switcherCls }">
              <down-outlined :class="switcherCls" />
            </template>
          </a-tree>
        </div>
      </a-layout-sider>
      <a-layout>
        <a-layout-content class="terminal-content">
          <!-- 标签页部分 -->
          <div class="tab-bar">
            <a-tag v-for="tab in tabs" :key="tab.key" :closable="true" @close="removeTab(tab)"
              @click="switchTab(tab.key)"
              :class="{ 'active-tab': tab.key === activeTabKey, 'inactive-tab': tab.key !== activeTabKey }">
              {{ tab.title }}
            </a-tag>
            <!-- 按钮容器，仅在 SSH 连接时显示 -->
            <div class="button-container" v-if="currentHostId && currentConnectionType === 'ssh'">
              <!-- 文件管理按钮 -->
              <a-button type="text" class="file-manager-button" @click="showFileManagerDrawer">
                <icon-font type="icon-wenjianguanli" class="file-manager-icon" />
                文件管理
              </a-button>
              <!-- 重新连接按钮 -->
              <a-button type="text" class="reconnect-button" @click="reconnectTerminal">
                <icon-font type="icon-shuaxin2" class="reconnect-icon" />
                重新连接
              </a-button>
            </div>
          </div>
          <!-- 终端容器 -->
          <div v-for="tab in tabs" :key="tab.key" v-show="tab.key === activeTabKey" class="terminal-container">
            <!-- SSH 终端 -->
            <div v-if="tab.connectionType === 'ssh'" :ref="setTerminalRef(tab.key)" class="full-terminal"></div>
            <!-- RDP 终端 -->
            <div v-else-if="tab.connectionType === 'rdp'" class="full-terminal">
              <WebrdsTerminal :hostId="originalHostIds[tab.key]" />
            </div>
          </div>
        </a-layout-content>
      </a-layout>
    </a-layout>
    <!-- 文件管理抽屉 -->
    <a-drawer v-model:open="isFileManagerVisible" title="文件管理" :width="900" :destroyOnClose="true"
      @close="handleDrawerClose">
      <!-- 文件列表和上传下载功能 -->
      <div class="file-manager-content">
        <!-- 当前路径显示和操作按钮 -->
        <div class="path-and-actions">
          <!-- 返回按钮 -->
          <a-button @click="goBack" class="action-button">
            <icon-font type="icon-go-back" />
          </a-button>
          <!-- 当前路径输入框，允许用户输入路径 -->
          <a-input v-model:value="currentPath" class="current-path-input" @keyup.enter="handlePathInput" />
          <!-- 操作按钮 -->
          <!-- 上传文件 -->
          <a-upload :customRequest="handleUpload" :showUploadList="false" multiple>
            <a-button class="action-button spacing">上传</a-button>
          </a-upload>
          <!-- 下载按钮 -->
          <a-button @click="downloadSelectedFiles" :disabled="selectedFileKeys.length === 0"
            class="action-button spacing">
            下载
          </a-button>
          <!-- 删除按钮 -->
          <a-button @click="deleteSelectedFiles" :disabled="selectedFileKeys.length === 0"
            class="action-button spacing">
            <DeleteOutlined />
            删除
          </a-button>
        </div>
        <!-- 文件列表 -->
        <a-table :columns="fileColumns" :dataSource="fileList" :rowKey="record => record.filename" :pagination="false"
          :scroll="{ y: 700 }" :rowSelection="rowSelection">
        </a-table>
      </div>
    </a-drawer>
  </a-layout>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, getCurrentInstance, h } from 'vue';
import { Terminal } from 'xterm';
import '@/assets/css/xterm.css';
import { FitAddon } from 'xterm-addon-fit';
import { DownOutlined, CaretLeftOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import axios from 'axios';
import IconFont from '@/icons';
import { useRoute } from 'vue-router';
import WebrdsTerminal from './WebrdpTerminal.vue'; // 引入新的 WebrdsTerminal 组件

// 声明响应式变量
const treeData = ref([]);
const expandedKeys = ref([]);
const selectedKeys = ref([]); // 选中的树节点
const tabs = ref([]);
const currentHostId = ref(null);
const activeTabKey = ref(null); // 当前活动的标签
const terminalRefs = ref({}); // 存储每个标签页的终端容器引用
const currentConnectionType = ref(null); // 当前连接类型：'ssh' 或 'rdp'
const connectionTypes = {}; // 存储每个标签的连接类型
let terminals = {}; // 存储每个标签的终端实例
let fitAddons = {}; // 存储终端的 FitAddon 实例
let sockets = {}; // 存储每个终端的 WebSocket 实例
const originalHostIds = {}; // 存储原始 hostId 以便创建 WebSocket 时使用

// 获取全局属性
const { appContext } = getCurrentInstance();
const wsServerAddress = appContext.config.globalProperties.$wsServerAddress; // 获取全局定义的 WebSocket 服务器地址

// 获取路由信息
const route = useRoute();

// 当前路径，默认为根目录 '/'
const currentPath = ref('/');

// 获取树状结构数据，从后端 API 请求并填充 treeData
const fetchTreeData = async () => {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get('/api/terminal/get_tree_structure/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    treeData.value = response.data.treeData;

    // 获取 hostId 并展开选中节点
    const hostId = route.query.hostId;
    if (hostId) {
      expandAndSelectNode(hostId); // 展开树并选中节点
    }
  } catch (error) {
    console.error('获取树结构数据失败:', error);
  }
};

// 设置终端引用
const setTerminalRef = (key) => (el) => {
  if (el) {
    terminalRefs.value[key] = el;
  }
};

// 处理节点扩展以跟踪扩展的 keys
const handleExpand = (keys) => {
  expandedKeys.value = keys;
};

// 查找特定节点在树中的路径
const findNodePath = (nodes, key, path = []) => {
  for (const node of nodes) {
    const currentPath = [...path, node.key];
    if (node.key === key) {
      return { node, path: currentPath };
    }
    if (node.children) {
      const result = findNodePath(node.children, key, currentPath);
      if (result) {
        return result;
      }
    }
  }
  return null;
};

// 展开并选中基于 hostId 的节点
const expandAndSelectNode = (hostId) => {
  const result = findNodePath(treeData.value, hostId);
  if (result) {
    const { node, path } = result;
    expandedKeys.value = path.slice(0, -1); // 展开父节点
    selectedKeys.value = [node.key]; // 选中节点
    const connectionType = node.icon === 'linux' ? 'ssh' : 'rdp';
    addTabWithUniqueName(node.title, node.key, connectionType);
  } else {
    console.error(`Node with key ${hostId} not found in treeData`);
  }
};

// 获取叶子节点（主机）的图标
const getLeafNodeIcon = (dataRef) => {
  return dataRef.icon === 'linux' ? 'icon-linux' : 'icon-windows';
};

// 处理树状节点选择事件，确保只有点击叶子节点时才初始化连接
const handleSelect = async (selectedKeysParam, info) => {
  if (info.node.isLeaf) {
    selectedKeys.value = selectedKeysParam;
    const connectionType = info.node.icon === 'linux' ? 'ssh' : 'rdp';
    addTabWithUniqueName(info.node.title, info.node.key, connectionType); // 调用带唯一名称的函数创建 Tab
  }
};

// 处理侧边栏的折叠与展开事件
const collapsed = ref(false);
const handleCollapse = (collapse) => (collapsed.value = collapse);

// 初始化指定的终端
const initializeTerminal = async (uniqueTabKey) => {
  const hostId = originalHostIds[uniqueTabKey]; // 获取原始 hostId

  if (terminals[uniqueTabKey]) return;

  await nextTick(); // 确保 DOM 更新完成
  const terminalContainer = terminalRefs.value[uniqueTabKey];

  if (!terminalContainer) {
    console.error('终端容器未挂载，无法初始化终端。');
    return;
  }

  const fitAddon = new FitAddon();
  const terminal = new Terminal({
    theme: {
      background: '#1e202366', // 设置背景颜色
      foreground: '#ffffff', // 设置字体颜色
    },
    cursorBlink: true, // 光标闪烁
    cursorStyle: 'bar', // 光标样式
    cursorWidth: 1, // 光标宽度
  });
  terminal.loadAddon(fitAddon);
  terminal.open(terminalContainer);
  fitAddon.fit();

  terminals[uniqueTabKey] = terminal;
  fitAddons[uniqueTabKey] = fitAddon;

  terminal.onData((data) => {
    if (sockets[uniqueTabKey]) {
      sockets[uniqueTabKey].send(data);
    }
  });

  // 创建 WebSocket 时仅使用原始 hostId
  const socket = new WebSocket(`${wsServerAddress}/ws/ssh/${hostId.replace(/-/g, '')}/`);
  sockets[uniqueTabKey] = socket;

  socket.onopen = () => {
    const { cols, rows } = terminal;
    socket.send(JSON.stringify({ cols, rows }));
  };

  socket.onmessage = (event) => {
    terminal.write(event.data);
  };

  socket.onclose = (event) => {
    if (!event.wasClean) {
      terminal.write('\r\n*** 连接已关闭 ***\r\n');
    }
  };

  socket.onerror = (event) => {
    terminal.write('\r\n*** 连接错误，请稍后再试 ***\r\n');
  };
};

// 切换到不同的标签时仅切换显示
const switchTab = async (uniqueTabKey) => {
  activeTabKey.value = uniqueTabKey;
  currentHostId.value = uniqueTabKey;
  currentConnectionType.value = connectionTypes[uniqueTabKey];
};

// 重新连接指定的终端
const reconnectTerminal = () => {
  const uniqueTabKey = activeTabKey.value;
  if (sockets[uniqueTabKey]) sockets[uniqueTabKey].close();
  if (terminals[uniqueTabKey]) terminals[uniqueTabKey].dispose();
  terminals[uniqueTabKey] = null;
  fitAddons[uniqueTabKey] = null;
  sockets[uniqueTabKey] = null;
  initializeTerminal(uniqueTabKey);
};

// 添加带唯一名称的 Tab 标签
const addTabWithUniqueName = (title, hostId, connectionType) => {
  let baseTitle = title;
  let index = 0;

  // 确保标签名称唯一
  while (tabs.value.find((tab) => tab.title === title)) {
    index += 1;
    title = `${baseTitle}(${index})`;
  }

  // 生成唯一的 tab key，结合节点的 key 和递增的数字
  const uniqueTabKey = `${hostId}-${index}`;

  // 存储原始 hostId 和连接类型
  originalHostIds[uniqueTabKey] = hostId;
  connectionTypes[uniqueTabKey] = connectionType;

  tabs.value.push({ title, key: uniqueTabKey, connectionType });

  // 设置新创建的 tab 为当前活动标签
  activeTabKey.value = uniqueTabKey;
  currentHostId.value = uniqueTabKey;
  currentConnectionType.value = connectionType;

  // 等待 DOM 更新后初始化终端或 RDP 连接
  nextTick(() => {
    if (connectionType === 'ssh') {
      initializeTerminal(uniqueTabKey);
    }
    // 对于 RDP，不需要初始化，WebrdsTerminal.vue 会处理
  });
};

// 移除 Tab 标签
const removeTab = (tab) => {
  tabs.value = tabs.value.filter((t) => t.key !== tab.key);

  // 清理终端和 WebSocket
  if (terminals[tab.key]) {
    terminals[tab.key].dispose();
    delete terminals[tab.key];
  }
  if (sockets[tab.key]) {
    sockets[tab.key].close();
    delete sockets[tab.key];
  }
  delete originalHostIds[tab.key]; // 删除存储的原始 hostId
  delete connectionTypes[tab.key]; // 删除存储的连接类型

  // 如果删除的 tab 是当前活动的 tab，需要更新 activeTabKey 和 currentHostId
  if (activeTabKey.value === tab.key) {
    if (tabs.value.length > 0) {
      const newActiveTab = tabs.value[tabs.value.length - 1];
      activeTabKey.value = newActiveTab.key;
      currentHostId.value = newActiveTab.key;
      currentConnectionType.value = connectionTypes[newActiveTab.key];
    } else {
      activeTabKey.value = null;
      currentHostId.value = null;
      currentConnectionType.value = null;
    }
  }
};

// 窗口大小变化时调整终端
const handleResize = () => {
  if (
    fitAddons[currentHostId.value] &&
    sockets[currentHostId.value] &&
    sockets[currentHostId.value].readyState === WebSocket.OPEN
  ) {
    fitAddons[currentHostId.value].fit();
    const { cols, rows } = terminals[currentHostId.value];
    sockets[currentHostId.value].send(JSON.stringify({ cols, rows }));
  }
};

// 文件管理相关
const isFileManagerVisible = ref(false); // 控制文件管理抽屉的显示
const fileList = ref([]); // 存储文件列表

// 定义文件列表的列
const fileColumns = [
  {
    title: '文件名',
    dataIndex: 'filename',
    key: 'filename',
    width: 200,
    customRender: ({ text, record }) => {
      return renderFilenameCell(text, record);
    },
  },
  {
    title: '属主属组',
    dataIndex: 'owner:group',
    key: 'owner:group',
    width: 120,
    customRender: ({ text, record }) => {
      return `${record.owner}:${record.group}`;
    },
  },
  {
    title: '大小',
    dataIndex: 'size',
    width: 100,
    key: 'size',
    customRender: ({ text, record }) => {
      return record.size;
    },
  },
  {
    title: '权限',
    dataIndex: 'permissions',
    key: 'permissions',
    width: 120,
    customRender: ({ text, record }) => {
      return record.permissions;
    },
  },
  {
    title: '修改日期',
    dataIndex: 'modify_time',
    key: 'modify_time',
    width: 200,
    customRender: ({ text, record }) => {
      return record.modify_time;
    },
  },
];

// 渲染文件名单元格的函数
const renderFilenameCell = (text, record) => {
  return h(
    'span',
    {
      onClick: () => handleFileClick(record),
      style: 'cursor: pointer; display: flex; align-items: center;',
    },
    [
      h(IconFont, {
        type: record.is_directory ? 'icon-a-Vector3' : 'icon-file',
        style: 'margin-right: 5px;',
      }),
      h(
        'span',
        {
          style: 'flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;',
        },
        record.filename
      ),
    ]
  );
};

// 多选框配置
const selectedFileKeys = ref([]); // 存储选中的文件名
const rowSelection = {
  selectedRowKeys: selectedFileKeys,
  onChange: (selectedRowKeys) => {
    selectedFileKeys.value = selectedRowKeys;
  },
};

// 显示文件管理抽屉并加载文件列表
const showFileManagerDrawer = async () => {
  isFileManagerVisible.value = true;
  currentPath.value = '/'; // 默认路径为根目录
  await loadFileList();
};

// 定义 handleDrawerClose 方法，在关闭抽屉时重置状态
const handleDrawerClose = () => {
  fileList.value = [];
  currentPath.value = '/';
  selectedFileKeys.value = [];
  // 如果有其他需要重置的状态，也可以在这里添加
};

// 加载文件列表
const loadFileList = async (path = currentPath.value) => {
  try {
    const uniqueTabKey = activeTabKey.value;
    const hostId = originalHostIds[uniqueTabKey];
    const response = await axios.get(`/api/terminal/files/${hostId}/`, {
      params: { path },
    });
    fileList.value = response.data.files;
    currentPath.value = response.data.current_path; // 更新当前路径
  } catch (error) {
    console.error('加载文件列表失败:', error);
  }
};

// 点击文件或目录
const handleFileClick = async (record) => {
  if (record.is_directory) {
    // 如果是目录，进入该目录
    const newPath = currentPath.value.endsWith('/')
      ? currentPath.value + record.filename
      : currentPath.value + '/' + record.filename;
    currentPath.value = newPath;
    await loadFileList(newPath);
  } else {
    // 如果是文件，可以添加预览等功能
  }
};

// 上传文件
const handleUpload = async ({ file, onSuccess, onError }) => {
  try {
    const uniqueTabKey = activeTabKey.value;
    const hostId = originalHostIds[uniqueTabKey];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', currentPath.value); // 上传到当前路径
    await axios.post(`/api/terminal/upload/${hostId}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    // 上传成功后刷新文件列表
    await loadFileList();
    onSuccess(null, file);
  } catch (error) {
    console.error('上传文件失败:', error);
    onError(error);
  }
};

// 下载选中的文件
const downloadSelectedFiles = async () => {
  try {
    const uniqueTabKey = activeTabKey.value;
    const hostId = originalHostIds[uniqueTabKey];
    for (const filename of selectedFileKeys.value) {
      const response = await axios.get(`/api/terminal/download/${hostId}/`, {
        params: {
          filename,
          path: currentPath.value,
        },
        responseType: 'blob',
      });
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  } catch (error) {
    console.error('下载文件失败:', error);
  }
};

// 删除选中的文件
const deleteSelectedFiles = async () => {
  try {
    const uniqueTabKey = activeTabKey.value;
    const hostId = originalHostIds[uniqueTabKey];
    for (const filename of selectedFileKeys.value) {
      await axios.delete(`/api/terminal/delete/${hostId}/`, {
        params: {
          filename,
          path: currentPath.value,
        },
      });
    }
    // 删除成功后刷新文件列表
    await loadFileList();
    // 清空选中的文件
    selectedFileKeys.value = [];
  } catch (error) {
    console.error('删除文件失败:', error);
  }
};

// 返回上一级目录
const goBack = async () => {
  if (currentPath.value !== '/') {
    // 移除当前路径的最后一个目录
    let newPath = currentPath.value.replace(/\/$/, ''); // 移除末尾的斜杠
    newPath = newPath.substring(0, newPath.lastIndexOf('/')); // 去掉最后一个目录
    if (newPath === '') {
      newPath = '/';
    }
    currentPath.value = newPath;
    await loadFileList();
  }
};

// 处理用户输入的路径
const handlePathInput = async () => {
  await loadFileList();
};

// 组件挂载后执行
onMounted(() => {
  fetchTreeData();
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  // 关闭所有 WebSocket 连接并释放资源
  Object.keys(sockets).forEach((key) => {
    if (sockets[key]) {
      sockets[key].close();
    }
  });
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* 样式保持不变 */
.terminal-header {
  text-align: center;
  color: #ffffff;
  height: 30px;
  line-height: 30px;
  background-color: #191C20;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.full-terminal {
  width: 100%;
  height: 100%;
}

.terminal-container {
  height: calc(100vh - 60px);
  width: 100%;
  background-color: #1e2023;
}

.terminal-sidebar {
  height: calc(100vh - 30px);
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.tree-view {
  flex: 1 0 90%;
  overflow-y: auto;
}

.terminal-content {
  min-height: 280px;
  background: #1e2023;
  border-left: 1px solid #30303066;
}

.tab-bar {
  height: 30px;
  display: flex;
  align-items: center;
  padding-left: 5px;
  color: #fff;
  border-top: 1px solid #303030;
  border-bottom: 1px solid #303030;
  background-color: #1d1f23;
}

.logo-img {
  height: 25px;
}

.tree-title {
  display: flex;
  align-items: center;
}

.title-text {
  padding-left: 2px;
}

:deep(:where(.css-dev-only-do-not-override-19iuou).ant-tree .ant-tree-indent-unit) {
  width: 20px !important;
}

/* tab标签页间距 */
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-tag) {
  margin-inline-end: 5px;
  border-radius: 2px;
  border: none;
  line-height: 30px;
}

/* tree 样式 */
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-tree) {
  color: rgba(255, 255, 255);
  background: #191C20;
}

:deep(:where(.css-dev-only-do-not-override-19iuou).ant-layout .ant-layout-sider) {
  background: #191C20;
}

:deep(:where(.css-dev-only-do-not-override-19iuou).ant-layout .ant-layout-sider-trigger) {
  background: #191C20;
}


/* 选定节点的样式 */
:deep(.ant-tree .ant-tree-node-selected) {
  background-color: #1e2023 !important;
  color: #ffffff !important;
}

/* 活跃tab样式*/
.active-tab {
  background-color: #1e2023 !important;
  color: #FFFFFF !important;
  position: relative;
  /* 底部边界定位 */
}

/* 活跃tab添加底部边框*/
.active-tab::after {
  content: '';
  /* 下划线的空内容 */
  position: absolute;
  bottom: 0;
  /* 将边框放置在tab的底部 */
  left: 25%;
  /* 将50%宽度的下划线居中 */
  width: 50%;
  /* 将下划线宽度设置为50% */
  height: 2px;
  /* 下划线的厚度 */
  background-color: #428DFF;
}


/* 非活跃tab样式 */
.inactive-tab {
  /* background-color: #1B1F23 !important; */
  color: #FFFFFF66 !important;
  border-color: #2d2e36 !important;
  position: relative;
}

/* 背景和文本的tab悬停样式 */
:deep(.ant-tag:hover) {
  background-color: #1e2023 !important;
  color: #FFFFFF !important;
  cursor: pointer;
}

/* 鼠标悬停tab，tab icon图标颜色更改为白色 */
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-tag.inactive-tab:hover .ant-tag-close-icon) {
  color: #FFFFFF !important;
}

/* 活跃tab icon图标（白色）*/
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-tag.active-tab .ant-tag-close-icon) {
  color: #ffffff !important;
}

/* 不活跃tab icon图标（白色降低透明度） */
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-tag.inactive-tab .ant-tag-close-icon) {
  color: #FFFFFF66 !important;
}

/* 按钮容器，使用 flex 布局 */
.button-container {
  display: flex;
  align-items: center;
  /* gap: 10px; 在两个按钮之间设置 10px 的间距 */
  position: absolute;
  right: 10px;
  /* 将按钮容器靠右对齐 */
}

/* 重新连接button */
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-btn) {
  color: #FFFFFF66;
}

/* 悬浮重新连接文字颜色 */
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-btn:hover) {
  color: #FFFFFF;
}

/* 悬浮重新连接背景颜色 */
:deep(:where(.css-dev-only-do-not-override-19iuou).ant-btn:hover) {
  background-color: #1e2023;
}

/* logo左边距 */
:where(.css-dev-only-do-not-override-19iuou).ant-layout .ant-layout-header {
  padding-inline: 8px !important;
}

/* 终端内容左边距 */
:deep(.xterm-rows) {
  padding-left: 10px !important;
}
</style>

<style>
/* 文件管理drawer抽屉*/
.ant-drawer .ant-drawer-content {
  width: 100%;
  height: 100%;
  overflow: auto;
  /* background: #21222b; */
  background: #1f1f1f;
  pointer-events: auto;
}

/* 文件管理drawer关闭按钮 */
.ant-drawer .ant-drawer-close {
  color: #ffffffD9;
}

.ant-drawer .ant-drawer-close:hover {
  color: #ffffff;
}

/* 文件管理drawer标题 */
.ant-drawer .ant-drawer-title {
  color: #ffffffD9;
}

/* 文件管理 */
.path-and-actions {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

/* 操作按钮的样式（返回、上传、下载、删除） */
.action-button {
  background-color: #141414 !important;
  color: #FFFFFF66 !important;
  border: none !important;
  display: flex;
  align-items: center;
  border: 1px solid transparent !important;
  /* 添加透明边框*/
  box-sizing: border-box;
  /* Include border in the element's total width */
}

.action-button:hover {
  background-color: #141414 !important;
  color: #FFFFFF !important;
  border: solid 1px #353535 !important;
}

.current-path-input {
  /* flex-grow: 1; */
  background: #141414 !important;
  border-color: #303030 !important;
  color: #ffffff !important;
}

/* Set the background color of the entire table to #141414 and the text color to #ffffffD9 */
.ant-table {
  background-color: #141414 !important;
  /* Table background color */
  color: #ffffffD9 !important;
  /* Table text color */
}

/* Change the background color and text color of the table header */
.ant-table-thead>tr>th {
  background-color: #141414 !important;
  /* Header background color */
  color: #ffffffD9 !important;
  /* Header text color */
  border-top: none !important;
  /* Remove all borders */
  border-bottom: none !important;
  border-bottom: 1px solid #303030 !important;
  /* Dividing line below header */
}

/* If needed, target the cell content inside the header */
.ant-table-thead>tr>th .ant-table-cell {
  background-color: #141414 !important;
  color: #ffffffD9 !important;
}

.ant-table-thead tr th::before {
  background: #303030 !important;
}


/* Set the background color of table rows to #141414 and text color to #ffffffD9 */
.ant-table-tbody>tr>td {
  background-color: #141414 !important;
  /* Row background color */
  color: #ffffffD9 !important;
  /* Row text color */
}

/* Change the background color of a row when the mouse hovers over it to #424242 */
.ant-table-tbody>tr:hover>td {
  background-color: #1f1f1f !important;
  /* Row hover background color */
}

/* Set the dividing line (border) between table rows to #424242 */
.ant-table-tbody>tr>td {
  border: none !important;
  /* Remove all borders */
  border-bottom: 1px solid #303030 !important;
  /* Row dividing line color */
}

/* Customize the appearance of the checkbox */

/* Unchecked checkbox state */
.ant-checkbox-inner {
  background-color: #141414 !important;
  /* Checkbox background when unchecked */
  border-color: #424242 !important;
  /* Checkbox border when unchecked */
}

/* Checked checkbox state */
.ant-checkbox-checked .ant-checkbox-inner {
  background-color: #424242 !important;
  /* Checkbox background when checked */
  border-color: #424242 !important;
  /* Checkbox border when checked */
}

/* Change the color of the checkmark inside the checkbox */
.ant-checkbox-checked .ant-checkbox-inner::after {
  border-color: #ffffffD9 !important;
  /* Checkmark color */
}

/* Checkbox hover state */
.ant-checkbox:hover .ant-checkbox-inner {
  border-color: #1f1f1f !important;
  /* Checkbox border color on hover */
}

/* Checkbox focus state */
.ant-checkbox-input:focus+.ant-checkbox-inner {
  border-color: #1f1f1f !important;
  /* Checkbox border color when focused */
}
</style>
