<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input class="input_item" addonBefore="主机名称"  placeholder="请输入主机名" />
            <a-input class="input_item" addonBefore="规则名称" placeholder="请输入规则名称" />
        </div>
        <div class="button_tools">
            <a-button class="button_font">重置</a-button>
            <a-button class="button_font" type="primary">查询</a-button>
        </div>
    </div>
    <!-- 新建命令报警按钮 -->
    <div class="button_create">
        <span>命令报警</span>
        <a-button @click="showCreateModal" class="button_item button_font" type="primary">新建规则</a-button>
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
        width: 50,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,  // 前端编号排序
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '名称',
        dataIndex: 'name',
        width: 100,
    },
    {
        title: '命令规则',
        dataIndex: 'command_rule',
        width: 130,
    },
    {
        title: '关联主机',
        dataIndex: 'links_host',
        width: 100,
    },
    {
        title: '告警联系人',
        dataIndex: 'alert_contact',
        width: 120,
    },
    {
        title: '是否告警',
        dataIndex: 'is_alert',
        width: 100,
        customRender: ({ text }) => h('div', {
            style: 'display: flex; align-items: center; justify-content: center;'
        }, text ? '是' : '否')
    },
    {
        title: '创建时间',
        dataIndex: 'create_time',
        width: 120,
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