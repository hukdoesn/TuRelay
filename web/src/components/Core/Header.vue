<template>
  <a-layout-header style="background: #fff; padding: 0; display: flex; justify-content: space-between; align-items: center;">
    <!-- 左边的 Breadcrumb 组件 -->
    <div style="padding: 0 16px;">
      <Breadcrumb />
    </div>
    <!-- 右边的操作区域 -->
    <div style="padding: 0 16px; display: flex; align-items: center; gap: 16px;">
      <!-- 终端图标按钮 -->
      <a-button type="link" @click="goToTerminal" style="display: flex; align-items: center; padding: 0;">
        <img width="18" height="18" src="https://img.icons8.com/parakeet-line/48/code.png" alt="code"/>
      </a-button>
      
      <!-- 用户下拉菜单 -->
      <Dropdown />
    </div>
  </a-layout-header>
</template>

<script setup>
import { useRouter } from 'vue-router';
import Breadcrumb from '../Core/Breadcrumb.vue';
import Dropdown from '../Core/Dropdown.vue';

const router = useRouter();

const goToTerminal = () => {
  const origin = window.location.origin;
  window.open(`${origin}/web-terminal`, '_blank');
};

const goToAbout = () => {
  router.push('/settings/about');
};

const openDocs = () => {
  window.open('https://github.com/hukdoesn/TuRelay', '_blank');
};

const openSupport = () => {
  window.open('https://github.com/hukdoesn/TuRelay', '_blank');
};
</script>

<style scoped>
/* 移除按钮的默认样式 */
:deep(.ant-btn-link) {
  color: inherit;
}

:deep(.ant-btn-link:hover) {
  color: #1890ff;
}

:deep(.ant-btn-link:focus) {
  color: inherit;
}

/* 下拉菜单样式 */
:deep(.ant-dropdown-menu) {
  min-width: 120px;
}

:deep(.ant-dropdown-menu-item) {
  padding: 8px 16px;
}

:deep(.ant-dropdown-menu-item a) {
  color: rgba(0, 0, 0, 0.85);
  text-decoration: none;
}

:deep(.ant-dropdown-menu-item:hover) {
  background-color: #f5f5f5;
}

:deep(.ant-dropdown-menu-item:hover a) {
  color: #1890ff;
}

/* 下拉链接样式 */
.ant-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.ant-dropdown-link:hover {
  color: #1890ff;
}
</style>
