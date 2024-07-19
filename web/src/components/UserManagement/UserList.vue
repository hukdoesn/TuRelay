<template>
    <div class="content_tools">
      <div class="input_tools">
        <a-input class="input_item" addonBefore="用户名" v-model:value="searchUsername" placeholder="请输入用户名" />
        <a-input class="input_item" addonBefore="邮箱" v-model:value.lazy="searchEmail" autofocus placeholder="请输入邮箱" />
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
      <a-table :columns="columns" :data-source="data" :pagination="paginationOptions" :scroll="tableScroll" size="small" @change="handleTableChange"/>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, h } from 'vue'
  import axios from 'axios'
  import { message } from 'ant-design-vue'
  
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
  const tableScroll = { y: 300 }
  
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
    },
    {
      title: '名称',
      dataIndex: 'name',
    },
    {
      title: '角色',
      dataIndex: 'role',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
    },
    {
      title: '状态',
      dataIndex: 'status',
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
    },
    {
      title: '操作',
      dataIndex: 'crud',
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
        id: (paginationOptions.current - 1) * paginationOptions.pageSize + index + 1,
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