<template>
  <a-layout-sider v-model:collapsed="collapsed" collapsible theme="light">
    <div class="logo" @click="JumpToHome">
      <!-- <img src="@/assets/svg/点睛.svg" alt="Logo" class="logo-img" /> -->
      <img v-if="collapsed" src="@/assets/svg/logo.svg" alt="Logo" class="logo-img" />
      <img v-else src="@/assets/svg/turelay.svg" alt="Logo" class="logo-img" />
      <!-- <span v-if="!collapsed" class="logo-text">TuRelay</span> -->
    </div>
    <a-menu
      :selectedKeys="selectedKeys"
      :openKeys="openKeys"
      theme="light"
      mode="inline"
      @openChange="handleOpenChange"
      @click="handleClick"
    >
      <a-menu-item key="/dashboard">
        <router-link to="/dashboard">
          <IconFont type="icon-shouye1" :style="{ fontSize: '16px' }" />
          <span>数据概览</span>
        </router-link>
      </a-menu-item>
      <a-sub-menu key="/user-management">
        <template #title>
          <IconFont type="icon-yonghuguanli" :style="{ fontSize: '16px' }" />
          <span>用户管理</span>
        </template>
        <a-menu-item key="/user-management/user-list">
          <router-link to="/user-management/user-list">用户列表</router-link>
        </a-menu-item>
        <a-menu-item key="/user-management/user-groups">
          <router-link to="/user-management/user-groups">
            <span class="developing-feature">用户组</span>
          </router-link>
        </a-menu-item>
        <a-menu-item key="/user-management/lock-record">
          <router-link to="/user-management/lock-record">锁定记录</router-link>
        </a-menu-item>
        <a-menu-item key="/user-management/credentials">
          <router-link to="/user-management/credentials">凭据管理</router-link>
        </a-menu-item>
      </a-sub-menu>
      <a-sub-menu key="/asset-management">
        <template #title>
          <IconFont type="icon-shebeizichanguanli" :style="{ fontSize: '16px' }" />
          <span>资产管理</span>
        </template>
        <a-menu-item key="/asset-management/hosts">
          <router-link to="/asset-management/hosts">主机列表</router-link>
        </a-menu-item>
        <a-menu-item key="/asset-management/databases">
          <router-link to="/asset-management/databases">
            <span class="developing-feature">数据库</span>
          </router-link>
        </a-menu-item>
        <a-menu-item key="/asset-management/websites">
          <router-link to="/asset-management/websites">站点监控</router-link>
        </a-menu-item>
      </a-sub-menu>
      <a-menu-item key="/web-terminal">
        <a :href="webTerminalUrl" target="_blank">
          <IconFont type="icon-terminal-fill" :style="{ fontSize: '16px' }" />
          <span>web终端</span>
        </a>
      </a-menu-item>
      <a-menu-item key="/ci-cd-system">
        <router-link to="/ci-cd-system">
          <IconFont type="icon-icon_CICD" :style="{ fontSize: '16px' }" />
          <span class="developing-feature">CI/CD系统</span>
        </router-link>
      </a-menu-item>
      <a-sub-menu key="/alert-management">
        <template #title>
          <IconFont type="icon-jinggao" :style="{ fontSize: '16px' }" />
          <span>报警管理</span>
        </template>
        <a-menu-item key="/alert-management/alert-contacts">
          <router-link to="/alert-management/alert-contacts">告警联系人</router-link>
        </a-menu-item>
        <a-menu-item key="/alert-management/alert-rules">
          <router-link to="/alert-management/alert-rules">
            <span class="developing-feature">报警规则</span>
          </router-link>
        </a-menu-item>
        <a-menu-item key="alert-managemanet/command-alert">
          <router-link to="/alert-management/command-alert">命令告警</router-link>
        </a-menu-item>
      </a-sub-menu>
      <a-sub-menu key="/audit-management">
        <template #title>
          <IconFont type="icon-shenjizuoyeguanli" :style="{ fontSize: '16px' }" />
          <span>审计管理</span>
        </template>
        <a-menu-item key="/audit-management/command-records">
          <router-link to="/audit-management/command-records">命令记录</router-link>
        </a-menu-item>
      </a-sub-menu>
      <a-sub-menu key="/logs-management">
        <template #title>
          <IconFont type="icon-rizhiguanli1" :style="{ fontSize: '16px' }" />
          <span>日志管理</span>
        </template>
        <a-menu-item key="/logs-management/login-logs">
          <router-link to="/logs-management/login-logs">登录日志</router-link>
        </a-menu-item>
        <a-menu-item key="/logs-management/operation-logs">
          <router-link to="/logs-management/operation-logs">操作日志</router-link>
        </a-menu-item>
        <a-menu-item key="/logs-management/alert-history">
          <router-link to="/logs-management/alert-history">告警历史</router-link>
        </a-menu-item>
      </a-sub-menu>
      <a-sub-menu key="/settings">
        <template #title>
          <IconFont type="icon-xitongshezhi2" :style="{ fontSize: '16px' }" />
          <span>系统设置</span>
        </template>
        <a-menu-item key="/settings/auth-settings">
          <router-link to="/settings/auth-settings">
            <span class="developing-feature">认证设置</span>
          </router-link>
        </a-menu-item>
        <a-menu-item key="/settings/safe-settings">
          <router-link to="/settings/safe-settings">安全设置</router-link>
        </a-menu-item>
        <a-menu-item key="/settings/about">
          <router-link to="/settings/about">关于</router-link>
        </a-menu-item>
      </a-sub-menu>
    </a-menu>
  </a-layout-sider>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  UserOutlined,
  DesktopOutlined,
  FileOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons-vue';
import IconFont from '@/icons';  // 引入 IconFont 组件

const collapsed = ref(false);
const selectedKeys = ref([]);
const openKeys = ref([]);
const route = useRoute();
const router = useRouter();

const webTerminalUrl = computed(() => {
  return `${window.location.origin}${router.resolve('/web-terminal').href}`;
});

const JumpToHome = () => {
  router.push('/dashboard');
}

const updateMenuState = () => {
  // 更新选中的菜单项
  selectedKeys.value = [route.path];

  // 更新展开的菜单项
  const paths = route.path.split('/').filter(Boolean);
  openKeys.value = paths.map((_, index) => '/' + paths.slice(0, index + 1).join('/'));
};

watch(route, updateMenuState, { immediate: true });

const handleOpenChange = (keys) => {
  openKeys.value = keys;
  localStorage.setItem('openKeys', JSON.stringify(keys));
};

const handleClick = (e) => {
  selectedKeys.value = [e.key];
  localStorage.setItem('selectedKeys', JSON.stringify([e.key]));
};

onMounted(() => {
  updateMenuState();

  // 将初始状态保存到 localStorage
  localStorage.setItem('selectedKeys', JSON.stringify(selectedKeys.value));
  localStorage.setItem('openKeys', JSON.stringify(openKeys.value));
});
</script>


<style scoped>
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  margin: 12px;
  background: rgba(255, 255, 255, 0.3);
  /* 点击 */
  cursor: pointer;
}

.logo-img {
  height: 28px;
  /* margin-right: 6px; */
}

.logo-text {
  transition: opacity 0.3s ease;
}

.developing-feature {
  text-decoration: line-through 1.4px;
  color: #00000040;
}

.developing-feature:hover {
  color: #000000;
}

.menu-item-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-icon {
  font-size: 14px;
  color: #00000040;
}

.info-icon:hover {
  color: #1890ff;
}

/* 添加自定义图标样式 */
:deep(.custom-icon) {
  font-size: 16px; /* 设置你想要的大小 */
}

/* 如果要统一设置所有 IconFont 的大小 */
:deep(.anticon) {
  font-size: 16px;
}
</style>
