<template>
  <div class="safe-settings-container">
    <a-card title="安全设置" :bordered="false">
      <!-- MFA 设置 -->
      <a-form :model="formState" layout="vertical">
        <a-form-item label="MFA 多因素认证">
          <a-radio-group v-model:value="formState.mfaEnabled">
            <a-radio value="disabled">未启用</a-radio>
            <a-radio value="enabled">全局启用 MFA</a-radio>
            <a-radio value="partial" v-if="hasDisabledMfaUsers">部分用户</a-radio>
          </a-radio-group>
          <div class="form-item-desc">
            <template v-if="formState.mfaEnabled === 'enabled'">
              启用后，所有用户登录时都需要进行 MFA 验证
            </template>
            <template v-if="formState.mfaEnabled === 'partial'">
              <a-alert
                type="warning"
                show-icon
              >
                <template #message>
                  <div class="mfa-users-list">
                    <span class="mfa-users-title">未启用MFA认证的用户：</span>
                    <span 
                      v-for="(item, index) in disabledMfaUsers" 
                      :key="item.username"
                      class="mfa-user-item"
                    >
                      {{ item.name }}（{{ item.username }}）
                      <span v-if="index < disabledMfaUsers.length - 1" class="separator">,</span>
                    </span>
                  </div>
                </template>
              </a-alert>
            </template>
          </div>
        </a-form-item>

        <!-- IP 登录限制 -->
        <a-divider />
        <h3>IP 登录限制</h3>
        
        <!-- IP 白名单 -->
        <a-form-item label="IP 白名单">
          <a-textarea
            v-model:value="formState.ipWhitelist"
            :rows="4"
            placeholder="请输入允许登录的IP地址，多个IP请用逗号分隔。例如: 192.168.10.1, 192.168.1.0/24"
          />
          <div class="form-item-desc">
            <a-alert
              type="info"
              :message="'优先级最高：设置白名单后，只有白名单内的IP可以访问，会忽略黑名单设置。' + 
                        '支持格式：单个IP(192.168.1.1)、网段(192.168.1.0/24)、全部IP(*)'"
              show-icon
            />
          </div>
        </a-form-item>

        <!-- IP 黑名单 -->
        <a-form-item label="IP 黑名单">
          <a-textarea
            v-model:value="formState.ipBlacklist"
            :rows="4"
            placeholder="请输入禁止登录的IP地址，多个IP请用逗号分隔。例如: 192.168.10.1, 192.168.1.0/24"
          />
          <div class="form-item-desc">
            <a-alert
              type="warning"
              :message="'仅在未设置白名单时生效：黑名单中的IP将被禁止登录系统。' + 
                        '支持格式：单个IP(192.168.1.1)、网段(192.168.1.0/24)、全部IP(*)'"
              show-icon
            />
          </div>
        </a-form-item>

        <!-- 水印设置 -->
        <a-divider />
        <a-form-item label="页面水印">
          <a-switch
            v-model:checked="formState.watermarkEnabled"
            checked-children="开启"
            un-checked-children="关闭"
            @change="handleWatermarkChange"
          />
          <div class="form-item-desc" v-if="formState.watermarkEnabled">
            开启后，所有用户页面将显示包含用户名称和时间的水印
          </div>
        </a-form-item>

        <!-- 提交按钮 -->
        <a-form-item>
          <a-button type="primary" @click="handleSubmit">
            保存设置
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';

const formState = reactive({
  mfaEnabled: 'disabled',
  ipWhitelist: '',
  ipBlacklist: '',
  watermarkEnabled: false,
});

const disabledMfaUsers = ref([]);
const hasDisabledMfaUsers = ref(false);

// 获取系统设置
const getSystemSettings = async () => {
  try {
    const response = await axios.get('/api/settings/system/');
    formState.watermarkEnabled = response.data.watermark_enabled;
    formState.ipWhitelist = response.data.ip_whitelist || '';
    formState.ipBlacklist = response.data.ip_blacklist || '';
    formState.mfaEnabled = response.data.mfa_enabled;
    
    // 更新未启用MFA的用户列表
    disabledMfaUsers.value = response.data.disabled_mfa_users || [];
    hasDisabledMfaUsers.value = disabledMfaUsers.value.length > 0;
    
    localStorage.setItem('watermarkEnabled', response.data.watermark_enabled);
    window.dispatchEvent(new Event('updateWatermark'));
  } catch (error) {
    message.error('获取系统设置失败');
  }
};

// IP 格式验证函数
const validateIpList = (ipList) => {
  if (!ipList) return true;
  const ips = ipList.split(',').map(ip => ip.trim());
  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/;
  
  for (const ip of ips) {
    if (ip === '*') continue;
    if (!ipRegex.test(ip)) {
      return false;
    }
    // 验证 IP 地址的每个段是否在 0-255 之间
    if (ip.includes('/')) {
      const [addr, prefix] = ip.split('/');
      if (parseInt(prefix) > 32) return false;
      const parts = addr.split('.');
      if (!parts.every(part => parseInt(part) >= 0 && parseInt(part) <= 255)) {
        return false;
      }
    } else {
      const parts = ip.split('.');
      if (!parts.every(part => parseInt(part) >= 0 && parseInt(part) <= 255)) {
        return false;
      }
    }
  }
  return true;
};

// 保存系统设置
const handleSubmit = async () => {
  // 验证 IP 格式
  if (formState.ipWhitelist && !validateIpList(formState.ipWhitelist)) {
    message.error('白名单 IP 格式不正确');
    return;
  }
  if (formState.ipBlacklist && !validateIpList(formState.ipBlacklist)) {
    message.error('黑名单 IP 格式不正确');
    return;
  }

  try {
    await axios.post('/api/settings/system/', {
      watermark_enabled: formState.watermarkEnabled,
      ip_whitelist: formState.ipWhitelist,
      ip_blacklist: formState.ipBlacklist,
      mfa_enabled: formState.mfaEnabled,
    });
    
    localStorage.setItem('watermarkEnabled', formState.watermarkEnabled);
    window.dispatchEvent(new Event('updateWatermark'));
    message.success('设置已保存');
    
    // 重新获取设置以更新用户列表
    await getSystemSettings();
  } catch (error) {
    message.error('保存设置失败');
  }
};

// 初始化
onMounted(() => {
  getSystemSettings();
});

// 监听水印开关变化
const handleWatermarkChange = (checked) => {
  formState.watermarkEnabled = checked;
};
</script>

<style scoped>
/* .safe-settings-container {
  padding: 24px;
  background: #f0f2f5;
} */

.form-item-desc {
  margin-top: 8px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}

:deep(.ant-form-item) {
  margin-bottom: 24px;
}

:deep(.ant-divider) {
  margin: 24px 0;
}

h3 {
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
}

.mfa-users-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.mfa-users-title {
  margin-right: 8px;
}

.mfa-user-item {
  color: #666;
  white-space: nowrap;
}

.separator {
  margin: 0 4px;
}
</style>