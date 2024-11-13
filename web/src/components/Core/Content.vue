<template>
  <a-watermark
    v-if="showWatermark"
    :content="watermarkContent"
    :font-size="16"
    :gap-x="100"
    :gap-y="100"
    :offset-left="50"
    :z-index="10"
  >
    <div :style="{ background: '#fff', minHeight: '360px' }">
      <router-view />
    </div>
  </a-watermark>
  <div v-else :style="{ background: '#fff', minHeight: '360px' }">
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import dayjs from 'dayjs';

const showWatermark = ref(false);
const watermarkContent = ref([]);

// 更新水印内容
const updateWatermarkContent = () => {
  const username = localStorage.getItem('name');
  const currentTime = dayjs().format('YYYY-MM-DD HH:mm:ss');
  watermarkContent.value = [username, currentTime];
};

// 检查水印状态
const checkWatermarkStatus = () => {
  const watermarkEnabled = localStorage.getItem('watermarkEnabled') === 'true';
  showWatermark.value = watermarkEnabled;
  if (watermarkEnabled) {
    updateWatermarkContent();
  }
};

// 监听水印状态变化
watch(showWatermark, (newVal) => {
  if (newVal) {
    updateWatermarkContent();
    if (!timer) {
      timer = setInterval(updateWatermarkContent, 60000);
    }
  } else if (timer) {
    clearInterval(timer);
    timer = null;
  }
});

// 设置定时器，每分钟更新一次水印时间
let timer = null;

onMounted(() => {
  checkWatermarkStatus();
});

// 监听 localStorage 的变化
window.addEventListener('storage', (e) => {
  if (e.key === 'watermarkEnabled') {
    checkWatermarkStatus();
  }
});

// 自定义事件监听器，用于即时更新水印状态
window.addEventListener('updateWatermark', checkWatermarkStatus);

// 组件卸载时清除定时器和事件监听器
onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
  window.removeEventListener('updateWatermark', checkWatermarkStatus);
});
</script>

<style scoped>
.content-container {
  position: relative;
}
</style>