<template>
    <a-layout>
      <!-- 顶部布局，用于显示标题 -->
      <a-layout-header class="terminal-header">
        <div class="header-title">Tu Relay</div>
      </a-layout-header>
      <a-layout>
        <!-- 侧边栏布局，包含树形结构 -->
        <a-layout-sider :width="collapsed ? 80 : 250" class="terminal-sidebar" :collapsible="true" :collapsed="collapsed" @collapse="handleCollapse">
          <div class="sidebar-content">
            <a-tree
              v-if="!collapsed"
              :treeData="treeData"
              @select="handleSelect"
              :expandedKeys="expandedKeys"
              @expand="handleExpand"
              class="tree-view"
            >
              <template #title="{ title, dataRef }">
                <span class="tree-title">
                  <icon-font :type="dataRef.isLeaf ? getLeafNodeIcon(dataRef) : (expandedKeys.includes(dataRef.key) ? 'icon-wenjianjia3' : 'icon-folder')" />
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
              <a-tag
                v-for="tab in tabs"
                :key="tab.key"
                :closable="true"
                @close="removeTab(tab)"
                @click="switchTab(tab.key)"
                :color="tab.key === activeTabKey ? 'blue' : ''"
              >
                {{ tab.title }}
              </a-tag>
            </div>
            <!-- 终端容器，显示当前激活的终端 -->
            <div v-if="currentHostId" ref="terminalContainer" class="terminal-container"></div>
            <!-- 重新连接按钮 -->
            <div class="reconnect-button" v-if="currentHostId">
              <a-button type="primary" @click="reconnectTerminal">重新连接</a-button>
            </div>
          </a-layout-content>
        </a-layout>
      </a-layout>
    </a-layout>
  </template>
  
  <script setup>
  import { ref, onMounted, onBeforeUnmount, nextTick, getCurrentInstance } from 'vue';
  import { Terminal } from 'xterm';
  import '@/assets/css/xterm.css';
  import { FitAddon } from 'xterm-addon-fit';
  import { DownOutlined } from '@ant-design/icons-vue';
  import axios from 'axios';
  import IconFont from '@/icons';
  
  // 声明响应式变量
  const treeData = ref([]);
  const expandedKeys = ref([]);
  const tabs = ref([]);
  const currentHostId = ref(null);
  const activeTabKey = ref(null); // 追踪当前活动的标签
  const terminalContainer = ref(null);
  
  let terminals = {}; // 用于存储所有的终端实例
  let fitAddons = {}; // 用于存储所有终端的FitAddon实例
  let socket = null; 
  
  const { appContext } = getCurrentInstance();
  const wsServerAddress = appContext.config.globalProperties.$wsServerAddress;
  
  // 获取树形结构数据
  const fetchTreeData = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.get('/api/terminal/get_tree_structure/', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      treeData.value = response.data.treeData;
    } catch (error) {
      console.error('获取树结构数据失败:', error);
    }
  };
  
  const handleExpand = (keys) => {
    expandedKeys.value = keys;
  };
  
  const getLeafNodeIcon = (dataRef) => {
    return dataRef.icon === 'linux' ? 'icon-linux' : 'icon-windows';
  };
  
  // 处理选择节点事件
  const handleSelect = async (selectedKeys, info) => {
    if (info.node.isLeaf) {
      addTab(info.node.title, info.node.key);
      currentHostId.value = info.node.key;
      await nextTick();
      reconnectTerminal(info.node.key); // 为特定主机ID重连终端
    }
  };
  
  const collapsed = ref(false);
  const handleCollapse = (collapse) => (collapsed.value = collapse);
  
  // 初始化指定的终端
  const initializeTerminal = (hostId) => {
    if (!terminalContainer.value) {
      console.error('终端容器未挂载，无法初始化终端。');
      return;
    }
  
    // 如果该终端已经存在，直接切换到该终端
    if (terminals[hostId]) {
      return;
    }
  
    const fitAddon = new FitAddon();
    const terminal = new Terminal();
    terminal.loadAddon(fitAddon);
    terminal.open(terminalContainer.value);
    fitAddon.fit();
  
    terminals[hostId] = terminal;
    fitAddons[hostId] = fitAddon;
  
    // 监听终端输入
    terminal.onData((data) => {
      if (socket) {
        socket.send(data);
      }
    });
  
    socket = new WebSocket(`${wsServerAddress}/ws/ssh/${hostId.replace(/-/g, '')}/`);
  
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
  
  // 切换到不同的标签时显示对应的终端
  const switchTab = async (key) => {
    activeTabKey.value = key;
    currentHostId.value = key;
    await nextTick();
    reconnectTerminal(key);
  };
  
  // 重新连接指定的终端
  const reconnectTerminal = (hostId) => {
    if (socket) socket.close();
    if (terminals[hostId]) terminals[hostId].dispose();
    terminals[hostId] = null;
    fitAddons[hostId] = null;
    initializeTerminal(hostId);
  };
  
  // 添加Tab标签
  const addTab = (title, key) => {
    if (!tabs.value.find((tab) => tab.key === key)) {
      tabs.value.push({ title, key });
    }
    activeTabKey.value = key; // 设置当前活跃标签
  };
  
  // 移除Tab标签
  const removeTab = (tab) => {
    tabs.value = tabs.value.filter((t) => t.key !== tab.key);
    delete terminals[tab.key]; // 删除对应的终端实例
  };
  
  // 窗口大小变化时调整终端
  const handleResize = () => {
    if (fitAddons[currentHostId.value] && socket && socket.readyState === WebSocket.OPEN) {
      fitAddons[currentHostId.value].fit();
      const { cols, rows } = terminals[currentHostId.value];
      socket.send(JSON.stringify({ cols, rows }));
    }
  };
  
  onMounted(() => {
    fetchTreeData();
    window.addEventListener('resize', handleResize);
  });
  
  onBeforeUnmount(() => {
    if (socket) socket.close();
    window.removeEventListener('resize', handleResize);
  });
  </script>
  