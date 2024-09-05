<template>
    <a-layout>
        <a-layout-header class="terminal-header">
            <div class="header-title">Web Terminal</div>
        </a-layout-header>
        <a-layout>
            <a-layout-sider
                :width="collapsed ? 80 : 250"
                class="terminal-sidebar"
                :collapsible="true"
                :collapsed="collapsed"
                @collapse="handleCollapse"
            >
            <!-- collapsible开启折叠收缩 -->
                <div class="sidebar-content">
                    <a-tree
                        :treeData="treeData"
                        defaultExpandAll
                        :showLine="true"
                        @select="handleSelect"
                        class="tree-view"
                    >
                        <template #switcherIcon="{ switcherCls }"><down-outlined :class="switcherCls" /></template>
                    </a-tree>
                </div>
            </a-layout-sider>
            <a-layout>
                <a-layout-content class="terminal-content">
                    <div ref="terminalContainer" class="terminal-container"></div>
                    <div class="reconnect-button">
                        <a-button type="primary" @click="reconnectTerminal">重新连接</a-button>
                    </div>
                </a-layout-content>
            </a-layout>
        </a-layout>
    </a-layout>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue';
import { Terminal } from 'xterm';
import '@/assets/css/xterm.css';
import { FitAddon } from 'xterm-addon-fit';
import { DownOutlined } from '@ant-design/icons-vue';
import axios from 'axios';  // 引入axios用于请求后端API

const treeData = ref([]);  // 初始化为空的树结构数据，从API接口获取数据填充

// 获取树状结构数据
const fetchTreeData = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 发送请求获取树状结构数据
        const response = await axios.get('/api/terminal/get_tree/', {
            headers: {
                'Authorization': `Bearer ${token}`  // 在请求头中包含Token
            },
        });
        // 直接使用后端返回的数据
        treeData.value = response.data.treeData;  // 将 API 返回的数据赋值给 treeData
    } catch (error) {
        console.error('获取树结构数据失败:', error);
    }
}

// 处理导航栏选择事件
const handleSelect = (selectedKeys, info) => {
    console.log('Selected:', selectedKeys, info);
    // 根据选择的节点进行不同的操作
};

// 折叠状态管理
const collapsed = ref(false);

// 切换折叠状态
const toggleCollapse = () => {
    collapsed.value = !collapsed.value;
};

// 处理折叠事件
const handleCollapse = (collapse) => {
    collapsed.value = collapse;
};

// 获取当前页面的 URL 并提取 hostId 参数
const pathSegments = window.location.pathname.split('/'); // 将路径按 '/' 分割
const hostId = pathSegments[pathSegments.length - 1]; // 提取最后一个片段作为 hostId

const terminalContainer = ref(null); // 终端容器引用
let terminal = null; // 初始化为 null，以便在每次重新连接时重新创建终端实例
let fitAddon = null; // 初始化为 null，以确保在需要时正确实例化
let socket = null; // WebSocket实例

// 获取全局属性
const { appContext } = getCurrentInstance();
const wsServerAddress = appContext.config.globalProperties.$wsServerAddress; // 获取全局定义的 WebSocket 服务器地址

// 初始化终端和WebSocket连接
const initializeTerminal = () => {
    // 检查终端容器是否挂载
    if (terminalContainer.value) {
        fitAddon = new FitAddon(); // 创建新的 FitAddon 实例
        terminal = new Terminal();
        terminal.loadAddon(fitAddon); // 加载自适应插件
        terminal.open(terminalContainer.value); // 将终端附加到容器
        fitAddon.fit(); // 调整终端大小以适应容器
    } else {
        console.error('终端容器未挂载，无法进行尺寸调整。');
    }

    // 建立WebSocket连接，使用动态获取的hostId
    socket = new WebSocket(`${wsServerAddress}/ws/ssh/${hostId}/`);

    // WebSocket打开时发送终端尺寸
    socket.onopen = () => {
        if (terminal && fitAddon) {
            fitAddon.fit(); // 适应容器大小
            const { cols, rows } = terminal;
            socket.send(JSON.stringify({ cols, rows })); // 发送初始的终端尺寸
        }
    };

    // 处理从服务器接收到的信息
    socket.onmessage = (event) => {
        if (terminal) {
            terminal.write(event.data); // 将服务器的数据写入终端
        }
    };

    // 处理终端输入并发送到服务器
    terminal.onData((data) => {
        if (socket) {
            socket.send(data); // 将输入数据发送到服务器
        }
    });

    // 处理连接错误
    socket.onerror = (event) => {
        if (terminal) {
            terminal.write('\r\n*** 连接错误，请稍后再试 ***\r\n');
        }
        console.error('WebSocket 错误:', event);
    };

    // 处理连接关闭
    socket.onclose = (event) => {
        if (!event.wasClean) {
            // 仅在非正常关闭时显示消息
            terminal.write('\r\n*** 连接已关闭 ***\r\n');
        }
    };
};

// 处理窗口大小调整并相应地调整终端大小
const handleResize = () => {
    // 检查终端和 fitAddon 是否已经初始化
    if (terminal && fitAddon && socket && socket.readyState === WebSocket.OPEN) {
        fitAddon.fit(); // 重新计算并适应终端大小
        const { cols, rows } = terminal;
        socket.send(JSON.stringify({ cols, rows })); // 发送调整后的终端尺寸到后端
    } else {
        console.warn('在调整大小时终端或 fitAddon 尚未初始化。');
    }
};

// 重新连接功能
const reconnectTerminal = () => {
    if (socket) {
        socket.close(); // 关闭当前 WebSocket 连接
    }
    if (terminal) {
        terminal.dispose(); // 销毁旧的终端实例，确保所有资源被释放
        terminal = null; // 将终端设置为 null，以便重新创建
    }
    if (fitAddon) {
        fitAddon = null; // 清除旧的 FitAddon 实例
    }
    initializeTerminal(); // 重新初始化终端和 WebSocket 连接
};

// 生命周期钩子
onMounted(() => {
    initializeTerminal(); // 挂载时初始化终端
    fetchTreeData();  // 挂载时获取树结构数据
    window.addEventListener('resize', handleResize); // 监听窗口大小改变
});

onBeforeUnmount(() => {
    if (socket) {
        socket.close(); // 卸载时关闭WebSocket连接
    }
    window.removeEventListener('resize', handleResize); // 清理事件监听器
});
</script>

<style scoped>
.terminal-header {
    text-align: center;
    color: #fff;
    height: 30px;
    line-height: 30px;
    background-color: #7dbcea;
}

.terminal-container {
    height: calc(100vh - 30px);
    /* 终端的全高，减去 header 的高度 */
    width: 100%;
    /* 终端的全宽 */
    background-color: black;
    /* 终端背景颜色 */
}

.terminal-sidebar {
    height: calc(100vh - 30px);
    /* 侧边栏的全高，减去 header 的高度 */
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
    /* padding: 24px; */
    min-height: 280px;
    background: #fff;
}

.reconnect-button {
    position: absolute;
    top: 10px;
    right: 10px;
}

.header-title {
    font-size: 24px;
    font-weight: bold;
}
</style>
