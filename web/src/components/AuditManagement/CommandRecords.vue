<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input class="input_item" addonBefore="用户名"  placeholder="请输入用户名" />
            <a-input class="input_item" addonBefore="主机名" placeholder="请输入主机名称" />
        </div>
        <div class="button_tools">
            <a-button class="button_font">重置</a-button>
            <a-button class="button_font" type="primary">查询</a-button>
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
import { ref, reactive , onMounted, h} from 'vue' 
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
        title: '命令',
        dataIndex: 'command',
        width: 300,
    },
    {
        title: '主机',
        dataIndex: 'hostname',
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

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    // 更新分页选项
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    // 重新获取命令记录
    fetchCommandRecords()
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