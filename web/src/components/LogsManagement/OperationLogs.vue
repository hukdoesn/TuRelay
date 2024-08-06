<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input class="input_item" addonBefore="用户名"  placeholder="请输入用户名" />
            <a-input class="input_item" addonBefore="登录IP" autofocus placeholder="请输入登录IP" />
        </div>
        <div class="button_tools">
            <a-button class="button_font">重置</a-button>
            <a-button class="button_font" type="primary">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>登录日志</span>
    </div>
    <div class="table_login">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue' 
import { message } from 'ant-design-vue';
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

// 表格滚动选项
const tableScroll = { y: 400 }

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
        width: 170,
    },
    {
        title: '操作模块',
        dataIndex: 'module',
        width: 170,
    },
    {
        title: '请求接口',
        dataIndex: 'request_interface',
        width: 120,
    },
    {
        title: '请求方法',
        dataIndex: 'request_method',
        width: 120,
    },
    {
        title: ' IP地址',
        dataIndex: 'ip_adderss',
        width: 170,
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
    },
]

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    // 更新分页选项
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    // 重新获取用户列表
    fetchUsers()
}
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