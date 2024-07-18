<template>
  <a-layout-header style="background: #fff; padding: 0; display: flex; justify-content: space-between; align-items: center;">
    <!-- 左边的 Breadcrumb 组件 -->
    <div style="padding: 0 16px;">
      <Breadcrumb />
    </div>
    <!-- 右边的 Dropdown 下拉菜单 -->
    <div style="padding: 0 16px;">
      <Dropdown />
    </div>
  </a-layout-header>
</template>

<script setup>
  import Breadcrumb from '../Core/Breadcrumb.vue';
  import Dropdown from '../Core/Dropdown.vue'; // 导入新的 Dropdown 组件
</script>
