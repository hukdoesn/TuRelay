<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input class="input_item" v-model:value="searchUsername" addonBefore="执行用户" placeholder="请输入执行用户" />
            <a-input class="input_item" v-model:value="searchHostname" addonBefore="执行主机" placeholder="请输入执行主机" />
        </div>
        <div class="button_tools">
            <a-button @click="resetFilters" class="button_font">重置</a-button>
            <a-button @click="fetchAlertLogs" class="button_font" type="primary">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>告警历史</span>
    </div>
    <div class="table_main">
        <a-table 
            style="font-size: 14px;" 
            :columns="columns" 
            :data-source="data" 
            :pagination="paginationOptions"
            :scroll="tableScroll" 
            size="middle" 
            @change="handleTableChange" 
        />
    </div>
</template>

<script setup>
import { ref, reactive, h, onMounted } from 'vue'
import { message, Tag } from 'ant-design-vue';
import axios from 'axios';
import IconFont from '@/icons'

// 搜索条件
const searchUsername = ref('')
const searchHostname = ref('')

// 表格数据
const data = ref([])

// 分页选项
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],
    showSizeChanger: true,
    total: 0,
})

// 表格滚动选项
const tableScroll = { y: 600 }

// 表格列定义
const columns = [
    {
        title: '编号',
        dataIndex: 'id',
        width: 80,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '执行用户',
        dataIndex: 'username',
        width: 120,
    },
    {
        title: '执行主机',
        dataIndex: 'hostname',
        width: 150,
    },
    {
        title: '匹配类型',
        dataIndex: 'match_type',
        width: 100,
        customRender: ({ text }) => h(Tag, {
            color: text === '精准匹配' ? 'rgba(22, 119, 255, 0.8)' : 'rgba(56,158,13,0.8)'
        }, text)
    },
    {
        title: '执行命令',
        dataIndex: 'command',
        width: 250,
        ellipsis: true,
    },
    {
        title: '触发规则',
        dataIndex: 'alert_rule',
        width: 150,
    },
    {
        title: '创建时间',
        dataIndex: 'create_time',
        width: 180,
    }
]

// 获取告警历史记录
const fetchAlertLogs = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        const response = await axios.get('/api/alert_history_logs/', {
            headers: {
                'Authorization': token
            },
            params: {
                username: searchUsername.value,
                hostname: searchHostname.value,
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
            }
        })
        
        data.value = response.data.results
        paginationOptions.total = response.data.pagination.total_items
    } catch (error) {
        message.error('获取告警历史记录失败')
        console.error('Error fetching alert logs:', error)
    }
}

// 处理表格分页变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    fetchAlertLogs()
}

// 重置搜索条件
const resetFilters = () => {
    searchUsername.value = ''
    searchHostname.value = ''
    paginationOptions.current = 1
    fetchAlertLogs()
}

// 初始化加载
onMounted(() => {
    fetchAlertLogs()
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