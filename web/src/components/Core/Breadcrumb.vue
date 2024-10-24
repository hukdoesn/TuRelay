<template>
  <!-- 面包屑导航栏 -->
  <a-breadcrumb style="margin: 16px 0">
    <!-- 遍历生成每个面包屑项 -->
    <a-breadcrumb-item v-for="(breadcrumb, index) in breadcrumbs" :key="index">
      <!-- 对于非最后一个面包屑项，使用 router-link 实现跳转 -->
      <router-link v-if="index !== breadcrumbs.length - 1" :to="breadcrumb.path">{{ breadcrumb.breadcrumbName }}</router-link>
      <!-- 对于最后一个面包屑项，显示当前路由的完整路径 -->
      <router-link v-else :to="route.fullPath">{{ breadcrumb.breadcrumbName }}</router-link>
    </a-breadcrumb-item>
  </a-breadcrumb>
</template>

<script setup>
import { useRoute } from 'vue-router'; // 导入 useRoute 以获取当前路由信息
import { computed } from 'vue'; // 导入 computed 以计算属性

const route = useRoute(); // 获取当前路由

// 计算面包屑数组
const breadcrumbs = computed(() => {
  const matched = route.matched; // 获取当前路由匹配的所有路由记录
  const breadcrumbsArray = matched.map(record => ({
    path: record.path, // 路由路径
    breadcrumbName: record.meta.breadcrumbName || 'Unknown' // 面包屑名称，默认值为 'Unknown'
  }));

  return breadcrumbsArray; // 返回面包屑数组
});
</script>