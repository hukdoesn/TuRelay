<template>
    <div v-if="!$route.params.username">
        <div class="content_tools">
            <div class="input_tools">
                <a-input class="input_item" addonBefore="用户名" v-model:value="searchUsername" placeholder="请输入用户名" />
                <a-input class="input_item" addonBefore="邮箱" v-model:value.lazy="searchEmail" placeholder="请输入邮箱" />
            </div>
            <div class="button_tools">
                <a-button class="button_font" @click="resetFilters">重置</a-button>
                <a-button class="button_font" type="primary" @click="fetchUsers">查询</a-button>
            </div>
        </div>
        <div class="button_create">
            <span>用户列表</span>
            <a-button class="button_item button_font" type="primary" @click="showCreateUserModal">新建用户</a-button>
        </div>
        <div class="table_user">
            <a-table style="font-size: 14px;" :columns="columns" :data-source="data" :pagination="paginationOptions"
                :scroll="tableScroll" size="middle" @change="handleTableChange" />
        </div>
        <!-- 重置密码模态框 -->
        <a-modal v-model:open="resetPasswordModalVisible" title="重置密码" @ok="handleResetPasswordOk"
            @cancel="handleResetPasswordCancel">
            <a-form :model="resetPasswordForm">
                <a-form-item label="新密码" name="password" :rules="formRules.password">
                    <a-input-password v-model:value="resetPasswordForm.newPassword" placeholder="请输入新密码" />
                </a-form-item>
            </a-form>
        </a-modal>
        <a-modal v-model:open="editModalVisible" title="编辑用户" @ok="handleEditOk" @cancel="handleEditCancel">
            <!-- 编辑用户表单 -->
            <a-form :model="editForm" labelAlign="right" :labelCol="{ span: 3 }"  layout="vertical">
                <a-form-item label="用户" name="username" :rules="formRules.username">
                    <a-input :disabled="true" v-model:value="editForm.username" />
                </a-form-item>
                <a-form-item label="名称" name="name" :rules="formRules.name">
                    <a-input v-model:value="editForm.name" />
                </a-form-item>
                <a-form-item label="手机" name="mobile" :rules="formRules.mobile">
                    <a-input v-model:value="editForm.mobile" />
                </a-form-item>
                <a-form-item label="邮箱" name="email" :rules="formRules.email">
                    <a-input v-model:value="editForm.email" />
                </a-form-item>
                <!-- 角色单选框 -->
                <a-form-item label="角色">
                    <a-radio-group v-model:value="editForm.role" @change="handleRoleChange('edit')">
                        <a-radio v-for="role in roles" :key="role.id" :value="role.id">{{ role.role_name }}</a-radio>
                    </a-radio-group>
                </a-form-item>
                <!-- 权限单选框 -->
                <a-form-item label="权限">
                    <a-radio-group v-model:value="editForm.permissions" :disabled="editForm.role === 1">
                        <a-radio v-for="permission in permissions" :key="permission.id" :value="permission.id">
                            {{ permission.name }}
                        </a-radio>
                    </a-radio-group>
                </a-form-item>
                <!-- 根据需要添加其他字段 -->
                <a-form-item label="MFA认证">
                    <a-radio-group v-model:value="editForm.mfa_level">
                        <a-radio :value="0">关闭</a-radio>
                        <a-radio :value="1">开启</a-radio>
                    </a-radio-group>
                </a-form-item>
            </a-form>
        </a-modal>
        <!-- 新建用户模态框 -->
        <a-modal v-model:open="createUserModalVisible" title="新建用户" @ok="handleCreateUserOk"
            @cancel="handleCreateUserCancel" @open="resetCreateUserForm">
            <a-form :model="createUserForm" :rules="formRules" ref="createFormRef" labelAlign="right"   layout="vertical"
                :labelCol="{ span: 3 }">
                <a-form-item label="用户" name="username" :rules="formRules.username">
                    <a-input v-model:value="createUserForm.username" placeholder="请输入用户名" />
                </a-form-item>
                <a-form-item label="名称" name="name" :rules="formRules.name">
                    <a-input v-model:value="createUserForm.name" placeholder="请输入名称" />
                </a-form-item>
                <a-form-item label="手机" name="mobile" :rules="formRules.mobile">
                    <a-input v-model:value="createUserForm.mobile" placeholder="请输入手机号" />
                </a-form-item>
                <a-form-item label="邮箱" name="email" :rules="formRules.email">
                    <a-input v-model:value="createUserForm.email" placeholder="请输入邮箱" />
                </a-form-item>
                <a-form-item label="密码" name="password" :rules="formRules.password">
                    <a-input-password v-model:value="createUserForm.password" placeholder="请输入密码" />
                </a-form-item>
                <a-form-item label="角色">
                    <a-radio-group v-model:value="createUserForm.role" @change="handleRoleChange('create')">
                        <a-radio v-for="role in roles" :key="role.id" :value="role.id">{{ role.role_name }}</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item v-if="showPermissions" label="权限">
                    <a-radio-group v-model:value="createUserForm.permissions">
                        <a-radio v-for="permission in permissions" :key="permission.id" :value="permission.id">{{
                permission.name }}</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item label="状态">
                    <a-switch v-model:checked="createUserForm.status" checked-children="启用" un-checked-children="禁用" />
                </a-form-item>
                <a-form-item label="MFA认证">
                    <a-radio-group v-model:value="createUserForm.mfa_level">
                        <a-radio :value="0">关闭</a-radio>
                        <a-radio :value="1">开启</a-radio>
                    </a-radio-group>
                </a-form-item>
            </a-form>
        </a-modal>
        <!-- 权限提示模态框 -->
        <!-- <showPermissionWarning ref="showPermissionWarning" /> -->
    </div>
    <router-view v-else></router-view>
</template>

<script setup>
// 引入所需模块和函数
import { ref, reactive, onMounted, h } from 'vue'
import axios from 'axios'
import { message, Tag, Badge, Modal, Dropdown, Menu, Popconfirm, MenuItem } from 'ant-design-vue'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'

// 获取 router 实例
const router = useRouter()

// 显示新建用户模态框
const showCreateUserModal = () => {
    createUserModalVisible.value = true
    resetCreateUserForm()
}

// 搜索字段
const searchUsername = ref('')
const searchEmail = ref('')
// 表格数据和分页选项
const data = ref([])
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],  // 可选的分页大小
    showSizeChanger: true,  // 显示分页大小选择器
    total: 0,
})
// 表格滚动选项
const tableScroll = { y: 400 }
// 编辑模态框相关
const editModalVisible = ref(false)
const editForm = reactive({
    username: '',
    name: '',
    mobile: '',
    email: '',
    password: '',
    role: '',
    permissions: [],
    // 添加其他字段
    mfa_level: 0,
})

// 重置密码模态框相关
const resetPasswordModalVisible = ref(false)
const resetPasswordForm = reactive({
    username: '',
    newPassword: '',
})

// 新建用户模态框相关
const createUserModalVisible = ref(false)
const createUserForm = reactive({
    username: '',
    name: '',
    password: '',
    mobile: '',
    email: '',
    role: '',
    permissions: [],
    status: true,
    mfa_level: 0,  // 默认关闭MFA
})

const formRules = reactive({
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 15, message: '用户名长度在 3 到 15 个字符', trigger: 'blur' },
        // 限制中文且只允许英语或拼音的新规则
        { pattern: /^[a-zA-Z0-9]+$/, message: '用户名只能包含英文', trigger: 'blur' }
    ],
    name: [
        { required: true, message: '请输入名称', trigger: 'blur' }
    ],
    mobile: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[0-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
    ],
    email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能小于 6 个字符', trigger: 'blur' }
    ],
    role: [
        { required: true, message: '请选择角色', trigger: 'change' }
    ],
    permissions: [
        { required: true, message: '请选择权限', trigger: 'change' },
        { type: 'array', min: 1, message: '至少选择一个权限', trigger: 'change' }
    ]
});

const createFormRef = ref(null);  // 用于重置用户表单的ref

// 获取角色和权限数据
const roles = ref([])
const permissions = ref([])

// 是否显示编辑权限字段
const editShowPermissions = ref(false)

// 获取角色和权限数据
const rolesPermissions = ref([])


// 是否显示新建权限字段
const showPermissions = ref(false)

// 权限模态框的引用
const permissionModal = ref(null)

// 表格列定义
const columns = [
    {
        title: '编号',
        dataIndex: 'id',
        width: 100,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,  // 前端编号排序
        customRender: ({ text, record }) => h('div', {
            class: 'id-link',
            onClick: () => viewDetail(record.username),
        }, text)
    },
    {
        title: '用户名',
        dataIndex: 'username',
        width: 170,
        customRender: ({ text, record }) => h('a', {
            class: 'table-link',
            onClick: () => viewDetail(record.username)
        }, text)
    },
    {
        title: '名称',
        dataIndex: 'name',
        width: 170,
    },
    {
        title: '角色',
        dataIndex: 'role',
        customRender: ({ text }) => {
            const [roleName, description] = typeof text === 'string' ? text.split(' - ') : [text, ''];
            return h('span', [
                roleName,
                description ? h('span', [
                    '\u00A0\u00A0',  // 添加两个不间断空格
                    h(Tag, { bordered: false, color: 'rgba(22, 119, 255, 0.8)' }, () => h('span', { style: { fontSize: '10px' } }, description))  // 设置字体大小为14px
                ]) : null
            ]);
        }
    },
    {
        title: '手机',
        dataIndex: 'mobile',
        width: 170,
    },
    {
        title: '邮箱',
        dataIndex: 'email',
    },
    {
        title: '状态',
        dataIndex: 'status',
        width: 120,
        customRender: ({ record }) => {
            const status = record.status ? 'error' : 'success';
            const text = record.status ? '锁定' : '启用';
            return h('div', { style: 'display: flex;  align-items: center; gap: 8px;' }, [
                h(Badge, { status }),
                h('span', text)
            ]);
        }
    },
    {
        title: '创建时间',
        dataIndex: 'create_time',
        customRender: ({ text }) => {
            return dayjs(text).format('YYYY-MM-DD HH:mm:ss');   // 格式化日期
        }
    },
    {
        title: '操作',
        dataIndex: 'crud',
        customRender: ({ record }) => h('div', { style: 'display: flex; align-items: center; justify-content: left; gap: 12px;' }, [
            h('span', { style: 'color: rgb(22,119,255); cursor: pointer;', onClick: () => showEditModal(record) }, '编辑'),
            h(Popconfirm, {
                title: `是否要删除 ${record.username} 账号?`,
                okText: 'Yes',
                cancelText: 'No',
                onConfirm: () => handleDeleteUser(record.username)
            }, {
                default: () => h('span', { style: 'color: red; cursor: pointer;' }, '删除')
            }),
            h(Dropdown, {
                overlay: h(Menu, null, {
                    default: () => [
                        h(MenuItem, { key: 'view', onClick: () => viewDetails(record) }, { default: () => '查看详情' }),
                        h(MenuItem, { key: 'reset', onClick: () => resetPassword(record) }, { default: () => '重置密码' }),
                        // 根据record的status决定是显示锁定还是解锁
                        h(MenuItem, { key: 'unlock', onClick: () => toggleUserStatus(record) }, { default: () => record.status ? '解锁用户' : '锁定用户' }),
                    ]
                }),
                trigger: 'click, hover',
                placement: "bottomLeft"
            }, {
                default: () => h('span', { style: 'cursor: pointer; color: rgb(20,93,254);' }, '...')
            })
        ])
    },
]


// 获取用户列表数据
const fetchUsers = async () => {
    try {
        // 从localStorage获取Token
        const token = localStorage.getItem('accessToken')
        // 发送请求获取用户数据
        const response = await axios.get('/api/users/', {
            headers: {
                'Authorization': token  // 在请求头中包含Token
            },
            params: {
                username: searchUsername.value,
                email: searchEmail.value,
                page: paginationOptions.current,
                page_size: paginationOptions.pageSize,
            }
        })
        // 遍历结果数据，重新生成前端编号
        data.value = response.data.results.map((user, index) => ({
            ...user,
            id: index + 1,  // 当前页的数据从1开始编号
            user_id: user.user_id,  // 包含实际的数据库用户ID
        }))
        paginationOptions.total = response.data.count
    } catch (error) {
        // 获取用户列表失败的提示
        message.error('获取用户列表失败')
    }
}

// 获取角色和权限数据
const fetchRolesAndPermissions = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        const response = await axios.get('/api/roles_permissions/', {
            headers: {
                'Authorization': token  // 在请求头中包含Token
            }
        })
        roles.value = response.data.roles
        permissions.value = response.data.permissions
        rolesPermissions.value = response.data.roles_permission  // 保存 roles_permission 数据
    } catch (error) {
        message.error('获取角色和权限数据失败')
    }
}

// 重置搜索条件
const resetFilters = () => {
    // 清空搜索字段
    searchUsername.value = ''
    searchEmail.value = ''
    // 重新获取用户列表
    fetchUsers()
}

// 新建用户确认处理函数
const handleCreateUserOk = async () => {
    // 触发表单验证
    try {
        await createFormRef.value.validateFields();
    } catch (validationError) {
        message.error('请检查表单是否填写正确');
        console.error('表单验证错误:', validationError);
        return; // 如果验证失败，则提前返回
    }
    try {
        const token = localStorage.getItem('accessToken');
        const formData = {
            ...createUserForm,
            permissions: Array.isArray(createUserForm.permissions) ? createUserForm.permissions : [createUserForm.permissions]
        };

        // 发送POST请求以创建新用户
        await axios.post('/api/users/create/', formData, {
            headers: {
                'Authorization': `Bearer ${token}`  // 添加Bearer前缀
            }
        });

        message.success('新建用户成功');
        createUserModalVisible.value = false;
        fetchUsers();  // 重新获取用户列表
    } catch (error) {
        // 只有在不是403错误时才显示错误消息
        if (!error.response || error.response.status !== 403) {
            message.error('新建用户失败');
        }
    }
};

// 新建用户取消处理函数
const handleCreateUserCancel = () => {
    createUserModalVisible.value = false
}

// 重置新建用户表单
const resetCreateUserForm = () => {
    createUserForm.username = ''
    createUserForm.name = ''
    createUserForm.password = ''
    createUserForm.mobile = ''
    createUserForm.email = ''
    createUserForm.role = ''
    createUserForm.permissions = []
    createUserForm.status = true
    showPermissions.value = false
    if (createFormRef.value) {
        createFormRef.value.resetFields()
    }
}

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    // 更新分页选项
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    // 重新获取用户列表
    fetchUsers()
}

// 显示编辑对话框
const showEditModal = (record) => {
    // 填充编辑表单数据
    editForm.username = record.username;
    editForm.name = record.name;
    editForm.mobile = record.mobile;
    editForm.email = record.email;
    editForm.mfa_level = record.mfa_level;  // 确保加载当前的 mfa_level 值

    // 从角色字段中提取角色 ID
    const roleId = roles.value.find(role => role.role_name === record.role.split(' - ')[0])?.id;
    editForm.role = roleId;

    // 设置权限
    if (record.permissions.length > 0) {
        editForm.permissions = record.permissions[0].id;
    } else {
        editForm.permissions = null;
    }

    editModalVisible.value = true;
};
// 删除用户
const handleDeleteUser = async (username) => {
    try {
        const token = localStorage.getItem('accessToken')  // 从localStorage获取Token
        await axios.delete(`/api/users/${username}/delete/`, {  // 发送DELETE请求
            headers: {
                'Authorization': token,  // 在请求头中包含Token
            }
        })
        message.success(`用户 ${username} 删除成功`)
        fetchUsers()  // 重新获取用户列表
    } catch (error) {
        // 只有在不是403错误时才显示错误消息
        if (!error.response || error.response.status !== 403) {
            message.error(`删除用户 ${username} 失败`)
        }
    }
};

// 查看详情
const viewDetails = (record) => {
    viewDetail(record.username);
};

// 显示重置密码对话框
const showResetPasswordModal = (record) => {
    // 填充重置密码表单数据
    resetPasswordForm.username = record.username
    resetPasswordModalVisible.value = true
}

// 重置密码确认处理函数
const handleResetPasswordOk = async () => {
    try {
        const token = localStorage.getItem('accessToken')  // 从localStorage获取Token
        // 发送POST请求重置密码
        const response = await axios.post(`/api/users/${resetPasswordForm.username}/reset_password/`, {
            new_password: resetPasswordForm.newPassword
        }, {
            headers: {
                'Authorization': token  // 在请求头中包含Token
            }
        });

        if (response.data.is_self_update) {
            message.success('密码修改成功，请重新登录');
            resetPasswordModalVisible.value = false;
            localStorage.clear();
            router.push('/login');
        } else {
            message.success(`用户 ${resetPasswordForm.username} 密码重置成功`);
            resetPasswordModalVisible.value = false;
        }
    } catch (error) {
        // 只有在不是403错误时才显示错误消息
        if (!error.response || error.response.status !== 403) {
            message.error(`重置用户 ${resetPasswordForm.username} 密码失败`);
        }
    }
};

// 重置密码取消处理函数
const handleResetPasswordCancel = () => {
    resetPasswordModalVisible.value = false
}

// 重置密码
const resetPassword = (record) => {
    showResetPasswordModal(record)
}

// 解除锁定
const toggleUserStatus = async (record) => {
    try {
        const token = localStorage.getItem('accessToken');
        const currentUsername = localStorage.getItem('name'); // 从 localStorage 获取当前用户名
        const newStatus = record.status ? 0 : 1;
        await axios.patch(`/api/users/${record.username}/lock/`, { status: newStatus }, {
            headers: {
                'Authorization': token
            }
        });
        const statusText = newStatus ? '禁用' : '启用';
        message.success(`用户 ${record.username} 已${statusText}`);

        // 如果禁用当前用户，清除 token 并重定向到登录页面
        if (newStatus) {
            if (record.username === currentUsername) { // 设有一个变量存储当前用户名
                localStorage.removeItem('accessToken');
                router.push('/login');
                return;
            }
        }
        fetchUsers();
    } catch (error) {
        // 只有在不是403错误时才显示错误消息
        if (!error.response || error.response.status !== 403) {
            message.error(`更改用户 ${record.username} 状态失败`);
        }
    }
};

// 编辑对话框确定
const handleEditOk = async () => {
    try {
        const token = localStorage.getItem('accessToken');
        // 构建更新数据
        const updateData = {
            username: editForm.username,
            email: editForm.email,
            name: editForm.name,
            mobile: editForm.mobile,
            role: editForm.role,
            permissions: Array.isArray(editForm.permissions) ? editForm.permissions : [editForm.permissions],
            mfa_level: editForm.mfa_level  // 确保包含 mfa_level
        };

        // 发送更新请求
        const response = await axios.put(`/api/users/${editForm.username}/update/`, updateData, {
            headers: {
                'Authorization': token
            }
        });

        if (response.status === 200) {
            message.success('用户信息更新成功');
            editModalVisible.value = false;
            fetchUsers();  // 重新获取用户列表
        }
    } catch (error) {
        // 只有在不是403错误时才显示错误消息
        if (!error.response || error.response.status !== 403) {
            message.error('用户信息更新失败');
        }
    }
};

// 编辑对话框取消
const handleEditCancel = () => {
    editModalVisible.value = false
}

// 处理角色变化
const handleRoleChange = (mode) => {
    let form;
    if (mode === 'create') {
        form = createUserForm;
    } else {
        form = editForm;
    }

    const selectedRoleId = form.role;

    if (selectedRoleId === 1) { // 假设1是“管理员”的ID
        form.permissions = [2]; // 自动设置为“全部权限”
        showPermissions.value = false; // 隐藏权限选择
        editShowPermissions.value = false;
    } else {
        form.permissions = []; // 清除权限
        showPermissions.value = mode === 'create'; // 仅在创建模式下显示权限选择
        editShowPermissions.value = mode === 'edit';
    }
};

// 初始化加载用户列表和角色、权限数据
onMounted(() => {
    fetchUsers()
    fetchRolesAndPermissions()
})

// 添加查看详情方法
const viewDetail = (username) => {
    router.push(`/user-management/user-list/${username}`);
};
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

.button_font {
    font-size: 12px;
}

/* 修改 input的addonBefore 和 placeholder 的字体大小 */
.ant-input-group-addon,
.ant-input::placeholder,
.ant-table-thead {
    font-size: 12px !important;
}

.id-link {
    background-color: #314659;
    color: white;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.2s;
}

.id-link:hover {
    background-color: rgba(0, 0, 0, 0.45); /* 鼠标悬浮时变浅色 */
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