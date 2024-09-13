<template>
    <!-- <IconFont type="icon-chongwuxiaolian" class="icon"/> -->
    <!-- <img src="@/assets/svg/不点睛.svg" alt=""> -->
    <a-dropdown>
      <a href="javascript:;" class="ant-dropdown-link" style="color: inherit;" @click.prevent>
        {{ Name }}
        <DownOutlined />
      </a>
      <template #overlay>
        <a-menu>
          <a-menu-item>
            <a href="javascript:;">个人信息</a>
          </a-menu-item>
          <a-menu-item>
            <a href="javascript:;">修改密码</a>
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item class="logout" @click="logout">
            <a href="javascript:;">退出登录</a>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
</template>
  
<script setup>
import { DownOutlined } from '@ant-design/icons-vue';
import Icon from '@ant-design/icons-vue/lib/components/Icon';
import { onMounted, ref } from 'vue';
import IconFont from '@/icons';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

const logout = () => {
    // 清除本地存储中的登录信息
    localStorage.clear();  // 更彻底地清除所有存储
    // 导航到登录页面
    router.push('/login');
};
const Name = ref(localStorage.getItem('name') || 'Tu Relay');

onMounted(() => {
  Name.value = localStorage.getItem('name') || 'Tu Relay';     // 从本地存储更新名字
})
</script>

<style>
  .logout .ant-dropdown-menu-title-content {
    color: black;
  }

  .logout .ant-dropdown-menu-title-content:hover {
    color: red;
  }

  .icon {
    margin-right: 8px;
  }
</style>