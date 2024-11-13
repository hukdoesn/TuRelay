<template>
  <div class="developing-container">
    <a-result
      status="info"
      title="功能开发中"
      sub-title="功能正在开发中，敬请期待..."
    >
      <template #icon>
        <span class="custom-icon">
          <code-outlined />
        </span>
      </template>
    </a-result>
  </div>
</template>

<script setup>
import { CodeOutlined } from '@ant-design/icons-vue';
</script>

<style scoped>
.developing-container {
  padding: 24px;
  background: #fff;
}

.custom-icon {
  font-size: 72px;
  color: #1890ff;
}
</style>