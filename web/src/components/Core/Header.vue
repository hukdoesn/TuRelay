<template>
  <a-layout-header style="background: #fff; padding: 0; display: flex; justify-content: space-between; align-items: center;">
    <!-- 左边的 Breadcrumb 组件 -->
    <div style="padding: 0 16px;">
      <Breadcrumb />
    </div>
    <!-- 右边的操作区域 -->
    <div style="padding: 0 16px; display: flex; align-items: center; gap: 16px;">
      <!-- GitHub图标按钮 -->
      <a-button type="link" @click="goToGithub" style="display: flex; align-items: center; padding: 0;">
        <img width="21" height="21" src="https://img.icons8.com/ios-glyphs/30/github.png" alt="github"/>
      </a-button>
      <!-- 终端图标按钮 -->
      <a-button type="link" @click="goToTerminal" style="display: flex; align-items: center; padding: 0;">
        <img width="18" height="18" src="https://img.icons8.com/parakeet-line/48/code.png" alt="code"/>
      </a-button>
      <!-- Dropdown 下拉菜单 -->
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
  // 获取当前域名和端口
  const origin = window.location.origin;
  // 在新标签页打开终端页面
  window.open(`${origin}/web-terminal`, '_blank');
};

const goToGithub = () => {
  // 在新标签页打开GitHub页面
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
</style>
