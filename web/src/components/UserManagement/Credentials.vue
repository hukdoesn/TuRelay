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
        <a-button @click="showCreateModal" class="button_item button_font" type="primary">新建凭据</a-button>
    </div>
    <!-- 显示凭据的表格 -->
    <div class="table_main">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>

    <!-- 创建凭据的模态框 -->
    <a-modal v-model:open="isCreateModalVisible" title="新建凭据" @ok="handleCreateOk" @cancel="handleCreateCancel" @open="resetCreateForm">
        <a-form 
            :model="createForm" 
            :rules="createRules" 
            ref="createFormRef"
            layout="vertical"
        >
        <!-- layout="vertical"：将表单布局设置为垂直 -->
            <a-form-item label="名称" name="name" :rules="createRules.name">
                <a-input v-model:value="createForm.name" placeholder="请输入名称" />
            </a-form-item>
            <a-form-item label="类型" name="type" :rules="createRules.type">
                <a-radio-group v-model:value="createForm.type">
                    <a-radio value="密码">密码</a-radio>
                    <a-radio value="密钥">密钥</a-radio>
                    <a-radio value="AccessKey">AccessKey</a-radio>
                </a-radio-group>
            </a-form-item>
            <template v-if="createForm.type === '密码'">
                <a-form-item label="账户" name="account" :rules="createRules.account">
                    <a-input v-model:value="createForm.account" placeholder="请输入账户" />
                </a-form-item>
                <a-form-item label="密码" name="password" :rules="createRules.password">
                    <a-input type="password" v-model:value="createForm.password" placeholder="请输入密码" />
                </a-form-item>
            </template>
            <template v-if="createForm.type === '密钥'">
                <a-form-item label="账户" name="account" :rules="createRules.account">
                    <a-input v-model:value="createForm.account" placeholder="请输入账户" />
                </a-form-item>
                <a-form-item label="密钥" name="key" :rules="createRules.key">
                    <a-textarea v-model:value="createForm.key" placeholder="请输入密钥" />
                </a-form-item>
                <a-form-item label="密钥密码" name="key_password" :rules="createRules.key_password">
                    <a-input type="password" v-model:value="createForm.key_password" placeholder="请输入密钥密码" />
                </a-form-item>
            </template>
            <template v-if="createForm.type === 'AccessKey'">
                <a-form-item label="Key ID" name="KeyId" :rules="createRules.KeyId">
                    <a-input v-model:value="createForm.KeyId" placeholder="请输入Key ID" />
                </a-form-item>
                <a-form-item label="Key Secret" name="KeySecret" :rules="createRules.KeySecret">
                    <a-input v-model:value="createForm.KeySecret" placeholder="请输入Key Secret" />
                </a-form-item>
            </template>
            <a-form-item label="备注" name="notes">
                <a-textarea v-model:value="createForm.notes" placeholder="请输入备注" />
            </a-form-item>
        </a-form>
    </a-modal>

    <!-- 编辑凭据的模态框 -->
    <a-modal v-model:open="isEditModalVisible" title="编辑凭据" @ok="handleEditOk" @cancel="handleEditCancel">
        <a-form 
            :model="editForm" 
            :rules="editRules" 
            ref="editFormRef"
            layout="vertical"
        >
        <!-- layout="vertical"：将表单布局设置为垂直 -->
            <a-form-item label="名称" name="name" :rules="editRules.name">
                <a-input v-model:value="editForm.name" placeholder="请输入名称" />
            </a-form-item>
            <a-form-item label="类型" name="type" :rules="editRules.type">
                <a-radio-group v-model:value="editForm.type">
                    <a-radio value="密码">密码</a-radio>
                    <a-radio value="密钥">密钥</a-radio>
                    <a-radio value="AccessKey">AccessKey</a-radio>
                </a-radio-group>
            </a-form-item>
            <template v-if="editForm.type === '密码'">
                <a-form-item label="账户" name="account" :rules="editRules.account">
                    <a-input v-model:value="editForm.account" placeholder="请输入账户" />
                </a-form-item>
                <a-form-item label="密码" name="password" :rules="editRules.password">
                    <a-input type="password" v-model:value="editForm.password" placeholder="请输入新密码" />
                </a-form-item>
            </template>
            <template v-if="editForm.type === '密钥'">
                <a-form-item label="账户" name="account" :rules="editRules.account">
                    <a-input v-model:value="editForm.account" placeholder="请输入账户" />
                </a-form-item>
                <a-form-item label="密钥" name="key" :rules="editRules.key">
                    <a-textarea v-model:value="editForm.key" placeholder="请输入新密钥" />
                </a-form-item>
                <a-form-item label="密钥密码" name="key_password" :rules="editRules.key_password">
                    <a-input type="password" v-model:value="editForm.key_password" placeholder="请输入新密钥密码" />
                </a-form-item>
            </template>
            <template v-if="editForm.type === 'AccessKey'">
                <a-form-item label="Key ID" name="KeyId" :rules="editRules.KeyId">
                    <a-input v-model:value="editForm.KeyId" placeholder="请输入Key ID" />
                </a-form-item>
                <a-form-item label="Key Secret" name="KeySecret" :rules="editRules.KeySecret">
                    <a-input v-model:value="editForm.KeySecret" placeholder="请输入新Key Secret" />
                </a-form-item>
            </template>
            <a-form-item label="备注" name="notes">
                <a-textarea v-model:value="editForm.notes" placeholder="请输入备注" />
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<script setup>
import { ref, reactive , onMounted, h} from 'vue' 
import { message, Tag, Modal, Popconfirm } from 'ant-design-vue';
import axios from 'axios';  // 引入axios用于请求后端API
import {showPermissionWarning} from '@/components/Global/PermissonWarning.vue'
import IconFont from '@/icons'

// 筛选条件
const searchAccount = ref('');
const searchType = ref('');

// 表格数据
const data = ref([])

const createFormRef = ref(null); // 创建表单引用
const editFormRef = ref(null);   // 编辑表单引用

// 分页选项
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],  // 可选的分页大小
    showSizeChanger: true,  // 显示分页大小选择器
    total: 0,
})

// 表格滚动选项
const tableScroll = { y: 500 }

// 创建凭据表单校验规则
const createRules = {
    name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
    type: [{ required: true, message: '请选择类型', trigger: 'change' }],
    account: [
        { required: true, message: '请输入账户', trigger: 'blur' },
        { pattern: /^[a-zA-Z]+$/, message: '账户名只能包含英文', trigger: 'blur' },
    ],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
    key: [{ required: true, message: '请输入密钥', trigger: 'blur' }],
    key_password: [{ required: true, message: '请输入密钥密码', trigger: 'blur' }],
    KeyId: [{ required: true, message: '请输入Key ID', trigger: 'blur' }],
    KeySecret: [{ required: true, message: '请输入Key Secret', trigger: 'blur' }],
};

// 编辑凭据表单校验规则
const editRules = {
    name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
    type: [{ required: true, message: '请选择类型', trigger: 'change' }],
    account: [
        { required: true, message: '请输入账户', trigger: 'blur' },
        { pattern: /^[a-zA-Z]+$/, message: '账户名只能包含英文', trigger: 'blur' },
    ],
    password: [{ required: false, message: '请输入新密码', trigger: 'blur' }],
    key: [{ required: false, message: '请输入新密钥', trigger: 'blur' }],
    key_password: [{ required: false, message: '请输入新密钥密码', trigger: 'blur' }],
    KeyId: [{ required: true, message: '请输入Key ID', trigger: 'blur' }],
    KeySecret: [{ required: false, message: '请输入新Key Secret', trigger: 'blur' }],
};

// 创建凭据的表单数据
const createForm = reactive({
    name: '',
    type: '',
    account: '',
    password: '',
    key: '',
    key_password: '',
    KeyId: '',
    KeySecret: '',
    notes: '',
});

// 编辑凭据的表单数据
const editForm = reactive({
    name: '',
    type: '',
    account: '',
    password: '',
    key: '',
    key_password: '',
    KeyId: '',
    KeySecret: '',
    notes: '',
});

// 模态框显示状态
const isCreateModalVisible = ref(false);  // 新建模态框的显示状态
const isEditModalVisible = ref(false);    // 编辑模态框的显示状态

// 权限检查函数
const checkPermission = (callback) => {
    const token = localStorage.getItem('accessToken');
    const payload = JSON.parse(atob(token.split('.')[1])); // 解码JWT的负载部分
    if (payload.is_read_only) {
        showPermissionWarning();  // 调用分离的权限提示函数
    } else {
        callback();
    }
};

// 显示创建模态框
const showCreateModal = () => {
    checkPermission(() => {
        isCreateModalVisible.value = true;
        resetCreateForm();  // 重置新建表单
    });
};

// 显示编辑模态框并填充表单数据
const showEditModal = (record) => {
    checkPermission(() => {
        isEditModalVisible.value = true;

        // 设置要编辑的当前凭据
        currentCredential.value = record;

        // 填充编辑表单数据，密码、密钥、密钥密码和KeySecret保持为空
        editForm.name = record.name;
        editForm.type = record.type;
        editForm.account = record.account;
        editForm.notes = record.notes;

        editForm.password = ''; // 确保密码字段为空
        editForm.key = ''; // 确保密钥字段为空
        editForm.key_password = ''; // 确保密钥密码字段为空
        editForm.KeyId = record.KeyId; // 填充Key ID，如果存在
        editForm.KeySecret = ''; // 确保KeySecret字段为空
    });
};

// 重置新建表单的数据
const resetCreateForm = () => {
    createForm.name = '';
    createForm.type = '';
    createForm.account = '';
    createForm.password = '';
    createForm.key = '';
    createForm.key_password = '';
    createForm.KeyId = '';
    createForm.KeySecret = '';
    createForm.notes = '';
};

// 重置编辑表单的数据
const resetEditForm = () => {
    editForm.name = '';
    editForm.type = '';
    editForm.account = '';
    editForm.password = '';
    editForm.key = '';
    editForm.key_password = '';
    editForm.KeyId = '';
    editForm.KeySecret = '';
    editForm.notes = '';
};

// 新建凭据的提交处理函数
const handleCreateOk = () => {
    checkPermission(() => {
        createFormRef.value.validate().then(async () => {
            try {
                const token = localStorage.getItem('accessToken');
                await axios.post('/api/credentials/create/', createForm, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                message.success('凭据创建成功');
                isCreateModalVisible.value = false;
                fetchCredentials(); // 重新加载凭据列表
            } catch (error) {
                message.error('凭据创建失败');
            }
        }).catch((error) => {
            message.error('请检查表单是否填写正确');
            console.log('验证失败:', error);
        });
    });
};

// 存储当前选中的凭据数据
const currentCredential = ref(null);
// 编辑凭据的提交处理函数
const handleEditOk = () => {
    checkPermission(() => {
        editFormRef.value.validate().then(async () => {
            try {
                const token = localStorage.getItem('accessToken');
                await axios.put(`/api/credentials/${currentCredential.value.id}/update/`, editForm, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                message.success('凭据更新成功');
                isEditModalVisible.value = false;
                fetchCredentials(); // 重新加载凭据列表
            } catch (error) {
                message.error('凭据更新失败');
                console.error('Update failed:', error.response ? error.response.data : error.message);
            }
        }).catch((error) => {
            message.error('请检查表单是否填写正确');
            console.log('验证失败:', error);
        });
    });
};

// 处理创建模态框的取消按钮
const handleCreateCancel = () => {
    isCreateModalVisible.value = false;
    resetCreateForm();
};

// 处理编辑模态框的取消按钮
const handleEditCancel = () => {
    isEditModalVisible.value = false;
    resetEditForm();
};

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
        customRender: ({ text}) => {
            let iconType ='';
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
        // customRender: ({ text }) => h(Tag, { 
        //     color: 'processing',
        //     style: {  },
        //     bordered: false
        // }, () => h('span', text))
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
            h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => showEditModal(record) }, '编辑'),
            h(Popconfirm, {
                title: `是否要删除 ${record.username} 账号?`,
                okText: 'Yes',
                cancelText: 'No',
                onConfirm: () => handleDeleteCredentials(record.id)     // 调用删除函数，并传递记录的ID
            }, {
                default: () => h('span', { style: 'color: red; cursor: pointer;' }, '删除')
            }),
        ])
    },
]

// 获取凭据列表
const fetchCredentials = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 发送请求获取凭据列表
        const response = await axios.get('/api/credentials/', {
            headers: {
                'Authorization': `Bearer ${token}`  // 在请求头中包含Token
            },
            params: {
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
                account: searchAccount.value,       // 将账户名筛选条件发送到后端
                type: searchType.value,     // 将类型筛选条件发送到后端
            },
        });
        // 直接使用后端返回的数据
        data.value = response.data.result;
        paginationOptions.total = response.data.pagination.total_items;
    } catch (error) {
        message.error('获取凭据列表失败');
    }
}

// 删除凭据
const handleDeleteCredentials = async (id) => {
    checkPermission(async () => {
        try {
            // 获取存储在localStorage中的Token
            const token = localStorage.getItem('accessToken');

            // 发送DELETE请求到后端以删除凭据
            const response = await axios.delete(`/api/credentials/${id}/delete/`, {
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
    })  
};

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current;
    paginationOptions.pageSize = pagination.pageSize;
    fetchCredentials();
}

// 重置筛选条件
const resetFilters = () => {
    searchAccount.value = '';
    searchType.value = '';
    fetchCredentials();
}

// 初次加载时获取凭据列表
onMounted(() => {
    fetchCredentials()
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