<template>
    <div v-if="!$route.params.id">
        <div class="content_table">
            <!-- 筛选条件输入框 -->
            <div class="input_tools">
                <a-input v-model:value="searchName" class="input_item" addonBefore="监控名称" placeholder="请输入监控名称" />
                <a-input v-model:value="searchDomain" class="input_item" addonBefore="域名" placeholder="请输入域名" />
            </div>
            <!-- 重置和查询按钮 -->
            <div class="button_tools">
                <a-button @click="resetFilters" class="button_font">重置</a-button>
                <a-button @click="fetchMonitors" class="button_font" type="primary">查询</a-button>
            </div>
        </div>

        <!-- 定时刷新下拉菜单和新建监控按钮 -->
        <div class="button_create">
            <span>域名监控</span>
            <div class="actions">
                <a-dropdown-button @click="handleButtonClick" class="dropdown_item">
                    刷新
                    <template #icon>
                        <DownOutlined v-if="!selectedRefreshInterval" />
                        <span v-else>{{ selectedRefreshInterval }}</span>
                    </template>
                    <template #overlay>
                        <a-menu @click="handleMenuClick">
                            <a-menu-item key="10">10s</a-menu-item>
                            <a-menu-item key="30">30s</a-menu-item>
                            <a-menu-item key="60">1m</a-menu-item>
                            <a-menu-item key="300">5m</a-menu-item>
                            <a-menu-item key="600">10m</a-menu-item>
                            <a-menu-item key="1800">30m</a-menu-item>
                            <a-menu-item key="3600">1h</a-menu-item>
                        </a-menu>
                    </template>
                </a-dropdown-button>
                <a-button @click="showCreateModal" class="button_item button_font" type="primary">新建监控</a-button>
            </div>
        </div>

        <!-- 显示监控的表格 -->
        <div class="table_main">
            <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
                :scroll="tableScroll" size="middle" @change="handleTableChange" />
        </div>

        <!-- 创建监控的模态框 -->
        <a-modal v-model:open="isCreateModalVisible" title="新建监控" @ok="handleCreateOk" @cancel="handleCreateCancel"
            @open="resetCreateForm">
            <a-form :model="createForm" :rules="createRules" ref="createFormRef" layout="vertical">
                <a-form-item label="监控名称" name="name" :rules="[{ required: true, message: '请输入监控名称' }]">
                    <a-input v-model:value="createForm.name" placeholder="请输入监控名称" />
                </a-form-item>
                <a-form-item label="域名" name="domain" :rules="[{ required: true, message: '请输入域名' }]">
                    <a-input v-model:value="createForm.domain" placeholder="请输入域名" />
                </a-form-item>
                <a-form-item label="启用监控" name="enable">
                    <a-switch v-model:checked="createForm.enable" @change="onEnableChange" />
                </a-form-item>
                <a-form-item label="监控频率" name="monitor_frequency" :rules="[{ required: true, message: '请选择监控频率' }]">
                    <a-radio-group v-model:value="createForm.monitor_frequency" :disabled="!createForm.enable">
                        <a-radio value="15">15秒</a-radio>
                        <a-radio value="30">30秒</a-radio>
                        <a-radio value="60">1分钟</a-radio>
                        <a-radio value="300">5分钟</a-radio>
                        <a-radio value="600">10分钟</a-radio>
                        <a-radio value="1800">30分钟</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item label="是否告警" name="alert">
                    <a-switch v-model:checked="createForm.alert" />
                </a-form-item>
            </a-form>
        </a-modal>

        <!-- 编辑监控的模态框 -->
        <a-modal v-model:open="isEditModalVisible" title="编辑监控" @ok="handleEditOk" @cancel="handleEditCancel">
            <a-form :model="editForm" :rules="editRules" ref="editFormRef" layout="vertical">
                <a-form-item label="监控名称" name="name" :rules="[{ required: true, message: '请输入监控名称' }]">
                    <a-input v-model:value="editForm.name" placeholder="请输入监控名称" />
                </a-form-item>
                <a-form-item label="域名" name="domain" :rules="[{ required: true, message: '请输入域名' }]">
                    <a-input v-model:value="editForm.domain" placeholder="请输入域名" />
                </a-form-item>
                <a-form-item label="启用监控" name="enable">
                    <a-switch v-model:checked="editForm.enable" @change="onEnableChange" />
                </a-form-item>
                <a-form-item label="监控频率" name="monitor_frequency" :rules="[{ required: true, message: '请选择监控频率' }]">
                    <a-radio-group v-model:value="editForm.monitor_frequency" :disabled="!editForm.enable">
                        <a-radio value="15">15秒</a-radio>
                        <a-radio value="30">30秒</a-radio>
                        <a-radio value="60">1分钟</a-radio>
                        <a-radio value="300">5分钟</a-radio>
                        <a-radio value="600">10分钟</a-radio>
                        <a-radio value="1800">30分钟</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item label="是否告警" name="alert">
                    <a-switch v-model:checked="editForm.alert" />
                </a-form-item>
            </a-form>
        </a-modal>
    </div>
    <router-view v-else></router-view>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue';
import { message, Tag, Modal, Popconfirm } from 'ant-design-vue';
import { DownOutlined } from '@ant-design/icons-vue';
import { useRouter } from 'vue-router';  // 添加路由导入
import axios from 'axios';
import { showPermissionWarning } from '@/components/Global/PermissonWarning.vue';

const router = useRouter();  // 初始化路由

// 筛选条件
const searchName = ref('');
const searchDomain = ref('');

// 表格数据
const data = ref([])

const createFormRef = ref(null); // 创建表单引用
const editFormRef = ref(null);   // 编辑表单引用

// 分页选项
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],
    showSizeChanger: true,
    total: 0,
})

// 表格滚动选项
const tableScroll = { y: 500 }

// 创建监控表单校验规则
const createRules = {
    name: [{ required: true, message: '请输入监控名称' }],
    domain: [{ required: true, message: '请输入域名' }],
    monitor_frequency: [{ required: true, message: '请选择监控频率' }],
};

// 编辑监控表单校验规则
const editRules = {
    name: [{ required: true, message: '请输入监控名称' }],
    domain: [{ required: true, message: '请输入域名' }],
    monitor_frequency: [{ required: true, message: '请选择监控频率' }],
};

// 创建监控的表单数据
const createForm = reactive({
    name: '',
    domain: '',
    enable: true,
    monitor_frequency: '60',
    alert: false,
});

// 编辑监控的表单数据
const editForm = reactive({
    name: '',
    domain: '',
    enable: true,
    monitor_frequency: '60',
    alert: false,
});

// 模态框显示状态
const isCreateModalVisible = ref(false);
const isEditModalVisible = ref(false);

// 刷新间隔状态和已选择的刷新间隔值
const refreshInterval = ref('10秒');  // 默认显示10秒
const selectedRefreshInterval = ref('');  // 用于存储已选择的刷新间隔值
let refreshTimer = null;  // 定时器，用于定时刷新页面

// 处理下拉菜单点击事件，设置刷新间隔并显示选择的值
const handleMenuClick = ({ domEvent }) => {
    const selectedValue = domEvent.target.innerText;  // 获取选中的显示值，如 "10s", "1m", "1h" 等
    selectedRefreshInterval.value = selectedValue;  // 更新显示的刷新间隔值

    // 清除之前的定时器
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }

    // 根据选择的间隔值设置定时刷新
    const intervalInMs = convertToMilliseconds(selectedValue);
    refreshTimer = setInterval(() => {
        fetchMonitors();  // 定时刷新页面
    }, intervalInMs);
};

// 将 "10s", "1m", "1h" 等转换为毫秒
const convertToMilliseconds = (interval) => {
    const unit = interval.slice(-1);  // 获取最后一个字符，判断是 s、m、h
    const value = parseInt(interval.slice(0, -1));  // 获取数值部分

    switch (unit) {
        case 's':
            return value * 1000;  // 秒转为毫秒
        case 'm':
            return value * 60 * 1000;  // 分钟转为毫秒
        case 'h':
            return value * 60 * 60 * 1000;  // 小时转为毫秒
        default:
            return 10000;  // 默认返回10秒的间隔
    }
};

// 处理下拉菜单按钮点击事件（如有需要，可以在此函数中添加额外逻辑）
const handleButtonClick = () => {
    message.info(`已刷新,当前选择的定时刷新为：${selectedRefreshInterval.value || '未选择'}`);
    fetchMonitors();
};

// 权限检查函数
const checkPermission = (callback) => {
    const token = localStorage.getItem('accessToken');
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (payload.is_read_only) {
        showPermissionWarning();
    } else {
        callback();
    }
};

// 启用监控开关的变化处理函数
const onEnableChange = (checked) => {
    // 无需更改频率；只需处理启用/禁用状态
    if (!checked) {
        createForm.monitor_frequency = createForm.monitor_frequency;    // 重置监控频率
        editForm.monitor_frequency = editForm.monitor_frequency;     // 重置监控频率
    }
};


// 显示创建模态框
const showCreateModal = () => {
        isCreateModalVisible.value = true;
        resetCreateForm();
};

// 显示编辑模态框并填充表单数据
const showEditModal = (record) => {
        isEditModalVisible.value = true;
        currentMonitor.value = record;
        editForm.name = record.name;
        editForm.domain = record.domain;
        editForm.enable = record.enable;
        editForm.monitor_frequency = record.monitor_frequency.toString();
        editForm.alert = record.alert;
};

// 重置新建表单的数据
const resetCreateForm = () => {
    createForm.name = '';
    createForm.domain = '';
    createForm.enable = true;
    createForm.monitor_frequency = '15';
    createForm.alert = false;
};

// 重置编辑表单的数据
const resetEditForm = () => {
    editForm.name = '';
    editForm.domain = '';
    editForm.enable = true;
    editForm.monitor_frequency = '15';  // 默认选择15秒
    editForm.alert = false;
};

// 新建监控的提交处理函数
const handleCreateOk = () => {
    checkPermission(() => {
        createFormRef.value.validate().then(async () => {
            try {
                const token = localStorage.getItem('accessToken');
                await axios.post('/api/monitor_domains/create/', createForm, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                message.success('监控创建成功');
                isCreateModalVisible.value = false;
                fetchMonitors(); // 重新加载监控列表
            } catch (error) {
                message.error('监控创建失败');
            }
        }).catch((error) => {
            message.error('请检查表单是否填写正确');
            console.log('验证失败:', error);
        });
    });
};

// 
const currentMonitor = ref(null);
// 编辑监控的提交处理函数
const handleEditOk = () => {
    checkPermission(() => {
        editFormRef.value.validate().then(async () => {
            try {
                const token = localStorage.getItem('accessToken');
                await axios.put(`/api/monitor_domains/${currentMonitor.value.id}/update/`, editForm, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                message.success('监控更新成功');
                isEditModalVisible.value = false;
                fetchMonitors();  // 重新加载监控列表
            } catch (error) {
                message.error('监控更新失败');
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
        title: '监控名称',
        dataIndex: 'name',
        width: 120,
        customRender: ({ text, record }) => h('a', {
            class: 'table-link',
            onClick: () => viewDetail(record.id)
        }, text)
    },
    {
        title: '域名',
        dataIndex: 'domain',
        width: 200,
    },
    {
        title: '连通性',
        dataIndex: 'connectivity',
        width: 100,
        customRender({ text }) {
            return h(Tag, { color: text ? 'green' : 'error' }, { default: () => text ? '可连接' : '不可连接' });
        }
    },
    {
        title: '状态码',
        dataIndex: 'status_code',
        width: 80,
    },
    {
        title: '重定向',
        dataIndex: 'redirection',
        width: 90,
        customRender({ text }) {
            return h(Tag, { color: text ? 'blue' : 'default' }, { default: () => text ? '有' : '无' });
        }
    },
    {
        title: '耗时(秒)',
        dataIndex: 'time_consumption',
        width: 100,
    },
    {
        title: 'TLS版本',
        dataIndex: 'tls_version',
        width: 90,
    },
    {
        title: 'HTTP版本',
        dataIndex: 'http_version',
        width: 100,
    },
    {
        title: '证书剩余天数',
        dataIndex: 'certificate_days',
        width: 100,
    },
    {
        title: '监控频率(秒)',
        dataIndex: 'monitor_frequency',
        width: 100,
    },
    {
        title: '是否告警',
        dataIndex: 'alert',
        width: 90,
        customRender({ text }) {
            return h(Tag, { color: text ? 'processing' : 'default' }, { default: () => text ? '是' : '否' });
        }
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
                title: `是否要删除监控 ${record.name} ？`,
                okText: 'Yes',
                cancelText: 'No',
                onConfirm: () => handleDeleteMonitor(record.id)     // 调用删除函数，并传递记录的ID
            }, {
                default: () => h('span', { style: 'color: red; cursor: pointer;' }, '删除')
            }),
        ])
    },
]

// 获取监控列表
const fetchMonitors = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 发送请求获取监控列表
        const response = await axios.get('/api/monitor_domains/', {
            headers: {
                'Authorization': `Bearer ${token}`  // 在请求头中包含Token
            },
            params: {
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
                name: searchName.value,       // 将监控名称筛选条件发送到后端
                domain: searchDomain.value,     // 将域名筛选条件发送到后端
            },
        });
        // 直接使用后端返回的数据
        data.value = response.data.result;
        paginationOptions.total = response.data.pagination.total_items;
    } catch (error) {
        message.error('获取监控列表失败');
    }
}

// 删除监控
const handleDeleteMonitor = async (id) => {
    checkPermission(async () => {
        try {
            // 获取存储在localStorage中的Token
            const token = localStorage.getItem('accessToken');

            // 发送DELETE请求到后端以删除监控
            await axios.delete(`/api/monitor_domains/${id}/delete/`, {
                headers: {
                    Authorization: `Bearer ${token}`,  // 在请求头中包含Token
                },
            });
            message.success('监控删除成功');
            fetchMonitors();  // 重新加载监控列表
        } catch (error) {
            // 处理请求错误
            message.error('监控删除失败');
        }
    })
};

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current;
    paginationOptions.pageSize = pagination.pageSize;
    fetchMonitors();
}

// 重置筛选条件
const resetFilters = () => {
    searchName.value = '';
    searchDomain.value = '';
    fetchMonitors();
}

// 初次加载时获取监控列表
onMounted(() => {
    fetchMonitors()
})

// 添加查看详情的方法
const viewDetail = (id) => {
  router.push(`/asset-management/websites/${id}`);
};
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

.actions {
    display: flex;
    align-items: center;
    gap: 16px;
    /* 下拉菜单和按钮之间的10px间隙 */
}

.dropdown_item {
    margin-right: 0;
    /* Adjust margin as needed */
}

:where(.css-dev-only-do-not-override-19iuou).ant-btn {
    font-size: 12px;
}

/* 修改 input的addonBefore 和 placeholder 的字体大小 */
.ant-input-group-addon,
.ant-input::placeholder,
.ant-table-thead {
    font-size: 12px !important;
}

.table-link {
    color: rgba(0, 0, 0, 0.88); 
    cursor: pointer;
    transition: opacity 0.3s ease; /* 添加透明度过渡效果 */
}

.table-link:hover {
    /* opacity: 0.8;  */
    color: rgba(0, 0, 0, 0.45);
}
</style>
