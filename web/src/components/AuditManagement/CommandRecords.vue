<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input v-model:value="filters.username" class="input_item" addonBefore="用户名" placeholder="请输入用户名" />
            <a-input v-model:value="filters.hostname" class="input_item" addonBefore="主机名" placeholder="请输入主机名称" />
        </div>
        <div class="button_tools">
            <a-button class="button_font" @click="resetFilters">重置</a-button>
            <a-button class="button_font" type="primary" @click="fetchCommandRecords">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>命令记录</span>
    </div>
    <div class="table_main">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { message, Tag } from 'ant-design-vue';
import axios from 'axios';

const data = ref([])

const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],
    showSizeChanger: true,
    total: 0,
})

const filters = reactive({
    username: '',
    hostname: '',
})

const tableScroll = { y: 700 }

const columns = [
    {
        title: '编号',  
        dataIndex: 'id',
        width: 120,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '执行用户',
        dataIndex: 'username',
        width: 170,
    },
    {
        title: '执行命令',
        dataIndex: 'command',
        width: 300,
    },
    {
        title: '主机名称',
        dataIndex: 'hosts',
        width: 170,
        customRender: ({ text }) => h(Tag, { 
            color: 'processing',
            style: {  },
            bordered: false
        }, () => h('span', text))
    },
    {
        title: 'IP地址',
        dataIndex: 'network',
        width: 170,
    },
    {
        title: '凭据',
        dataIndex: 'credential',
        width: 170,
    },
    {
        title: '执行时间',
        dataIndex: 'create_time',
        width: 170,
    }
]

const fetchCommandRecords = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        const response = await axios.get('/api/command_logs/', {
            headers: {
                'Authorization': `Bearer ${token}`
            },
            params: {
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
                username: filters.username,
                hostname: filters.hostname,
            }
        })
        
        // 直接使用当前数据的索引+1作为编号，这样每页都会从1开始
        data.value = response.data.data.items.map((commandLog, index) => ({
            ...commandLog,
            id: index + 1  // 每页都从1开始编号
        }))
        
        paginationOptions.total = response.data.data.total
    } catch (error) {
        message.error('获取命令记录列表失败')
        console.error('Error fetching command records:', error)
    }
}

const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    fetchCommandRecords()
}

const resetFilters = () => {
    filters.username = ''
    filters.hostname = ''
    paginationOptions.current = 1
    fetchCommandRecords()
}

onMounted(() => {
    fetchCommandRecords()
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
