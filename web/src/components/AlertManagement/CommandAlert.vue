<template>
  <div v-if="!$route.params.id">
    <!-- 原有的命令告警列表内容 -->
    <div class="content_table">
      <div class="input_tools">
        <a-input class="input_item" addonBefore="主机名称" v-model:value="searchHost" placeholder="请输入主机名" />
        <a-input class="input_item" addonBefore="规则名称" v-model:value="searchName" placeholder="请输入规则名称" />
      </div>
      <div class="button_tools">
        <a-button class="button_font" @click="resetFilters">重置</a-button>
        <a-button class="button_font" type="primary" @click="fetchCommandAlerts">查询</a-button>
      </div>
    </div>
    <!-- 新建命令告警按钮 -->
    <div class="button_create">
      <span>命令告警</span>
      <a-button @click="showCreateModal" class="button_item button_font" type="primary">新建规则</a-button>
    </div>
    <div class="table_main">
      <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
        :scroll="tableScroll" size="middle" @change="handleTableChange" :rowKey="record => record.id">
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'operation'">
            <a-space>
              <a @click="viewDetail(record.id)">查看</a>
              <a @click="showEditModal(record)">编辑</a>
              <a-popconfirm
                title="是否要删除此命令告警规则？"
                @confirm="handleDelete(record.id)"
                okText="是"
                cancelText="否"
              >
                <a style="color: red;">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 新建命令告警规则模态框 -->
    <a-modal v-model:open="createModalVisible" title="新建命令告警规则" @ok="handleCreateOk" @cancel="handleCreateCancel">
      <a-form :model="createForm" :rules="formRules" ref="createFormRef" labelAlign="right" :labelCol="{ span: 6 }"
        layout="vertical">
        <a-form-item label="规则名称" name="name">
          <a-input v-model:value="createForm.name" placeholder="请输入规则名称" />
        </a-form-item>
        <a-form-item label="匹配类型" name="match_type">
          <a-radio-group v-model:value="createForm.match_type">
            <a-radio value="exact">精准匹配</a-radio>
            <a-radio value="fuzzy">模糊匹配</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="命令规则" name="command_rule">
          <a-textarea v-model:value="createForm.command_rule" :rows="4"
            placeholder="请输入命令规则，每行一个，例如：&#10;ls -l&#10;ps aux" />
        </a-form-item>
        <a-form-item label="关联主机" name="hosts">
          <a-select v-model:value="createForm.hosts" mode="multiple" placeholder="请选择关联主机">
            <a-select-option v-for="host in hostOptions" :key="host.id" :value="host.id">
              {{ host.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="告警联系人" name="alert_contacts">
          <a-select v-model:value="createForm.alert_contacts" placeholder="请选择告警联系人">
            <a-select-option v-for="contact in alertContactOptions" :key="contact.id" :value="contact.id">
              {{ contact.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="是否告警" name="is_active">
          <a-switch v-model:checked="createForm.is_active" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑命令告警规则模态框 -->
    <a-modal v-model:open="editModalVisible" title="编辑命令告警规则" @ok="handleEditOk" @cancel="handleEditCancel">
      <a-form :model="editForm" :rules="formRules" ref="editFormRef" labelAlign="right" :labelCol="{ span: 6 }"
        layout="vertical">
        <a-form-item label="规则名称" name="name">
          <a-input v-model:value="editForm.name" placeholder="请输入规则名称" />
        </a-form-item>
        <a-form-item label="匹配类型" name="match_type">
          <a-radio-group v-model:value="editForm.match_type">
            <a-radio value="exact">精准匹配</a-radio>
            <a-radio value="fuzzy">模糊匹配</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="命令规则" name="command_rule">
          <a-textarea v-model:value="editForm.command_rule" :rows="4"
            placeholder="请输入命令规则，每行一个，例如：&#10;ls -l&#10;ps aux" />
        </a-form-item>
        <a-form-item label="关联主机" name="hosts">
          <a-select v-model:value="editForm.hosts" mode="multiple" placeholder="请选关联主机">
            <a-select-option v-for="host in hostOptions" :key="host.id" :value="host.id">
              {{ host.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="告警联系人" name="alert_contacts">
          <a-select v-model:value="editForm.alert_contacts" placeholder="请选择告警联系人">
            <a-select-option v-for="contact in alertContactOptions" :key="contact.id" :value="contact.id">
              {{ contact.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="是否告警" name="is_active">
          <a-switch v-model:checked="editForm.is_active" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
  <router-view v-else></router-view>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { message, Modal, Popconfirm, Tag, Switch } from 'ant-design-vue';
import axios from 'axios';
import dayjs from 'dayjs';
import { useRouter } from 'vue-router';

const router = useRouter();

// 搜索字段
const searchHost = ref('')
const searchName = ref('')

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
        dataIndex: 'displayId',
        width: 80,
        showSorterTooltip: false,
        sorter: (a, b) => a.displayId - b.displayId,
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '名称',
        dataIndex: 'name',
        width: 150,
    },
    {
        title: '匹配类型',
        dataIndex: 'match_type',
        width: 120,
        customRender: ({ text }) => text === 'exact' ? '精准匹配' : '模糊匹配'
    },
    {
        title: '命令规则',
        dataIndex: 'command_rule',
        width: 200,
        customRender: ({ text }) => {
            return text.join(', ');
        }
    },
    {
        title: '关联主机',
        dataIndex: 'host_names',
        width: 280,
        customRender: ({ text }) => {
            const hostNames = Array.isArray(text) ? text : [];
            return h('div', {
                style: {
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    width: '100%'
                },
                title: hostNames.join(', ')
            }, hostNames.map(hostName => h(Tag, {
                color: 'rgba(22, 119, 255, 0.8)',
                bordered: false,
                style: { marginRight: '2px' }
            }, () => hostName))); // 子内容改为函数形式
        }
    },
    {
        title: '告警联系人',
        dataIndex: 'alert_contact_names',
        width: 120,
        customRender: ({ text }) => {
            return Array.isArray(text) ? text.join(', ') : text;
        }
    },
    {
        title: '是否告警',
        dataIndex: 'is_active',
        width: 100,
        customRender: ({ text, record }) => {
            return h(Switch, {
                checked: text,
                loading: record.switchLoading,
                onChange: (checked) => handleSwitchChange(checked, record)
            }, {
                checkedChildren: () => '是',
                unCheckedChildren: () => '否'
            });
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
        width: 150,
        customRender: ({ record }) => h('div', { style: 'display: flex; align-items: center; justify-content: left; gap: 12px;' }, [
        h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => showEditModal(record) }, '查看'),
        h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => showEditModal(record) }, '编辑'),
        h(Popconfirm, {
            okText: 'Yes',
            cancelText: 'No',
            onConfirm: () => handleDelete(record.id)
        }, {
            title: () => `是否要删除命令告警规则 ${record.name} ？`, // Correctly using slot function
            default: () => h('span', { style: 'color: red; cursor: pointer;' }, '删除')
        })
        ])
    },
]

// 新建命令告警规则表单
const createForm = reactive({
    name: '',
    command_rule: '',
    hosts: [],
    alert_contacts: [], // 修改为数组
    is_active: true,
    match_type: 'exact',
})

// 编辑命令告警规则表单
const editForm = reactive({
    id: null,
    name: '',
    command_rule: '',
    hosts: [],
    alert_contacts: [],
    is_active: true,
    match_type: 'exact',
})

// 表单规则
const formRules = {
    name: [
        { required: true, message: '请输入规则名称', trigger: 'blur' },
        { max: 150, message: '规则名称长度不能超过150个字符', trigger: 'blur' }
    ],
    command_rule: [
        { required: true, message: '请输入命令规则', trigger: 'blur' }
    ],
    hosts: [
        { required: true, message: '请选择关联主机', trigger: 'change', type: 'array' }
    ],
    alert_contacts: [
        { required: true, message: '请选择告警联系人', trigger: 'change' }
    ],
    match_type: [
        { required: true, message: '请选择匹配类型', trigger: 'change' }
    ],
}

// 模态框可见性
const createModalVisible = ref(false)
const editModalVisible = ref(false)

// 表单引用
const createFormRef = ref(null)
const editFormRef = ref(null)

// 主机选项
const hostOptions = ref([])

// 告警联系人选项
const alertContactOptions = ref([])

// 获取命令告警规则列表
const fetchCommandAlerts = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        const response = await axios.get('/api/command_alerts/', {
            headers: {
                'Authorization': token
            },
            params: {
                host: searchHost.value,
                name: searchName.value,
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
            }
        })
        data.value = response.data.results.map((alert, index) => ({
            ...alert,
            key: alert.id,
            displayId: index + 1,
            alert_contact_names: Array.isArray(alert.alert_contact_names) ? alert.alert_contact_names : [alert.alert_contact_names].filter(Boolean)
        }))
        paginationOptions.total = response.data.pagination.total_items
    } catch (error) {
        message.error('获取命令告警规则列表失败')
        console.error('Error fetching command alerts:', error)
    }
}

// 获取主机列表
const fetchHosts = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        const response = await axios.get('/api/command_alerts/hosts/', {
            headers: {
                'Authorization': token
            }
        })
        hostOptions.value = response.data.map(host => ({
            id: host.id,
            name: host.name
        }))
    } catch (error) {
        message.error('获取机列表失败')
        console.error('Error fetching hosts:', error)
    }
}

// 获取告警联人列表
const fetchAlertContacts = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        const response = await axios.get('/api/command_alerts/alert_contacts/', {
            headers: {
                'Authorization': token
            }
        })
        alertContactOptions.value = response.data.results.map(contact => ({
            id: contact.id,
            name: contact.name
        }))
    } catch (error) {
        message.error('获取告警联系人列表失败')
        console.error('Error fetching alert contacts:', error)
    }
}

// 重置搜索条件
const resetFilters = () => {
    searchHost.value = ''
    searchName.value = ''
    fetchCommandAlerts()
}

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    fetchCommandAlerts()
}

// 重置新建命令则表单
const resetCreateForm = () => {
    createForm.name = ''
    createForm.command_rule = ''
    createForm.hosts = []
    createForm.alert_contacts = []
    createForm.is_active = true
    if (createFormRef.value) {
        createFormRef.value.resetFields()
    }
}

// 显示新建命令告警规则模态框
const showCreateModal = () => {
    resetCreateForm()
    createModalVisible.value = true
}

// 处理新建命令告警规则
const handleCreateOk = async () => {
    try {
        await createFormRef.value.validateFields()
        const token = localStorage.getItem('accessToken')
        const formData = {
            ...createForm,
            command_rule: createForm.command_rule.split('\n').filter(rule => rule.trim() !== ''),
            hosts: createForm.hosts,
            alert_contacts: createForm.alert_contacts, // 这里不需要修改，因为现在它已经是一个数组
        }
        const response = await axios.post('/api/command_alerts/create/', formData, {
            headers: {
                'Authorization': token
            }
        })
        message.success('新建命令告警规则成功')
        createModalVisible.value = false
        fetchCommandAlerts()
        resetCreateForm()
    } catch (error) {
        message.error('新建命令告警规则失败')
        console.error('Error creating command alert:', error)
    }
}

// 取消新建命令告警规则
const handleCreateCancel = () => {
    createModalVisible.value = false
    resetCreateForm()
}

// 显示编辑命令告警规则模态框
const showEditModal = (record) => {
    editForm.id = record.id;
    editForm.name = record.name;
    editForm.command_rule = record.command_rule.join('\n');
    editForm.hosts = record.hosts;
    editForm.alert_contacts = record.alert_contacts;
    editForm.is_active = record.is_active;
    editForm.match_type = record.match_type; // 确保这行正确设置
    editModalVisible.value = true;
}

// 处理编辑命令告警规则
const handleEditOk = async () => {
    try {
        await editFormRef.value.validateFields()
        const token = localStorage.getItem('accessToken')
        const formData = {
            ...editForm,
            command_rule: editForm.command_rule.split('\n').filter(rule => rule.trim() !== ''),
            hosts: editForm.hosts,
            alert_contacts: Array.isArray(editForm.alert_contacts) ? editForm.alert_contacts : [editForm.alert_contacts].filter(Boolean),
        }
        const response = await axios.put(`/api/command_alerts/${editForm.id}/update/`, formData, {
            headers: {
                'Authorization': token
            }
        })
        message.success('编辑命令告警规则成功')
        editModalVisible.value = false
        fetchCommandAlerts()
    } catch (error) {
        message.error('编辑命令告警规则失败')
        console.error('Error editing command alert:', error)
    }
}

// 取消编辑命令告警规则
const handleEditCancel = () => {
    editModalVisible.value = false
    editFormRef.value.resetFields()
}

// 处理删除命令告警规则
const handleDelete = async (id) => {
    try {
        const token = localStorage.getItem('accessToken')
        await axios.delete(`/api/command_alerts/${id}/delete/`, {
            headers: {
                'Authorization': token
            }
        })
        message.success('删除命令告警规则成功')
        fetchCommandAlerts()
    } catch (error) {
        message.error('删除命令告警规则失败')
        console.error('Error deleting command alert:', error)
    }
}

// 处理开关变化
const handleSwitchChange = async (checked, record) => {
    try {
        record.switchLoading = true;
        const token = localStorage.getItem('accessToken')
        await axios.put(`/api/command_alerts/${record.id}/update/`,
            { is_active: checked },
            {
                headers: {
                    'Authorization': token
                }
            }
        );
        record.is_active = checked;
        message.success(`${record.name} 告警状态已更新`);
    } catch (error) {
        message.error('更新告警状态失败');
        console.error('Error updating alert status:', error);
    } finally {
        record.switchLoading = false;
    }
}

// 添加查看详情的方法
const viewDetail = (id) => {
  router.push(`/alert-management/command-alert/${id}`);
};

// 初始化加载命令告警规则列表、主机列表和告警联系人列表
onMounted(() => {
    fetchCommandAlerts()
    fetchHosts()
    fetchAlertContacts()
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

