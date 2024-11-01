<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input class="input_item" addonBefore="用户名" v-model:value="searchUsername" placeholder="请输入用户名" />
            <a-input class="input_item" addonBefore="登录IP" v-model:value.lazy="searchClientIp" placeholder="请输入登录IP" />
        </div>
        <div class="button_tools">
            <a-button @click="resetFilters" class="button_font">重置</a-button>
            <a-button @click="fetchLoginLogs" class="button_font" type="primary">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>登录日志</span>
    </div>
    <div class="table_main">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>
</template>

<script setup>
import { ref, reactive, h, onMounted } from 'vue'
import { message, Tag } from 'ant-design-vue';
import axios from 'axios';  // 引入axios用于请求后端API
import IconFont from '@/icons'

// 搜索输入框的绑定变量
const searchUsername = ref('')
const searchClientIp = ref('')

// 表格数据
const data = ref([])

// 分页选项
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],  // 可选的分页大小
    showSizeChanger: true,  // 显示分页大小选择器
    total: 0,
})

// 表格滚动选项
const tableScroll = { y: 600 }

// 表格列定义
const columns = [
    {
        title: '编号',
        dataIndex: 'id',
        width: 100,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,  // 前端编号排序
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '用户名',
        dataIndex: 'username',
        width: 120,
    },
    {
        title: '客户端IP',
        dataIndex: 'client_ip',
        width: 150,
        customRender: ({ text }) => h('span', [
            h('a', {
                href: `https://ip.cn/`, // 跳转到IP查询网站
                target: '_blank', // 在新选项卡中打开链接
                style: { marginRight: '8px' }
            }, [
                h(IconFont, { type: 'icon-IPdizhi' }) 
            ]),
            text
        ])
    },
    {
        title: '登录状态',
        dataIndex: 'login_status',
        width: 120,
        customRender: ({ text }) => h(Tag, {
            color: text === 1 ? 'processing' : 'error',
            bordered: false
        }, () => text === 1 ? '成功' : '失败')
    },
    {
        title: '原因',
        dataIndex: 'reason',
        width: 120,
        customRender: ({ text }) => {
            // 如果原因字段为空，则填充为'-'符号并添加左边距显示
            return text ? text : h('div', { style: 'margin-left: 8px;' }, '-');
        }
    },
    {
        title: '浏览器信息',
        dataIndex: 'browser_info',
        width: 190,
        customRender: ({ text }) => {
            let iconType = '';
            let browserName = text.split(' ')[0]; // 从文本中提取浏览器名
            switch (browserName) {
                case 'Chrome':
                    iconType = 'icon-Chrome';
                    break;
                case 'Edge':
                    iconType = 'icon-MicrosoftEdge';
                    break;
                case 'Safari':
                    iconType = 'icon-Safari';
                    break;
                case 'Firefox':
                    iconType = 'icon-firefox';
                    break;
                default:
                    iconType = 'icon-a-404'; // 默认图标
                    break;
            }
            return h('div', { style: 'display: flex; align-items: center;' }, [
                h(IconFont, { type: iconType, style: 'margin-right: 8px; font-size: 18px;' }),
                h('span', text)
            ]);
        }
    },
    {
        title: '操作系统',
        dataIndex: 'os_info',
        width: 170,
        customRender: ({ text }) => {
            let iconType = '';
            let osName = text.split(' ')[0]; // 从文本中提取操作系统名
            switch (osName) {
                case 'Windows':
                    iconType = 'icon-windows';
                    break;
                case 'Mac':
                    iconType = 'icon-apple1';
                    break;
                case 'Linux':
                    iconType = 'icon-Linux';
                    break;
                case 'Android':
                    iconType = 'icon-android';
                    break;
                case 'iOS':
                    iconType = 'icon-cellular-phone-replenishing';
                    break;
                default:
                    iconType = 'icon-jujue'; // 默认图标
                    break;
            }
            return h('div', { style: 'display: flex; align-items: center;' }, [
                h(IconFont, { type: iconType, style: 'margin-right: 8px; font-size: 18px;' }),
                h('span', text)
            ]);
        }
    },
    {
        title: '登录时间',
        dataIndex: 'login_time',
        width: 170,
    },
]

// 获取登录日志列表
const fetchLoginLogs = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 发送请求获取登录日志列表
        const response = await axios.get('/api/login_logs/', {
            headers: {
                'Authorization': `Bearer ${token}`  // 在请求头中包含Token
            },
            params: {
                username: searchUsername.value,
                client_ip: searchClientIp.value,
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
            }
        })
        // 遍历结果数据，重新生成前端编号
        data.value = response.data.results.map((loginLog, index) => ({
            ...loginLog,
            id: index + 1,  // 当前页的数据从1开始编号
        }))
        paginationOptions.total = response.data.pagination.total_items
    } catch (error) {
        // 获取用户列表失败的提示
        message.error('获取登录日志列表失败')
        console.error('Error fetching login logs:', error)
    }
}

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    // 更新分页选项
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    // 重新获取登录日志列表
    fetchLoginLogs()
}

// 重置搜索过滤器
const resetFilters = () => {
    searchUsername.value = ''
    searchClientIp.value = ''
    paginationOptions.current = 1
    fetchLoginLogs()
}

// 初次加载时获取登录日志列表
onMounted(() => {
    fetchLoginLogs()
})
</script>

<style>
.content_table,
.button_create {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 25px 0 25px 0;
    background-color: #fff;
}

.input_tools {
    display: flex;
    gap: 16px;
}

.input_item {
    flex: 1;
    max-width: 300px;
    /* 设置最大宽度 */
    min-width: 200px;
    /* 设置最小宽度 */
}

.button_tools {
    display: flex;
    gap: 16px;
}

.button_font {
    font-size: 12px;
}
/* 修改 input的addonBefore 和 placeholder 的字体大小 */
.ant-input-group-addon,
.ant-input::placeholder,
.ant-table-thead {
    font-size: 12px !important;
}
</style>