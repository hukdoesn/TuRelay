<template>
  <div v-if="websiteDetail" class="website-detail">
    <a-descriptions title="站点监控详情" :column="1" :labelStyle="{ color: 'rgba(0, 0, 0, 0.45)' }">
      <a-descriptions-item label="监控名称">{{ websiteDetail.name }}</a-descriptions-item>
      <a-descriptions-item label="域名">{{ websiteDetail.domain }}</a-descriptions-item>
      <a-descriptions-item label="连通性">{{ websiteDetail.connectivity ? '可连接' : '不可连接' }}</a-descriptions-item>
      <a-descriptions-item label="状态码">{{ websiteDetail.status_code || '-' }}</a-descriptions-item>
      <a-descriptions-item label="重定向">{{ websiteDetail.redirection || '无' }}</a-descriptions-item>
      <a-descriptions-item label="耗时(秒)">{{ websiteDetail.time_consumption || '-' }}</a-descriptions-item>
      <a-descriptions-item label="TLS版本">{{ websiteDetail.tls_version || '-' }}</a-descriptions-item>
      <a-descriptions-item label="HTTP版本">{{ websiteDetail.http_version || '-' }}</a-descriptions-item>
      <a-descriptions-item label="证书剩余天数">{{ websiteDetail.certificate_days || '-' }}</a-descriptions-item>
      <a-descriptions-item label="监控频率(秒)">{{ websiteDetail.monitor_frequency }}</a-descriptions-item>
      <a-descriptions-item label="是否告警">{{ websiteDetail.alert ? '是' : '否' }}</a-descriptions-item>
      <a-descriptions-item label="创建时间">{{ formatDate(websiteDetail.create_time) }}</a-descriptions-item>
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
const websiteDetail = ref(null);

// 获取站点监控详情
const fetchWebsiteDetail = async () => {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get(`/api/monitor_domains/${route.params.id}/`, {
      headers: {
        'Authorization': token
      }
    });
    console.log('Website detail response:', response.data);
    websiteDetail.value = response.data;
  } catch (error) {
    console.error('Error fetching website detail:', error.response || error);
    message.error(error.response?.data?.error || '获取站点监控详情失败');
  }
};

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-';
};

onMounted(() => {
  console.log('Component mounted, route params:', route.params);
  if (route.params.id) {
    fetchWebsiteDetail();
  }
});
</script>
