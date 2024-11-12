<template>
  <a-descriptions v-if="userDetail" title="用户详情" :column="1" :labelStyle="{ color: 'rgba(0, 0, 0, 0.45)' }">
    <a-descriptions-item label="用户名">{{ userDetail.username }}</a-descriptions-item>
    <a-descriptions-item label="姓名">{{ userDetail.name }}</a-descriptions-item>
    <a-descriptions-item label="角色">{{ userDetail.role }}</a-descriptions-item>
    <a-descriptions-item label="权限">{{ userDetail.permissions[0].name }}</a-descriptions-item>
    <a-descriptions-item label="手机号">{{ userDetail.mobile }}</a-descriptions-item>
    <a-descriptions-item label="邮箱">{{ userDetail.email }}</a-descriptions-item>
    <a-descriptions-item label="状态">{{ userDetail.status ? '锁定' : '启用' }}</a-descriptions-item>
    <a-descriptions-item label="MFA认证">{{ userDetail.mfa_level === 1 ? '开启' : '关闭' }}</a-descriptions-item>
    <a-descriptions-item label="创建时间">{{ formatDate(userDetail.create_time) }}</a-descriptions-item>
    <a-descriptions-item label="登陆时间">{{ formatDate(userDetail.last_login) }}</a-descriptions-item>
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
const userDetail = ref(null);

const fetchUserDetail = async () => {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get(`/api/users/${route.params.username}/detail/`, {
      headers: {
        'Authorization': token
      }
    });
    userDetail.value = response.data;
  } catch (error) {
    message.error('获取用户详情失败');
    console.error('Error fetching user detail:', error);
  }
};

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '';
};

onMounted(() => {
  fetchUserDetail();
});
</script>
