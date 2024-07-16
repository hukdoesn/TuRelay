<template>
  <a-config-provider :locale="zhCN">
    <router-view></router-view>
  </a-config-provider>
</template>

<script setup>
import zhCN from "ant-design-vue/es/locale/zh_CN";    //ant-design-vue自带设置中文
</script>
<style scoped>
</style>