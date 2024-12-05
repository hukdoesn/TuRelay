<template>
    <div class="content_table">
        <div class="input_tools">
            <!-- 用户名输入框 -->
            <a-input v-model:value="filters.username" class="input_item" addonBefore="操作用户" placeholder="请输入操作用户名" />
            <!-- 请求方法输入框 -->
            <a-input v-model:value="filters.request_method" class="input_item" addonBefore="请求方法" placeholder="请输入请求方法" />
        </div>
        <div class="button_tools">
            <!-- 重置按钮 -->
            <a-button class="button_font" @click="resetFilters">重置</a-button>
            <!-- 查询按钮 -->
            <a-button class="button_font" type="primary" @click="fetchOperationLogs">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>操作日志</span>
    </div>
    <div class="table_main">
        <!-- 操作日志表格 -->
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { message, Tag, Modal, Table } from 'ant-design-vue';
import axios from 'axios';  // 引入axios用于请求后端API
import IconFont from '@/icons'

//  表格数据
const data = ref([])

//  分页选项
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],  // 可选的分页大小
    showSizeChanger: true,  // 显示分页大小选择器
    total: 0,
})

//  筛选选项
const filters = reactive({
    username: '',  // 用于存储输入的用户名筛选条件
    request_method: '',  // 用于存储输入的请求方法筛选条件
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
        title: '操作用户',
        dataIndex: 'username',
        width: 130,
    },
    {
        title: '操作模块',
        dataIndex: 'module',
        width: 130,
        customRender: ({ text }) => h(Tag, { 
            color: 'rgba(22, 119, 255, 0.8)',
            style: {  },
            bordered: false
        }, () => h('span', text))
    },
    {
        title: '请求接口',
        dataIndex: 'request_interface',
        width: 200,
    },
    {
        title: '请求方法',
        dataIndex: 'request_method',
        width: 120,
    },
    {
        title: 'IP地址',
        dataIndex: 'ip_address',
        width: 170,
        // 设置icon图标
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
        title: '请求时间',
        dataIndex: 'create_time',
        width: 170,
    },
    {
        title: '操作',
        dataIndex: 'crud',    
        width: 170,
        customRender: ({ record }) => h('div', { style: 'display: flex; align-items: center; justify-content: left; gap: 12px;' }, [
            h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => showDetails(record) }, '查看详情'),
        ]),
    },
]

// 获取操作日志列表
const fetchOperationLogs = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 发送请求获取操作日志列表
        const response = await axios.get('/api/operation_logs/', {
            headers: {
                'Authorization': `Bearer ${token}`  // 在请求头中包含Token
            },
            params: {
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
                username: filters.username,  // 将用户名筛选条件发送到后端
                request_method: filters.request_method,  // 将请求方法筛选条件发送到后端
            }
        })
        
        // 遍历结果数据，重新生成前端编号
        data.value = response.data.result.map((operationLog, index) => ({
            ...operationLog,
            id: index + 1,  // 当前页的数据从1开始编号
        }))
        paginationOptions.total = response.data.pagination.total_items
    } catch (error) {
        // 获取操作日志列表失败的提示
        message.error('获取操作日志列表失败')
        console.error('Error fetching operation logs:', error)
    }
}

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    // 更新分页选项
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    // 重新获取操作日志列表
    fetchOperationLogs()
}

// 重置筛选条件
const resetFilters = () => {
    filters.username = ''  // 清空用户名筛选条件
    filters.request_method = ''  // 清空请求方法筛选条件
    fetchOperationLogs()  // 重新获取操作日志列表
}

// 显示详情模态框
const showDetails = (record) => {
    Modal.info({
        title: '操作详情',
        width: 800,  // 设置模态框宽度
        content: h(Table, {
            columns: [
                { title: '变更前', dataIndex: 'before' },
                { title: '变更后', dataIndex: 'after' }
            ],
            dataSource: [
                {
                    key: '1',
                    before: h('pre', {}, JSON.stringify(JSON.parse(record.before_change || '{}'), null, 2)),
                    after: h('pre', {}, JSON.stringify(JSON.parse(record.after_change || '{}'), null, 2))
                }
            ],
            pagination: false,  // 不显示分页
            bordered: true
        }),
        onOk() {}
    });
}

// 初次加载时获取操作日志列表
onMounted(() => {
    fetchOperationLogs()
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