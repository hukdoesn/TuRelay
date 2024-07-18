<template>
    <div class="content_tools">
        <div class="input_tools">
            <a-input class="input_item" addonBefore="用户名" v-model:value="value" placeholder="请输入用户名" />
            <a-input class="input_item" addonBefore="邮箱" v-model:value.lazy="value1" autofocus placeholder="请输入邮箱" />
        </div>
        <div class="button_tools">
            <a-button>重置</a-button>
            <a-button type="primary">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>用户列表</span>
        <a-button class="button_item" type="primary">新建用户</a-button>
    </div>
    <div class="table_user">
        <a-table :columns="columns" :data-source="data" :pagination="paginationOptions" :scroll="tableScroll" />
    </div>
</template>

<script setup>
const columns = [
    {
        title: '编号',
        dataIndex: 'id',
        // width:  100,
        showSorterTooltip: false,
        sorter: (a, b) => b.id - a.id,
        customRender: ({ text }) => h('div', { style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;' }, text)
    },
    {
        title: 'Name',
        name: 'Name',
        dataIndex: 'name',
        key: 'name',
    },
    {
        title: 'Age',
        dataIndex: 'age',
        key: 'age',
    },
    {
        title: 'Address',
        dataIndex: 'address',
        key: 'address',
    },
    {
        title: 'Tags',
        key: 'tags',
        dataIndex: 'tags',
    },
    {
        title: 'Action',
        key: 'action',
    },
];
</script>

<style>
.content_tools,
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
</style>