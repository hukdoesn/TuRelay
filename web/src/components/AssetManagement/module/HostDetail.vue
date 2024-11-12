<template>
  <div v-if="hostDetail" class="host-detail">
    <a-descriptions title="主机详情" :column="1" :labelStyle="{ color: 'rgba(0, 0, 0, 0.45)' }">
      <a-descriptions-item label="主机名称">{{ hostDetail.name }}</a-descriptions-item>
      <a-descriptions-item label="连接状态">{{ hostDetail.status ? '连接成功' : '连接失败' }}</a-descriptions-item>
      <a-descriptions-item label="所属节点">{{ hostDetail.node }}</a-descriptions-item>
      <a-descriptions-item label="操作系统">{{ hostDetail.operating_system }}</a-descriptions-item>
      <a-descriptions-item label="IP地址">{{ hostDetail.network }}</a-descriptions-item>
      <a-descriptions-item label="端口">{{ hostDetail.port }}</a-descriptions-item>
      <a-descriptions-item label="协议">{{ hostDetail.protocol }}</a-descriptions-item>
      <a-descriptions-item label="凭据名称">{{ hostDetail.account_type }}</a-descriptions-item>
      <a-descriptions-item label="备注">{{ hostDetail.remarks || '-' }}</a-descriptions-item>
      <a-descriptions-item label="创建时间">{{ formatDate(hostDetail.create_time) }}</a-descriptions-item>
    </a-descriptions>
  </div>
  <div v-else class="loading-container">
    <a-spin />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import axios from 'axios';
import dayjs from 'dayjs';

const route = useRoute();
const hostDetail = ref(null);

// 获取主机详情
const fetchHostDetail = async () => {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get(`/api/hosts/${route.params.id}/`, {
      headers: {
        'Authorization': token
      }
    });
    console.log('Host detail response:', response.data);
    hostDetail.value = response.data;
  } catch (error) {
    console.error('Error fetching host detail:', error.response || error);
    message.error(error.response?.data?.error || '获取主机详情失败');
  }
};

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-';
};

onMounted(() => {
  console.log('Component mounted, route params:', route.params);
  if (route.params.id) {
    fetchHostDetail();
  }
});
</script>
