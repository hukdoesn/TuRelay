<template>
    <div class="content_table">
        <!-- 筛选条件输入框 -->
        <div class="input_tools">
            <a-input v-model:value="searchName" class="input_item" addonBefore="名称" placeholder="请输入主机名称" />
            <a-input v-model:value="searchNode" class="input_item" addonBefore="节点" placeholder="请输入节点" />
        </div>
        <!-- 重置和查询按钮 -->
        <div class="button_tools">
            <a-button @click="resetFilters" class="button_font">重置</a-button>
            <a-button @click="fetchHosts" class="button_font" type="primary">查询</a-button>
        </div>
    </div>
    <!-- 新建主机按钮 -->
    <div class="button_create">
        <span>主机管理</span>
        <a-button @click="showCreateModal" class="button_item button_font" type="primary">新建主机</a-button>
    </div>
    <!-- 显示主机的表格 -->
    <div class="table_main">
        <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
            :scroll="tableScroll" size="middle" @change="handleTableChange" />
    </div>

    <!-- 创建主机的模态框 -->
    <a-modal v-model:open="isCreateModalVisible" title="新建主机" @ok="handleCreateOk" @cancel="handleCreateCancel"
        @open="resetCreateForm">
        <a-form :model="createForm" :rules="createRules" ref="createFormRef" layout="vertical">
            <a-form-item label="名称" name="name" :rules="createRules.name">
                <a-input v-model:value="createForm.name" placeholder="请输入主机名称" id="Create_Hosts" />
            </a-form-item>
            <a-form-item label="协议" name="protocol" :rules="createRules.protocol">
                <a-radio-group v-model:value="createForm.protocol" @change="handleProtocolChange">
                    <a-radio value="SSH">SSH</a-radio>
                    <a-radio value="RDP">RDP</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="IP 地址和端口" name="network">
                <a-input-group compact>
                    <!-- IP和端口的组合输入 -->
                    <a-form-item-rest>
                        <a-input v-model:value="createForm.network" placeholder="请输入IP地址" style="width: 70%" />
                    </a-form-item-rest>
                    <a-form-item-rest>
                        <a-input-number v-model:value="createForm.port" :min="1" :max="65535" placeholder="请输入端口号"
                            style="width: 30%" />
                    </a-form-item-rest>
                </a-input-group>
            </a-form-item>
            <a-form-item label="凭据选项" name="credential_option">
                <a-radio-group v-model:value="credentialOption" @change="handleCredentialOptionChange">
                    <a-radio value="existing">使用现有凭据</a-radio>
                    <a-radio value="new">创建新凭据</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="账户类型" name="account_type" :rules="createRules.account_type">
                <a-select v-model:value="createForm.account_type" placeholder="请选择账户类型"
                    :disabled="isAccountTypeDisabled">
                    <a-select-option v-for="credential in filteredCredentials" :key="credential.id"
                        :value="credential.id" :disabled="isCredentialTypeDisabled(credential.type)">
                        {{ credential.name }}
                    </a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="节点" name="node" :rules="createRules.node">
                <a-select v-model:value="createForm.node" placeholder="请选择节点">
                    <a-select-option v-for="node in availableNodes" :key="node.id" :value="node.id">
                        {{ node.name }}
                    </a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="备注" name="remarks">
                <a-textarea v-model:value="createForm.remarks" placeholder="请输入备注" />
            </a-form-item>
        </a-form>
        <template #footer>
            <!-- 底部按钮 -->
            <div style="display: flex; justify-content: space-between; width: 100%;">
                <a-button key="test" @click="handleTestConnection">测试连接</a-button>
                <div>
                    <!-- 取消和确认 -->
                    <a-button key="cancel" @click="handleCreateCancel">取消</a-button>
                    <a-button key="submit" type="primary" @click="handleCreateOk">确认</a-button>
                </div>
            </div>
        </template>
    </a-modal>

    <!-- 编辑主机的模态框 -->
    <a-modal v-model:open="isEditModalVisible" title="编辑主机" @ok="handleEditOk" @cancel="handleEditCancel"
        @open="prepareEditForm">
        <a-form :model="editForm" :rules="editRules" ref="editFormRef" layout="vertical">
            <a-form-item label="名称" name="name" :rules="editRules.name">
                <a-input v-model:value="editForm.name" placeholder="请输入主机名称" id="Edit_Hosts" />
            </a-form-item>
            <a-form-item label="协议" name="protocol" :rules="editRules.protocol">
                <a-radio-group v-model:value="editForm.protocol" @change="handleProtocolChange" :disabled="true">
                    <a-radio value="SSH">SSH</a-radio>
                    <a-radio value="RDP">RDP</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="IP 地址和端口" name="network">
                <a-input-group compact>
                    <!-- IP和端口的组合输入 -->
                    <a-form-item-rest>
                        <a-input v-model:value="editForm.network" placeholder="请输入IP地址" style="width: 70%" />
                    </a-form-item-rest>
                    <a-form-item-rest>
                        <a-input-number v-model:value="editForm.port" :min="1" :max="65535" placeholder="请输入端口号"
                            style="width: 30%" />
                    </a-form-item-rest>
                </a-input-group>
            </a-form-item>
            <a-form-item label="凭据选项" name="credential_option">
                <a-radio-group v-model:value="credentialOption" @change="handleCredentialOptionChange">
                    <a-radio value="existing">使用现有凭据</a-radio>
                    <a-radio value="new">创建新凭据</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="账户类型" name="account_type" :rules="editRules.account_type">
                <a-select v-model:value="editForm.account_type" placeholder="请选择账户类型" :disabled="isAccountTypeDisabled">
                    <a-select-option v-for="credential in filteredCredentials" :key="credential.id"
                        :value="credential.id" :disabled="isCredentialTypeDisabled(credential.type)">
                        {{ credential.name }}
                    </a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="节点" name="node" :rules="editRules.node">
                <a-select v-model:value="editForm.node" placeholder="请选择节点">
                    <a-select-option v-for="node in availableNodes" :key="node.id" :value="node.id">
                        {{ node.name }}
                    </a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="备注" name="remarks">
                <a-textarea v-model:value="editForm.remarks" placeholder="请输入备注" />
            </a-form-item>
        </a-form>
        <template #footer>
            <!-- 底部按钮 -->
            <div style="display: flex; justify-content: space-between; width: 100%;">
                <a-button key="test" @click="handleTestConnection">测试连接</a-button>
                <div>
                    <!-- 取消和确认 -->
                    <a-button key="cancel" @click="handleEditCancel">取消</a-button>
                    <a-button key="submit" type="primary" @click="handleEditOk">确认</a-button>
                </div>
            </div>
        </template>
    </a-modal>
    <!-- 打开新建凭据模态框并且结束调用handleProtocolChange方法请求最新凭据列表 -->
    <CreateCredentialModal ref="createCredentialModalRef" @refresh="handleProtocolChange" />
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { message, Tag, Modal, Popconfirm, Badge } from 'ant-design-vue';
import axios from 'axios';  // 引入axios用于请求后端API
import { showPermissionWarning, checkPermission } from '@/components/Global/PermissonWarning.vue'
import IconFont from '@/icons'
import CreateCredentialModal from '@/components/UserManagement/module/CreateCredentialModal.vue' // 引入创建凭据模态框组件

// 引用模态框组件的实例
const createCredentialModalRef = ref(null);

// 打开新建凭据模态框
const openCreateModal = () => {
    createCredentialModalRef.value.showCreateModal();
};

// 筛选条件
const searchName = ref('');
const searchNode = ref('');
const searchProtocol = ref('');

// 节点选项
const availableNodes = ref([]);

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

// 创建主机表单校验规则
const createRules = {
    name: [{ required: true, message: '名称不能为空', trigger: 'blur' }],
    protocol: [{ required: true, message: '协议不能为空', trigger: 'blur' }],
    network: [{ required: true, message: 'IP 地址不能为空', trigger: 'blur' }],
    port: [{ required: true, message: '端口不能为空', trigger: 'blur' }],
    account_type: [{ required: true, message: '账户类型不能为空', trigger: 'blur' }],
    node: [{ required: true, message: '节点不能为空', trigger: 'blur' }],
};

// 编辑主机表单校验规则
const editRules = {
    name: [{ required: true, message: '名称不能为空', trigger: 'blur' }],
    protocol: [{ required: true, message: '协议不能为空', trigger: 'blur' }],
    network: [{ required: true, message: 'IP 地址不能为空', trigger: 'blur' }],
    port: [{ required: true, message: '端口不能为空', trigger: 'blur' }],
    account_type: [{ required: true, message: '账户类型不能为空', trigger: 'blur' }],
    node: [{ required: true, message: '节点不能为空', trigger: 'blur' }],
};

// 创建主机的表单数据
const createForm = reactive({
    name: '',
    protocol: 'SSH', // 默认为SSH
    network: '',
    port: '',
    account_type: '',
    node: '',
    remarks: '',
});

// 编辑主机的表单数据
const editForm = reactive({
    name: '',
    protocol: '',
    network: '',
    port: '',
    account_type: '',
    node: '',
    remarks: '',
});

// 模态框显示状态
const isCreateModalVisible = ref(false);  // 新建模态框的显示状态
const isEditModalVisible = ref(false);    // 编辑模态框的显示状态

// 凭据选项控制
const credentialOption = ref('existing');

// 控制账户类型选择框的禁用状态
const isAccountTypeDisabled = ref(true);

// 过滤后的凭据列表（根据协议类型筛选）
const filteredCredentials = ref([]);

// 根据协议类型更新过滤的凭据列表
const updateFilteredCredentials = () => {
    axios.get('/api/credentials/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        params: {
            type: createForm.protocol === 'SSH' ? ['密码', '密钥'] : ['密码'],
        }
    }).then(response => {
        filteredCredentials.value = response.data.result;
        isAccountTypeDisabled.value = filteredCredentials.value.length === 0; // 根据结果启用/禁用
    }).catch(error => {
        message.error('获取凭据列表失败');
    });
};

const availableTypes = ref(['密码', '密钥']);

// 处理协议更改的功能
const handleProtocolChange = () => {
    updateFilteredCredentials();  // 根据选定的协议获取凭据

    if (createForm.protocol === 'SSH') {
        availableTypes.value = ['密码', '密钥']; // SSH的可用类型
    } else if (createForm.protocol === 'RDP') {
        availableTypes.value = ['密码']; // RDP的可用类型
    } else {
        availableTypes.value = []; // 默认或其他协议
    }

    isAccountTypeDisabled.value = availableTypes.value.length === 0; // 如果没有有效的类型，请禁用

    // 如果当前类型无效，请重置帐户类型
    if (!availableTypes.value.includes(createForm.account_type)) {
        createForm.account_type = '';
    }
};

// 处理凭据类型变化
const isCredentialTypeDisabled = (type) => {
    if (createForm.protocol === 'SSH') {
        return type === 'AccessKey'; // 禁用SSH的AccessKey
    } else if (createForm.protocol === 'RDP') {
        return type === '密钥' || type === 'AccessKey'; // 禁用RDP的密钥和访问密钥
    }
    return false; // Enable all for other cases
};


// 处理凭据选项变化
const handleCredentialOptionChange = () => {
    if (credentialOption.value === 'new') {
        // // 发出事件通知父组件
        // emit('open-create-credentials-modal')
        openCreateModal();
    }
};

// 显示创建模态框
const showCreateModal = () => {
    isCreateModalVisible.value = true;
    handleProtocolChange();  // 根据协议更新凭据
    resetCreateForm();  // 重置新建表单
    fetchNodes(); // 获取节点列表
};

// 显示编辑模态框并填充表单数据
const showEditModal = (record) => {
    isEditModalVisible.value = true;
    prepareEditForm(record); // This should populate the form
    currentHost.value = record;  // Make sure currentHost is set
    fetchNodes(); // 获取节点列表
};
const prepareEditForm = (record) => {
    // 设置要编辑的当前记录
    currentHost.value = record;

    // 用所选记录的数据填充表单字段
    editForm.name = record.name;
    editForm.protocol = record.protocol;
    editForm.network = record.network;
    editForm.port = record.port;
    editForm.account_type = record.account_type;

    // Here, you should set the node ID, not the name
    const node = availableNodes.value.find(n => n.name === record.node);
    editForm.node = node ? node.id : '';  // Set the node ID

    editForm.remarks = record.remarks;

    // 确保根据协议启用/禁用帐户类型
    handleProtocolChange();
};

// 重置新建表单的数据
const resetCreateForm = () => {
    createForm.name = '';
    createForm.protocol = 'SSH';
    createForm.network = '';
    createForm.port = '';
    createForm.account_type = '';
    createForm.node = '';
    createForm.remarks = '';
    isAccountTypeDisabled.value = true;
    credentialOption.value = 'existing'; // 默认使用现有凭据
};

// 重置编辑表单的数据
const resetEditForm = () => {
    editForm.name = '';
    editForm.protocol = '';
    editForm.network = '';
    editForm.port = '';
    editForm.account_type = '';
    editForm.node = '';
    editForm.remarks = '';
    isAccountTypeDisabled.value = true;
    credentialOption.value = 'existing'; // 默认使用现有凭据
};

// 新建主机的提交处理函数
const handleCreateOk = () => {
    checkPermission(() => {
        createFormRef.value.validate().then(async () => {
            try {
                const token = localStorage.getItem('accessToken');
                await axios.post('/api/hosts/create/', createForm, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                message.success('主机创建成功');
                isCreateModalVisible.value = false;
                fetchHosts(); // 重新加载主机列表
            } catch (error) {
                message.error('主机创建失败');
            }
        }).catch((error) => {
            message.error('请检查表单是否填写正确');
            console.log('验证失败:', error);
        });
    });
};

// 存储当前选中的主机数据
const currentHost = ref(null);

// 编辑主机的提交处理函数
const handleEditOk = () => {
    checkPermission(() => {
        editFormRef.value.validate().then(async () => {
            try {
                const token = localStorage.getItem('accessToken');

                // 在发送请求之前，将account_type转换为ID
                const selectedCredential = filteredCredentials.value.find(
                    (credential) => credential.name === editForm.account_type
                );

                // 确保account_type设置为ID，而不是名称
                const formData = { ...editForm };
                formData.account_type = selectedCredential ? selectedCredential.id : null;

                await axios.put(`/api/hosts/${currentHost.value.id}/update/`, formData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                message.success('主机更新成功');
                isEditModalVisible.value = false;
                fetchHosts(); // 重新加载主机列表
            } catch (error) {
                message.error('主机更新失败');
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
    resetCreateForm();      // 仅重置表单字段，不调用handleProtocolChange
};

// 处理编辑模态框的取消按钮
const handleEditCancel = () => {
    isEditModalVisible.value = false;
    resetEditForm();
};

// 表格列定义
const columns = [
    // {
    //     title: '编号',  
    //     dataIndex: 'id',
    //     // width: 100,
    //     showSorterTooltip: false,
    //     sorter: (a, b) => a.id - b.id,  // 前端编号排序
    //     customRender: ({ text }) => h('div', {
    //         style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
    //     }, text)
    // },
    {
        title: '名称',
        dataIndex: 'name',
        // width: 150,
    },
    {
        title: '状态',
        dataIndex: 'status',
        width: 100,
        customRender: ({ record }) => {
            const status = record.status ? 'success' : 'error';
            const text = record.status ? '成功' : '失败';
            return h('div', { style: 'display: flex;  align-items: center; gap: 8px;' }, [
                h(Badge, { status }),
                h('span', text)
            ]);
        }
    },
    {
        title: '节点',
        dataIndex: 'node',
        // width: 170,
    },
    {
        title: '操作系统',
        dataIndex: 'operating_system',
        // width: 150,
        customRender: ({ record }) => {
            let iconType = '';
            switch (record.protocol) {
                case 'SSH':
                    iconType = 'icon-linux';
                    break;
                case 'RDP':
                    iconType = 'icon-windows';
                    break;
            }
            return h('div', { style: 'display: flex; align-items: center;' }, [
                h(IconFont, { type: iconType, style: 'margin-right: 8px; font-size: 18px;' }),
                h('span', record.operating_system)
            ]);
        }
    },
    {
        title: 'IP地址',
        dataIndex: 'network',
        // width: 170,
        customRender: ({ record }) => {
            const ip = record.network;  // 获取IP
            const port = record.port;   // 获取端口
            return `${ip}:${port}`;
        }
    },
    {
        title: '协议',
        dataIndex: 'protocol',
        // width: 130,
        customRender: ({ record }) => {
            let color = '';
            if (record.protocol === 'SSH') {
                color = 'rgba(22, 119, 255, 0.8)';
            } else if (record.protocol === 'RDP') {
                color = 'rgba(74, 222, 128, 0.8)';
            }
            return h(Tag, { color: color }, {
                default: () => record.protocol
            });
        }
    },
    {
        title: '创建时间',
        dataIndex: 'create_time',
        // width: 190,
    },
    {
        title: '操作',
        dataIndex: 'crud',
        // width: 170,
        customRender: ({ record }) => h('div', { style: 'display: flex; align-items: center; justify-content: left; gap: 12px;' }, [
            h(IconFont, { type: 'icon-zhongduan', style: { fontSize: '18px', cursor: 'pointer' }, onClick: () => openWebTerminal(record.id) }),
            h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => showEditModal(record) }, '编辑'),
            h(Popconfirm, {
                title: `是否要删除 ${record.name} 主机?`,
                okText: 'Yes',
                cancelText: 'No',
                onConfirm: () => handleDeleteHost(record.id)     // 调用删除函数，并传递记录的ID
            }, {
                default: () => h('span', { style: 'color: red; cursor: pointer;' }, '删除')
            }),
        ])
    },
]

// 获取节点列表
const fetchNodes = async () => {
    try {
        const token = localStorage.getItem('accessToken');
        const response = await axios.get('/api/nodes/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        availableNodes.value = response.data;
    } catch (error) {
        message.error('获取节点列表失败');
    }
};

// 获取主机列表
const fetchHosts = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 发送请求获取主机列表
        const response = await axios.get('/api/hosts/', {
            headers: {
                'Authorization': `Bearer ${token}`  // 在请求头中包含Token
            },
            params: {
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
                name: searchName.value,       // 将主机名称筛选条件发送到后端
                node: searchNode.value,       // 将节点筛选条件发送到后端
                protocol: searchProtocol.value,     // 将协议筛选条件发送到后端
            },
        });
        // 直接使用后端返回的数据
        data.value = response.data.result;
        paginationOptions.total = response.data.pagination.total_items;
    } catch (error) {
        message.error('获取主机列表失败');
    }
}

// 删除主机
const handleDeleteHost = async (id) => {
    checkPermission(async () => {
        try {
            // 获取存储在localStorage中的Token
            const token = localStorage.getItem('accessToken');

            // 发送DELETE请求到后端以删除主机
            const response = await axios.delete(`/api/hosts/${id}/delete/`, {
                headers: {
                    Authorization: `Bearer ${token}`,  // 在请求头中包含Token
                },
            });
            message.success('主机删除成功');
            fetchHosts();  // 重新加载主机列表
        } catch (error) {
            // 处理请求错误
            message.error('主机删除失败');
        }
    })
};

const handleTestConnection = async () => {
    // 如果编辑，使用“editForm”，如果创建，使用“createForm”
    const form = isEditModalVisible.value ? editForm : createForm;

    // 在提出请求之前，将凭证名称转换为ID
    const selectedCredential = filteredCredentials.value.find(
        (credential) => credential.name === form.account_type
    );

    let credentialId = form.account_type;

    if (selectedCredential) {
        credentialId = selectedCredential.id; // Convert the name to the ID
    }

    try {
        const response = await axios.post('/api/hosts/test_connection/', {
            host_id: currentHost.value?.id || null,  // 如果是编辑，使用当前记录的ID，否则为 null
            ip_address: form.network, //来自正确表格的IP地址
            port: form.port,          //    表格的端口
            credential_id: credentialId, // 表格的凭据ID
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
            },
            timeout: 20000,  // 20秒超时
        });

        if (response.data.status === 0) {
            message.success('连接成功');
            fetchHosts();  // 重新加载主机列表
        } else {
            message.error(`连接失败: ${response.data.error}`);
        }
    } catch (error) {
        // 处理超时连接
        if (error.code === 'ECONNABORTED') {
            message.error('连接超时');
        }
    }
};

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current;
    paginationOptions.pageSize = pagination.pageSize;
    fetchHosts();
}

// 重置筛选条件
const resetFilters = () => {
    searchName.value = '';
    searchNode.value = '';
    searchProtocol.value = '';
    fetchHosts();
}

const openWebTerminal = (hostId) => {
    window.open(`/web-terminal/${hostId}`, '_blank');
};

// 初次加载时获取主机列表
onMounted(() => {
    fetchHosts();
    fetchNodes(); // 获取节点列表
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