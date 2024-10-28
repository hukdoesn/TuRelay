<!-- 1 -->
<template>
    <div class="content_table">
        <div class="input_tools">
            <a-input class="input_item" addonBefore="名称" v-model:value="searchName" placeholder="请输入名称" />
            <a-input class="input_item" addonBefore="通知类型" v-model:value="searchNotifyType" placeholder="请输入通知类型" />
        </div>
        <div class="button_tools">
            <a-button class="button_font" @click="resetFilters">重置</a-button>
            <a-button class="button_font" type="primary" @click="fetchAlertContacts">查询</a-button>
        </div>
    </div>
    <!-- 新建告警联系人按钮 -->
    <div class="button_create">
        <span>告警联系人</span>
        <a-button @click="showCreateModal" class="button_item button_font" type="primary">新建告警联系人</a-button>
    </div>
    <div class="table_main">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>

    <!-- 新建告警联系人模态框 -->
    <a-modal v-model:open="createModalVisible" title="新建告警联系人" @ok="handleCreateOk" @cancel="handleCreateCancel">
        <a-form :model="createForm" :rules="formRules" ref="createFormRef" labelAlign="right" :labelCol="{ span: 6 }" layout="vertical" >
            <a-form-item label="名称" name="name">
                <a-input v-model:value="createForm.name" placeholder="请输入名称" />
            </a-form-item>
            <a-form-item label="通知类型" name="notify_type">
                <a-select v-model:value="createForm.notify_type" placeholder="请选择通知类型" >
                    <a-select-option value="钉钉">钉钉</a-select-option>
                    <a-select-option value="企微">企微</a-select-option>
                    <a-select-option value="飞书">飞书</a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="Webhook" name="webhook">
                <a-input v-model:value="createForm.webhook" placeholder="请输入Webhook链接" />
            </a-form-item>
        </a-form>
    </a-modal>

    <!-- 编辑告警联系人模态框 -->
    <a-modal v-model:open="editModalVisible" title="编辑告警联系人" @ok="handleEditOk" @cancel="handleEditCancel">
        <a-form :model="editForm" :rules="formRules" ref="editFormRef" labelAlign="right" :labelCol="{ span: 6 }" layout="vertical">
            <a-form-item label="名称" name="name">
                <a-input v-model:value="editForm.name" placeholder="请输入名称" />
            </a-form-item>
            <a-form-item label="通知类型" name="notify_type">
                <a-select v-model:value="editForm.notify_type" placeholder="请选择通知类型">
                    <a-select-option value="钉钉">钉钉</a-select-option>
                    <a-select-option value="企微">企微</a-select-option>
                    <a-select-option value="飞书">飞书</a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="Webhook" name="webhook">
                <a-input v-model:value="editForm.webhook" placeholder="请输入Webhook链接" />
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { message, Modal, Popconfirm } from 'ant-design-vue';
import axios from 'axios';
import dayjs from 'dayjs';
import IconFont from '@/icons';

// 搜索字段
const searchName = ref('')
const searchNotifyType = ref('')

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
const tableScroll = { y: 400 }

// 表格列定义
const columns = [
    {
        title: '编号',
        dataIndex: 'id',
        width: 70,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '名称',
        dataIndex: 'name',
        width: 90,
    },
    {
        title: '创建人',
        dataIndex: 'creator',
        width: 90,
    },
    {
        title: '通知类型',
        dataIndex: 'notify_type',
        width: 90,
        customRender: ({ record }) => {
            let iconType ='';
            switch (record.notify_type) {
                case '钉钉':
                    iconType = 'icon-dingding';
                    break;
                case '企微':
                    iconType = 'icon-icon_qiyeweixin';
                    break;
                case '飞书':
                    iconType = 'icon-feishu';
                    break;
            }
            return h('div', { style: 'display: flex; align-items: center; gap: 8px;' }, [
                h(IconFont, {
                    type: iconType,
                    style: 'cursor: pointer; font-size: 20px; color:#1890ff;',
                }),
                h('span', null, record.notify_type),
            ]);
        }
    },
    {
        title: 'WebHook',
        dataIndex: 'webhook',
        width: 150,
        customRender: ({ text }) => {
            return text.length > 50 ? text.substring(0, 43) + '...' : text;
        }
    },
    {
        title: '创建时间',
        dataIndex: 'create_time',
        width: 120,
        customRender: ({ text }) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
        title: '操作',
        dataIndex: 'operation',
        width: 100,
        customRender: ({ record }) => h('div', { style: 'display: flex; align-items: center; justify-content: left; gap: 12px;' }, [
            h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => showEditModal(record) }, '编辑'),
            h(Popconfirm, {
                title: `是否要删除告警联系人 ${record.name} ？`,
                okText: 'Yes',
                cancelText: 'No',
                onConfirm: () => handleDelete(record.name)     // 使用 name 而不是 id
            }, {
                default: () => h('span', { style: 'color: red; cursor: pointer;' }, '删除')
            })
        ])
    },
]

// 新建告警联系人表单
const createForm = reactive({
    name: '',
    notify_type: null,
    webhook: '',
})

// 编辑告警联系人表单
const editForm = reactive({
    id: null,
    originalName: '', // 保存原始名称
    name: '',
    notify_type: null,
    webhook: '',
})

// 表单规则
const formRules = {
    name: [
        { required: true, message: '请输入名称', trigger: 'blur' },
        { max: 150, message: '名称长度不能超过150个字符', trigger: 'blur' }
    ],
    notify_type: [
        { required: true, message: '请选择通知类型', trigger: 'change' }
    ],
    webhook: [
        { required: true, message: '请输入Webhook链接', trigger: 'blur' },
        { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
    ]
}

// 模态框可见性
const createModalVisible = ref(false)
const editModalVisible = ref(false)

// 表单引用
const createFormRef = ref(null)
const editFormRef = ref(null)

// 获取告警联系人列表
const fetchAlertContacts = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        const response = await axios.get('/api/alert_contacts/', {
            headers: {
                'Authorization': token
            },
            params: {
                name: searchName.value,
                notify_type: searchNotifyType.value,
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
            }
        })
        // 遍历结果数据，重新生成前端编号
        data.value = response.data.results.map((alertContact, index) => ({
            ...alertContact,
            id: index + 1,       // 当前页的数据从1开始编号
        }))
        paginationOptions.total = response.data.pagination.total_items
    } catch (error) {
        message.error('获取告警联系人列表失败')
        console.error('Error fetching alert contacts:', error)
    }
}

// 重置搜索条件
const resetFilters = () => {
    searchName.value = ''
    searchNotifyType.value = ''
    fetchAlertContacts()
}

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    fetchAlertContacts()
}

// 重置新建告警联系人表单
const resetCreateForm = () => {
    createForm.name = ''
    createForm.notify_type = null
    createForm.webhook = ''
    if (createFormRef.value) {
        createFormRef.value.resetFields()
    }
}

// 显示新建告警联系人模态框
const showCreateModal = () => {
    resetCreateForm()
    createModalVisible.value = true
}

// 处理新建告警联系人
const handleCreateOk = async () => {
    try {
        await createFormRef.value.validateFields()
        const token = localStorage.getItem('accessToken')
        const creator = localStorage.getItem('name')
        const response = await axios.post('/api/alert_contacts/create/', {
            ...createForm,
            creator: creator
        }, {
            headers: {
                'Authorization': token
            }
        })
        message.success('新建告警联系人成功')
        createModalVisible.value = false
        fetchAlertContacts()
        resetCreateForm()
    } catch (error) {
        message.error('新建告警联系人失败')
        console.error('Error creating alert contact:', error)
    }
}

// 取消新建告警联系人
const handleCreateCancel = () => {
    createModalVisible.value = false
    resetCreateForm()
}

// 显示编辑告警联系人模态框
const showEditModal = (record) => {
    editForm.originalName = record.name // 保存原始名称
    editForm.name = record.name
    editForm.notify_type = record.notify_type
    editForm.webhook = record.webhook
    editModalVisible.value = true
}

// 处理编辑告警联系人
const handleEditOk = async () => {
    try {
        await editFormRef.value.validateFields()
        const token = localStorage.getItem('accessToken')
        const response = await axios.put(`/api/alert_contacts/${editForm.originalName}/update/`, editForm, {
            headers: {
                'Authorization': token
            }
        })
        message.success('编辑告警联系人成功')
        editModalVisible.value = false
        fetchAlertContacts()
    } catch (error) {
        message.error('编辑告警联系人失败')
        console.error('Error editing alert contact:', error)
    }
}

// 取消编辑告警联系人
const handleEditCancel = () => {
    editModalVisible.value = false
    editForm.notify_type = null  // Set to null
    editFormRef.value.resetFields()
}

// 处理删除告警联系人
const handleDelete = async (name) => {
    try {
        const token = localStorage.getItem('accessToken')
        await axios.delete(`/api/alert_contacts/${name}/delete/`, {
            headers: {
                'Authorization': token
            }
        })
        message.success('删除告警联系人成功')
        fetchAlertContacts()
    } catch (error) {
        message.error('删除告警联系人失败')
        console.error('Error deleting alert contact:', error)
    }
}
onMounted(() => {
    fetchAlertContacts()
})
</script>

<style scoped>
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
    min-width: 200px;
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

