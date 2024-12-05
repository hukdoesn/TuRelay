<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input v-model:value="filters.username" class="input_item" addonBefore="用户名"  placeholder="请输入用户名" />
            <a-input  v-model:value="filters.status" class="input_item" addonBefore="状态" placeholder="请输入状态" />
        </div>
        <div class="button_tools">
            <a-button class="button_font" @click="resetFilters">重置</a-button>
            <a-button class="button_font" type="primary" @click="fetchLockRecord">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>锁定记录</span>
    </div>
    <div class="table_main">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>
</template>

<script setup>
import { ref, reactive, h , onMounted } from 'vue' 
import { message, Badge, Tag } from 'ant-design-vue';
import axios from 'axios';  // 引入axios用于请求后端API

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
    status: '',  // 用于存储输入的状态筛选条件
})

// 表格滚动选项
const tableScroll = { y: 400 }

// 表格列定义
const columns = [
    {
        title: '编号',  
        dataIndex: 'id',
        width: 120,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,  // 前端编号排序
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '用户名',
        dataIndex: 'username',
        width: 170,
    },
    {
        title: '失败登录次数',
        dataIndex: 'login_count',
        width: 120,
        customRender: ({ text }) => h(Tag, { 
            // color: 'rgba(22, 119, 255, 0.8)',
            // color: 'processing',
            style: { },
            // bordered: false,
        }, () => `${text} 次`)  // 将“次”附加到文本值
    },
    {
        title: '锁定',
        dataIndex: 'lock_count',
        width: 120,
        customRender: ({ text }) => h(Tag, { 
            // color: 'rgba(22, 119, 255, 0.8)',
            // color: 'processing',
            style: { },
            // bordered: false,
        }, () => `${text} 次`)  // 将“次”附加到文本值
    },

    {
        title: '状态',
        dataIndex: 'status',
        width: 120,
        customRender: ({ record }) => {
            const status = record.status ? 'error' : 'success';
            const text = record.status ? '锁定' : '启用';
            return h('div', { style: 'display: flex;  align-items: center; gap: 8px;' }, [
                h(Badge, { status }),
                h('span', text)
            ]);
        }
    },
    {
        title: '最后尝试时间',
        dataIndex: 'last_attempt_time',
        width: 170,
        customRender: ({ text }) => text || 'N/A'  // 如果是 null 则显示"N/A"
    }
]

//将状态文本映射到布尔值或整数值的函数
const mapStatus = (statusText) => {
    if (statusText === '启用') {
        return 0;  // 对应于“已启用”
    } else if (statusText === '锁定') {
        return 1;  // 对应于“已锁定”
    } else {
        return ''; // 如果不匹配则默认
    }
}

// 获取锁定记录
const fetchLockRecord = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 将状态文本转换为适合后端的布尔值/整数
        const statusValue = mapStatus(filters.status);

        // 发送请求获取操作日志列表
        const response = await axios.get('/api/lock_record/', {
            headers: {
                'Authorization': `Bearer ${token}`  // 在请求头中包含Token
            },
            params: {
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
                username: filters.username,  // 将用户名筛选条件发送到后端
                status: statusValue,  // 将状态筛选条件转换后发送到后端
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
    // 重新获取锁定记录
    fetchLockRecord()
}

// 重置筛选条件
const resetFilters = () => {
    filters.username = ''  // 清空用户名筛选条件
    filters.status = ''  // 清空状态筛选条件
    fetchLockRecord()  // 重新获取锁定记录
}

// 初次加载时获取锁定记录
onMounted(() => {
    fetchLockRecord()
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