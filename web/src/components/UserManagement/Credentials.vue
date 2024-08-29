<template>
    <div class="content_table">
        <!-- 筛选条件输入框 -->
        <div class="input_tools">
            <a-input v-model:value="searchAccount" class="input_item" addonBefore="账户" placeholder="请输入账户名" />
            <a-input v-model:value="searchType" class="input_item" addonBefore="类型" placeholder="请输入类型名称" />
        </div>
        <!-- 重置和查询按钮 -->
        <div class="button_tools">
            <a-button @click="resetFilters" class="button_font">重置</a-button>
            <a-button @click="fetchCredentials" class="button_font" type="primary">查询</a-button>
        </div>
    </div>
    <!-- 新建凭据按钮 -->
    <div class="button_create">
        <span>凭据管理</span>
        <a-button @click="openCreateModal" class="button_item button_font" type="primary">新建凭据</a-button>
    </div>
    <!-- 显示凭据的表格 -->
    <div class="table_main">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>

    <!-- Include modal components -->
    <CreateCredentialModal ref="createCredentialModalRef" @refresh="fetchCredentials" />
    <EditCredentialModal ref="editCredentialModalRef" @refresh="fetchCredentials" />
</template>

<script setup>
// 引入必要的依赖
import { ref, reactive , onMounted, h } from 'vue'; 
import { message, Tag, Modal, Popconfirm } from 'ant-design-vue';
import axios from 'axios';  // 引入axios用于请求后端API
import CreateCredentialModal from './module/CreateCredentialModal.vue'; // 引入创建凭据模态框组件
import EditCredentialModal from './module/EditCredentialModal.vue'; // 引入编辑凭据模态框组件
import { showPermissionWarning } from '@/components/Global/PermissonWarning.vue'; // 引入权限警告组件
import IconFont from '@/icons'; // 引入图标组件

// 筛选条件
const searchAccount = ref('');
const searchType = ref('');

// 表格数据
const data = ref([]);

// 分页选项
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],  // 可选的分页大小
    showSizeChanger: true,  // 显示分页大小选择器
    total: 0,
});

// 表格滚动选项
const tableScroll = { y: 500 };

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
        title: '名称',
        dataIndex: 'name',
        width: 170,
    },
    {
        title: '类型',
        dataIndex: 'type',
        width: 170,
        customRender: ({ text }) => {
            let iconType = '';
            switch (text) {
                case '密码':
                    iconType = 'icon-mima2';
                    break;
                case '密钥':
                    iconType = 'icon-yuechi1';
                    break;
                case 'AccessKey':
                    iconType = 'icon-lianjie-connect1';
                    break;
            }
            return h('div', { style: 'display: flex; align-items: center;' }, [
                h(IconFont, { type: iconType, style: 'margin-right: 8px; font-size: 18px;' }),
                h('span', text)
            ]);
        }
    },
    {
        title: '账户',
        dataIndex: 'account',
        width: 170,
        customRender: ({ text }) => {
            // 如果账户字段为空，则填充为'-'符号并添加左边距显示
            return text ? text : h('div', { style: 'margin-left: 8px;' }, '-');
        }
    },
    {
        title: '备注',
        dataIndex: 'notes',
        width: 200,
    },
    {
        title: '创建时间',
        dataIndex: 'create_time',
        width: 190,
    },
    {
        title: '操作',
        dataIndex: 'crud',
        width: 170,
        customRender: ({ record }) => h('div', { style: 'display: flex; align-items: center; justify-content: left; gap: 12px;' }, [
            h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => openEditModal(record) }, '编辑'),
            h(Popconfirm, {
                title: `是否要删除 ${record.account} 账号?`,
                okText: 'Yes',
                cancelText: 'No',
                onConfirm: () => handleDeleteCredentials(record.id)     // 调用删除函数，并传递记录的ID
            }, {
                default: () => h('span', { style: 'color: red; cursor: pointer;' }, '删除')
            }),
        ])
    },
];

// 引用模态框组件的实例
const createCredentialModalRef = ref(null);
const editCredentialModalRef = ref(null);

// 打开新建凭据模态框
const openCreateModal = () => {
    createCredentialModalRef.value.showCreateModal();
};

// 打开编辑凭据模态框并传递当前记录数据
const openEditModal = (record) => {
    editCredentialModalRef.value.showEditModal(record);
};

// 获取凭据列表
const fetchCredentials = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken');
        // 发送请求获取凭据列表
        const response = await axios.get('/api/credentials/', {
            headers: {
                Authorization: `Bearer ${token}`,  // 在请求头中包含Token
            },
            params: {
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
                account: searchAccount.value,       // 将账户名筛选条件发送到后端
                type: searchType.value,             // 将类型筛选条件发送到后端
            },
        });
        // 直接使用后端返回的数据
        data.value = response.data.result;
        paginationOptions.total = response.data.pagination.total_items;
    } catch (error) {
        message.error('获取凭据列表失败');
    }
};

// 删除凭据
const handleDeleteCredentials = async (id) => {
    try {
        // 获取存储在localStorage中的Token
        const token = localStorage.getItem('accessToken');
        // 发送DELETE请求到后端以删除凭据
        await axios.delete(`/api/credentials/${id}/delete/`, {
            headers: {
                Authorization: `Bearer ${token}`,  // 在请求头中包含Token
            },
        });
        message.success('凭据删除成功');
        fetchCredentials();  // 重新加载凭据列表
    } catch (error) {
        // 处理请求错误
        message.error('凭据删除失败');
    }
};

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current;
    paginationOptions.pageSize = pagination.pageSize;
    fetchCredentials();
};

// 重置筛选条件
const resetFilters = () => {
    searchAccount.value = '';
    searchType.value = '';
    fetchCredentials();
};

// 初次加载时获取凭据列表
onMounted(() => {
    fetchCredentials();
});
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
