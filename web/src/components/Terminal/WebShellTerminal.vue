<template>
    <a-layout>
        <!-- 顶部布局，用于显示标题 -->
        <a-layout-header class="terminal-header">
            <img  src="@/assets/svg/terminal_logo.svg" alt="Logo" class="logo-img" />
        </a-layout-header>
        <a-layout>
            <!-- 侧边栏布局，包含树形结构 -->
            <a-layout-sider 
                :width="250" 
                :collapsedWidth="30" 
                class="terminal-sidebar" 
                :collapsible="true"
                :collapsed="collapsed" 
                @collapse="handleCollapse">
                <!-- 树形结构显示的内容，支持折叠 -->
                <div class="sidebar-content">
                    <a-tree v-if="!collapsed" :treeData="treeData" @select="handleSelect" :expandedKeys="expandedKeys"
                        @expand="handleExpand" class="tree-view">
                        <!-- 使用图标来区分叶子节点和非叶子节点 -->
                        <template #title="{ title, dataRef }">
                            <span class="tree-title">
                                <!-- 如果是叶子节点，使用根据操作系统选择的图标，否则根据展开状态选择图标 -->
                                <icon-font
                                    :type="dataRef.isLeaf ? getLeafNodeIcon(dataRef) : (expandedKeys.includes(dataRef.key) ? 'icon-folder-open' : 'icon-folder')" />
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
                    <!-- Tab elements -->
                    <div class="tab-bar">
                        <a-tag
                            v-for="tab in tabs"
                            :key="tab.key"
                            :closable="true"
                            @close="removeTab(tab)"
                            @click="switchTab(tab.key)"
                            :class="{'active-tab': tab.key === activeTabKey, 'inactive-tab': tab.key !== activeTabKey}" 
                        >
                            {{ tab.title }}
                        </a-tag>
                        <!-- 重新连接按钮 -->
                        <div class="reconnect-button" v-if="currentHostId">
                            <a-button type="text" @click="reconnectTerminal">
                                <!-- 添加图标 -->
                                <icon-font type="icon-shuaxin2" class="reconnect-icon"/>
                                <!-- 显示文本 -->
                                重新连接
                            </a-button>
                        </div>
                    </div>
                    <!-- 创建每个终端容器 -->
                    <div v-for="tab in tabs" :key="tab.key" v-show="tab.key === activeTabKey" class="terminal-container"
                        :ref="setTerminalRef(tab.key)"></div>
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
const terminalRefs = ref({}); // 用于存储每个标签页的终端容器引用
let terminals = {}; // 用于存储每个标签的终端实例
let fitAddons = {}; // 用于存储终端的FitAddon实例
let sockets = {}; // 用于存储每个终端的 WebSocket 实例
const originalHostIds = {}; // 用于存储原始 hostId 以便创建 WebSocket 时使用

// 获取全局属性
const { appContext } = getCurrentInstance();
const wsServerAddress = appContext.config.globalProperties.$wsServerAddress; // 获取全局定义的 WebSocket 服务器地址

// 获取树状结构数据，从后端API请求并填充treeData
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

// 设置终端引用
const setTerminalRef = (key) => (el) => {
    if (el) {
        terminalRefs.value[key] = el;
    }
};

// 处理节点扩展以跟踪扩展的keys
const handleExpand = (keys) => {
    expandedKeys.value = keys;
};

// 获取叶子节点（主机）的图标
const getLeafNodeIcon = (dataRef) => {
    return dataRef.icon === 'linux' ? 'icon-linux' : 'icon-windows';
};

// 处理树状节点选择事件，确保只有点击叶子节点时才初始化终端连接
const handleSelect = async (selectedKeys, info) => {
    if (info.node.isLeaf) {
        addTabWithUniqueName(info.node.title, info.node.key); // 调用带唯一名称的函数创建Tab
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
            background: '#242739', // 设置背景颜色
            foreground: '#ffffff'  // 设置字体颜色
        }
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

    // 创建WebSocket时仅使用原始 hostId
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

// 添加带唯一名称的Tab标签
const addTabWithUniqueName = (title, hostId) => {
    let baseTitle = title;
    let index = 0;

    // 确保标签名称唯一
    while (tabs.value.find((tab) => tab.title === title)) {
        index += 1;
        title = `${baseTitle}(${index})`;
    }

    // 生成唯一的tab key，结合节点的key和递增的数字
    const uniqueTabKey = `${hostId}-${index}`;

    // 存储原始 hostId
    originalHostIds[uniqueTabKey] = hostId;

    tabs.value.push({ title, key: uniqueTabKey });

    // 设置新创建的tab为当前活动标签
    activeTabKey.value = uniqueTabKey;
    currentHostId.value = uniqueTabKey;

    // 等待 DOM 更新后初始化终端
    nextTick(() => {
        initializeTerminal(uniqueTabKey);
    });
};

// 移除Tab标签
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
};

// 窗口大小变化时调整终端
const handleResize = () => {
    if (fitAddons[currentHostId.value] && sockets[currentHostId.value] && sockets[currentHostId.value].readyState === WebSocket.OPEN) {
        fitAddons[currentHostId.value].fit();
        const { cols, rows } = terminals[currentHostId.value];
        sockets[currentHostId.value].send(JSON.stringify({ cols, rows }));
    }
};

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
    background-color: #16171F;
    display: flex;
    align-items: center;
    justify-content: flex-start;
}

.terminal-container {
    height: calc(100vh - 60px);
    width: 100%;
    background-color: #242739;
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
    background: #242739;
}

.tab-bar {
    height: 30px;
    display: flex;
    align-items: center;
    padding-left: 5px;
    color: #fff;
    background-color: #2D2F3D;
}

.logo-img {
  height: 31px;
}

.reconnect-button {
    position: absolute;
    /* top: 10px; */
    right: 10px;
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
    background: #16171F;
}

:deep(:where(.css-dev-only-do-not-override-19iuou).ant-layout .ant-layout-sider) {
    background: #16171F;
}

:deep(:where(.css-dev-only-do-not-override-19iuou).ant-layout .ant-layout-sider-trigger) {
    background: #16171F;
}


/* 选定节点的样式 */
:deep(.ant-tree .ant-tree-node-selected) {
    background-color: #242739 !important; 
    color: #ffffff !important;
}

/* 活跃tab样式*/
.active-tab {
    background-color: #242739 !important; 
    color: #FFFFFF !important;
    position: relative; /* 底部边界定位 */
}

/* 活跃tab添加底部边框*/
.active-tab::after {
    content: ''; /* 下划线的空内容 */
    position: absolute;
    bottom: 0; /* 将边框放置在tab的底部 */
    left: 25%; /* 将50%宽度的下划线居中 */
    width: 50%; /* 将下划线宽度设置为50% */
    height: 2px; /* 下划线的厚度 */
    background-color: #428DFF; 
}


/* 非活跃tab样式 */
.inactive-tab {
    background-color: #2D2F3D !important; 
    color: #FFFFFF66 !important; 
    border-color: #2d2e36 !important; 
    position: relative;
}

/* 背景和文本的tab悬停样式 */
:deep(.ant-tag:hover) {
    background-color: #242739 !important; 
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

/* 默认重新连接按钮图标颜色 */
.reconnect-button icon-font {
    color: #FFFFFF66; /* 非悬浮时，图标的颜色 */
}

/* 悬浮重新连接按钮时，改变图标颜色 */
.reconnect-button:hover icon-font {
    color: #FFFFFF; /* 悬浮时，图标的颜色 */
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
    background-color: #242739;
}

/* 默认重新连接按钮图标颜色 */
.reconnect-button icon-font svg {
    color: #FFFFFF66; /* 非悬浮时，图标的颜色 */
}

/* 悬浮重新连接按钮时，改变图标颜色 */
.reconnect-button:hover icon-font svg {
    color: #FFFFFF; /* 悬浮时，图标的颜色 */
}

/* logo左边距 */
:where(.css-dev-only-do-not-override-19iuou).ant-layout .ant-layout-header {
    padding-inline: 8px !important;
}

/* 终端内容左边距 */
:deep(.xterm-dom-renderer-owner-1 .xterm-rows ){
      padding-left: 10px !important; 
  }
</style>