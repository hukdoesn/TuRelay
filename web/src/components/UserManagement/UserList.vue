<template>
    <div class="content_tools">
        <div class="input_tools">
            <a-input class="input_item" addonBefore="用户名" v-model:value="searchUsername" placeholder="请输入用户名" />
            <a-input class="input_item" addonBefore="邮箱" v-model:value.lazy="searchEmail" autofocus
                placeholder="请输入邮箱" />
        </div>
        <div class="button_tools">
            <a-button class="button_font" @click="resetFilters">重置</a-button>
            <a-button class="button_font" type="primary" @click="fetchUsers">查询</a-button>
        </div>
    </div>
    <div class="button_create">
        <span>用户列表</span>
        <a-button class="button_item button_font" type="primary" @click="createUser">新建用户</a-button>
    </div>
    <div class="table_user">
        <a-table style="font-size: 13px;" :columns="columns" :data-source="data" :pagination="paginationOptions" :scroll="tableScroll"
            size="small" @change="handleTableChange" />
    </div>
    <a-modal v-model:visible="editModalVisible" title="编辑用户" @ok="handleEditOk" @cancel="handleEditCancel">
        <!-- 编辑用户表单 -->
        <a-form :model="editForm">
            <a-form-item label="用户名">
                <a-input v-model:value="editForm.username" disabled />
            </a-form-item>
            <a-form-item label="邮箱">
                <a-input v-model:value="editForm.email" />
            </a-form-item>
            <a-form-item label="名称">
                <a-input v-model:value="editForm.name" />
            </a-form-item>
            <!-- 根据需要添加其他字段 -->
        </a-form>
    </a-modal>
</template>

<script setup>
import { ref, reactive, h } from 'vue'
import axios from 'axios'
import { message, Tag, Badge, Modal, Dropdown, Menu } from 'ant-design-vue'
import dayjs from 'dayjs'

const searchUsername = ref('')
const searchEmail = ref('')
const data = ref([])
const paginationOptions = reactive({
    current: 1,
    pageSize: 10,
    pageSizeOptions: ['10', '20', '50', '100'],  // 可选的分页大小
    showSizeChanger: true,  // 显示分页大小选择器
    total: 0,
})
const tableScroll = { y: 400 }
const editModalVisible = ref(false)
const editForm = reactive({
    username: '',
    email: '',
    name: '',
    // 添加其他字段
})

const columns = [
    {
        title: '编号',
        dataIndex: 'id',
        width: 100,
        showSorterTooltip: false,
        sorter: (a, b) => a.id - b.id,  // 前端编号排序
        customRender: ({ text }) => h('div', {
            style: 'background-color: #314659; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'
        }, text)
    },
    {
        title: '用户名',
        dataIndex: 'username',
        width: 150,
    },
    {
        title: '名称',
        dataIndex: 'name',
        width: 150,
    },
    {
        title: '角色',
        dataIndex: 'role',
        customRender: ({ text }) => {
            const [roleName, description] = text.split(' - ');
            return h('span', [
                roleName,
                description ? h('span', [
                    '\u00A0\u00A0',  // 添加两个不间断空格
                    h(Tag, { bordered: false, color: 'processing' }, () => h('span', { style: { fontSize: '10px' } }, description))  // 设置字体大小为14px
                ]) : null
            ]);
        }
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
        customRender: ({ record }) => {
            return h('div', { style: 'display: flex; gap: 8px;' }, [
                h('a', { onClick: () => showEditModal(record) }, '编辑'),
                h('a', { onClick: () => confirmDelete(record) }, '删除'),
                h(Dropdown, {
                    overlay: () => h(Menu, [
                        h(Menu.Item, { key: 'view' }, () => h('a', { onClick: () => viewDetails(record) }, '查看详情')),
                        h(Menu.Item, { key: 'reset' }, () => h('a', { onClick: () => resetPassword(record) }, '重置密码')),
                        h(Menu.Item, { key: 'unlock' }, () => h('a', { onClick: () => unlockUser(record) }, '解除锁定')),
                    ])
                }, h('a', null, '...'))
            ]);
        }
    },
]

// 获取用户列表数据
const fetchUsers = async () => {
    try {
        const token = localStorage.getItem('accessToken')  // 从localStorage获取Token
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
        }))
        paginationOptions.total = response.data.count
    } catch (error) {
        message.error('获取用户列表失败')
        console.error('Error fetching users:', error)
    }
}

// 重置搜索条件
const resetFilters = () => {
    searchUsername.value = ''
    searchEmail.value = ''
    fetchUsers()
}

// 新建用户函数
const createUser = () => {
    // 在这里添加新建用户的逻辑
    console.log('新建用户')
}

// 处理表格分页和排序变化
const handleTableChange = (pagination) => {
    paginationOptions.current = pagination.current
    paginationOptions.pageSize = pagination.pageSize
    fetchUsers()
}

// 显示编辑对话框
const showEditModal = (record) => {
    editForm.username = record.username
    editForm.email = record.email
    editForm.name = record.name
    // 设置其他字段
    editModalVisible.value = true
}

// 确认删除
const confirmDelete = (record) => {
    Modal.confirm({
        title: `是否要删除 ${record.username} 账号?`,
        onOk: () => deleteUser(record),
        onCancel: () => console.log('取消删除'),
    });
}

// 删除用户
const deleteUser = async (record) => {
    try {
        const token = localStorage.getItem('accessToken')
        await axios.delete(`/api/users/${record.user_id}/`, {
            headers: {
                'Authorization': token
            }
        })
        message.success(`用户 ${record.username} 删除成功`)
        fetchUsers()  // 重新获取用户列表
    } catch (error) {
        message.error(`删除用户 ${record.username} 失败`)
        console.error('Error deleting user:', error)
    }
}

// 查看详情
const viewDetails = (record) => {
    console.log('查看详情', record)
}

// 重置密码
const resetPassword = (record) => {
    console.log('重置密码', record)
}

// 解除锁定
const unlockUser = (record) => {
    console.log('解除锁定', record)
}

// 编辑对话框确定
const handleEditOk = async () => {
    try {
        const token = localStorage.getItem('accessToken')
        await axios.put(`/api/users/${editForm.user_id}/`, {
            username: editForm.username,
            email: editForm.email,
            name: editForm.name,
            // 添加其他字段
        }, {
            headers: {
                'Authorization': token
            }
        })
        message.success('用户信息更新成功')
        editModalVisible.value = false
        fetchUsers()  // 重新获取用户列表
    } catch (error) {
        message.error('用户信息更新失败')
        console.error('Error updating user:', error)
    }
}

// 编辑对话框取消
const handleEditCancel = () => {
    editModalVisible.value = false
}

// 初始化加载用户列表
fetchUsers()
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
</style>