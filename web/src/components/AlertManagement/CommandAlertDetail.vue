<template>
  <a-descriptions v-if="alertDetail" title="命令告警详情" :column="1" :labelStyle="{ fontWeight: 'bold', color: 'rgba(0, 0, 0, 0.45)' }">
    <a-descriptions-item label="规则名称">{{ alertDetail.name }}</a-descriptions-item>
    <a-descriptions-item label="命令规则">{{ alertDetail.command_rule ? alertDetail.command_rule.join(', ') : '' }}</a-descriptions-item>
    <a-descriptions-item label="关联主机">{{ alertDetail.host_names ? alertDetail.host_names.join(', ') : '' }}</a-descriptions-item>
    <a-descriptions-item label="告警联系人">{{ alertDetail.alert_contact_names ? alertDetail.alert_contact_names.join(', ') : '' }}</a-descriptions-item>
    <a-descriptions-item label="是否告警">{{ alertDetail.is_active !== undefined ? (alertDetail.is_active ? '是' : '否') : '' }}</a-descriptions-item>
    <a-descriptions-item label="创建时间">{{ alertDetail.create_time ? formatDate(alertDetail.create_time) : '' }}</a-descriptions-item>
  </a-descriptions>
  <a-spin v-else />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { message, Spin } from 'ant-design-vue';
import axios from 'axios';
import dayjs from 'dayjs';

const route = useRoute();
const alertDetail = ref(null);

const fetchAlertDetail = async () => {
  try {
    const response = await axios.get(`/api/command_alerts/${route.params.id}/`);
    alertDetail.value = response.data;
  } catch (error) {
    message.error('获取命令告警详情失败');
    console.error('Error fetching command alert detail:', error);
  }
};

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '';
};

onMounted(() => {
  fetchAlertDetail();
});
</script>
