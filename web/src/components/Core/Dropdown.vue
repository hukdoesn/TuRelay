<template>
    <a-dropdown>
      <a href="javascript:;" class="ant-dropdown-link" style="color: inherit;" @click.prevent>
        {{ Name }}
        <DownOutlined />
      </a>
      <template #overlay>
        <a-menu>
          <a-menu-item @click="showUserInfo">
            <a href="javascript:;">个人信息</a>
          </a-menu-item>
          <a-menu-item @click="showResetPasswordModal">
            <a href="javascript:;">修改密码</a>
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item class="logout" @click="logout">
            <a href="javascript:;">退出登录</a>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>

    <!-- 个人信息模态框 -->
    <a-modal
      v-model:open="userInfoModalVisible"
      title="个人信息"
      :footer="null"
      @cancel="closeUserInfoModal"
      width="400px"
    >
      <div class="user-info-container">
        <div class="user-avatar">
          <span class="avatar-text">{{ Name.charAt(0).toUpperCase() }}</span>
        </div>
        <div class="user-name">{{ userInfo.name }}</div>
        <div class="user-role">{{ userInfo.role }}</div>
        
        <div class="info-divider"></div>
        
        <div class="info-section">
          <div class="info-item">
            <div class="info-label">用户名</div>
            <div class="info-value">{{ userInfo.username }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">邮箱</div>
            <div class="info-value">{{ userInfo.email }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">手机</div>
            <div class="info-value">{{ userInfo.mobile }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">状态</div>
            <div class="info-value">
              <a-badge :status="userInfo.status ? 'error' : 'success'" :text="userInfo.status ? '锁定' : '启用'" />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">MFA认证</div>
            <div class="info-value">{{ userInfo.mfa_level === 1 ? '已开启' : '未开启' }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">最后登录</div>
            <div class="info-value">{{ userInfo.last_login ? dayjs(userInfo.last_login).format('YYYY-MM-DD HH:mm:ss') : '-' }}</div>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- 重置密码模态框 -->
    <a-modal
      v-model:open="resetPasswordModalVisible"
      title="修改密码"
      @ok="handleResetPasswordOk"
      @cancel="handleResetPasswordCancel"
    >
      <a-form :model="resetPasswordForm">
        <a-form-item
          label="新密码"
          name="password"
          :rules="[
            { required: true, message: '请输入新密码' },
            { min: 6, message: '密码长度不能小于6个字符' }
          ]"
        >
          <a-input-password v-model:value="resetPasswordForm.newPassword" placeholder="请输入新密码" />
        </a-form-item>
      </a-form>
    </a-modal>
</template>
  
<script setup>
import { DownOutlined } from '@ant-design/icons-vue';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import dayjs from 'dayjs';
import { message } from 'ant-design-vue';

const router = useRouter();
const Name = ref(localStorage.getItem('name') || 'Tu Relay');

// 用户信息相关
const userInfoModalVisible = ref(false);
const userInfo = ref({});

// 重置密码相关
const resetPasswordModalVisible = ref(false);
const resetPasswordForm = ref({
  newPassword: ''
});

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get('/api/users/current/', {
      headers: {
        'Authorization': token
      }
    });
    userInfo.value = response.data;
  } catch (error) {
    message.error('获取用户信息失败');
  }
};

// 显示用户信息
const showUserInfo = async () => {
  await fetchUserInfo();
  userInfoModalVisible.value = true;
};

// 关闭用户信息模态框
const closeUserInfoModal = () => {
  userInfoModalVisible.value = false;
};

// 显示重置密码模态框
const showResetPasswordModal = () => {
  resetPasswordModalVisible.value = true;
};

// 处理重置密码
const handleResetPasswordOk = async () => {
  try {
    if (!resetPasswordForm.value.newPassword) {
      message.error('请输入新密码');
      return;
    }
    if (resetPasswordForm.value.newPassword.length < 6) {
      message.error('密码长度不能小于6个字符');
      return;
    }

    const token = localStorage.getItem('accessToken');
    const response = await axios.post('/api/users/current/reset_password/', {
      new_password: resetPasswordForm.value.newPassword
    }, {
      headers: {
        'Authorization': token
      }
    });

    if (response.data.is_self_update) {
      message.success('密码修改成功，请重新登录');
      resetPasswordModalVisible.value = false;
      localStorage.clear();
      router.push('/login');
    } else {
      message.success('密码修改成功');
      resetPasswordModalVisible.value = false;
    }
  } catch (error) {
    message.error('密码修改失败');
  }
};

// 处理重置密码取消
const handleResetPasswordCancel = () => {
  resetPasswordModalVisible.value = false;
  resetPasswordForm.value.newPassword = '';
};

// 登出
const logout = async () => {
    try {
        await axios.post('/api/logout/');
        localStorage.clear();
        router.push('/login');
    } catch (error) {
        console.error('登出失败:', error);
        localStorage.clear();
        router.push('/login');
    }
};

onMounted(() => {
  Name.value = localStorage.getItem('name') || 'Tu Relay';
});
</script>

<style scoped>
.logout .ant-dropdown-menu-title-content {
  color: black;
}

.logout .ant-dropdown-menu-title-content:hover {
  color: red;
}

.icon {
  margin-right: 8px;
}

/* 个人信息样式 */
.user-info-container {
  padding: 20px;
  text-align: center;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #1890ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.avatar-text {
  color: white;
  font-size: 32px;
  font-weight: bold;
}

.user-name {
  font-size: 20px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 4px;
}

.user-role {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 20px;
}

.info-divider {
  height: 1px;
  background-color: #f0f0f0;
  margin: 16px 0;
}

.info-section {
  text-align: left;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-label {
  width: 80px;
  color: rgba(0, 0, 0, 0.45);
  flex-shrink: 0;
}

.info-value {
  color: rgba(0, 0, 0, 0.85);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 适配暗色主题的样式 */
:deep(.ant-modal-content) {
  border-radius: 8px;
}

:deep(.ant-modal-header) {
  border-radius: 8px 8px 0 0;
}

:deep(.ant-modal-body) {
  padding: 0;
}
</style>