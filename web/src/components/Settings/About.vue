<template>
  <div class="page-container">
    <div class="about-container">
      <!-- 个人资料卡片 -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-wrapper">
            <img class="avatar" src="@/assets/img/me.png" alt="头像" />
            <div class="avatar-decoration">
              <span class="emoji">✨</span>
              <span class="emoji">🎨</span>
            </div>
          </div>
          <div class="profile-info">
            <div class="name-wrapper">
              <h1 class="name">胡图图不涂涂</h1>
              <span class="emoji-tag">🎯</span>
            </div>
            <p class="bio">生活不易，猫猫叹气 <span class="emoji">✨</span></p>
            <div class="social-links">
              <a href="https://github.com/hukdoesn/TuRelay" target="_blank" class="social-link github">
                <img src="@/assets/svg/github.svg" alt="GitHub" class="icon" />
                <span class="social-text">开源项目</span>
              </a>
              <a href="https://ext4.cn/" class="social-link blog">
                <img src="@/assets/svg/blog.svg" alt="Blog" class="icon" />
                <span class="social-text">技术博客</span>
              </a>
              <div class="social-link wechat" @click="toggleQR">
                <img src="@/assets/svg/wechat.svg" alt="WeChat" class="icon" />
                <span class="social-text">一起交流</span>
              </div>
              <div class="social-link donate" @click="toggleDonate">
                <img src="@/assets/svg/donate.svg" alt="打赏" class="icon" />
                <span class="social-text">请我喝咖啡</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 更新日志时间轴 -->
      <div class="timeline-section">
        <div class="section-header">
          <div class="header-left">
            <h2>更新日志</h2>
            <span class="update-count">共 {{ updates.length }} 个版本</span>
          </div>
          <a-radio-group v-model:value="timelineMode" button-style="solid" size="small">
            <a-radio-button value="all">全部</a-radio-button>
            <a-radio-button value="feature">功能</a-radio-button>
            <a-radio-button value="security">安全</a-radio-button>
            <a-radio-button value="bugfix">修复</a-radio-button>
            <a-radio-button value="optimization">优化</a-radio-button>
          </a-radio-group>
        </div>

        <div class="timeline-wrapper">
          <a-timeline>
            <a-timeline-item v-for="(item, index) in filteredUpdates" :key="index">
              <template #dot>
                <div :class="['custom-dot', item.type]">
                  <component :is="getIcon(item.type)" />
                </div>
              </template>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="version">{{ item.version }}</span>
                  <span class="date">{{ formatDate(item.date) }}</span>
                  <a-tag :color="getTagColor(item.type)">{{ getTypeText(item.type) }}</a-tag>
                </div>
                <div class="timeline-title">{{ item.title }}</div>
                <div class="timeline-description">
                  <ul>
                    <li v-for="(detail, dIndex) in item.details" :key="dIndex">{{ detail }}</li>
                  </ul>
                </div>
              </div>
            </a-timeline-item>
          </a-timeline>
        </div>
      </div>
    </div>

    <!-- 微信二维码弹窗 -->
    <div v-if="showQR" class="modal" @click.self="toggleQR">
      <div class="modal-container">
        <img :src="wechatQR" alt="微信二维码" />
        <p class="modal-tip">扫码加我微信 <span class="emoji">👻</span></p>
      </div>
    </div>

    <!-- 打赏弹窗 -->
    <div v-if="showDonate" class="modal" @click.self="toggleDonate">
      <div class="modal-container donate-container">
        <div class="donate-header">
          <h3>请我喝杯咖啡 <span class="emoji">☕️</span></h3>
          <p class="donate-desc">谢谢你的支持哦 <span class="emoji"></span></p>
        </div>
        <div class="donate-types">
          <div 
            class="donate-type" 
            :class="{ active: donateType === 'wechat' }"
            @click="setDonateType('wechat')"
          >
            <img src="@/assets/svg/wechat.svg" alt="微信支付" class="donate-icon" />
            <span>微信支付</span>
          </div>
          <div 
            class="donate-type"
            :class="{ active: donateType === 'alipay' }"
            @click="setDonateType('alipay')"
          >
            <img src="@/assets/svg/alipay.svg" alt="支付宝" class="donate-icon" />
            <span>支付宝</span>
          </div>
        </div>
        <div class="donate-qr">
          <img 
            :src="donateType === 'wechat' ? '/src/assets/img/wechat-pay.png' : '/src/assets/img/alipay-pay.png'"
            :alt="donateType === 'wechat' ? '微信支付' : '支付宝支付'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import dayjs from 'dayjs'
import {
  BugOutlined,
  RocketOutlined,
  ToolOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons-vue'

const showQR = ref(false)
const showDonate = ref(false)
const wechatQR = '/src/assets/img/wechat.png'
const donateType = ref('wechat')
const timelineMode = ref('all')

// 更新记录数据
const updates = ref([
  {
    version: 'v1.0.0',
    date: '2024-03-20',
    type: 'feature',
    title: '新增功能',
    details: [
      '安全设置页面',
      'MFA多因素全局控制功能',
      'IP登陆限制：IP白名单、IP黑名单',
      '开启水印功能',
    ]
  },
  {
    version: 'v1.0.0',
    date: '2024-03-19',
    type: 'security',
    title: '安全性更新',
    details: [
      '增强密码策略',
      '添加双因素认证支持',
      '改进会话管理'
    ]
  },
  {
    version: 'v1.0.0',
    date: '2024-03-18',
    type: 'bugfix',
    title: 'Bug修复更新',
    details: [
      '修复文件上传问题',
      '解决WebTerminal连接稳定性问题',
      '修复部分UI显示异常'
    ]
  },
  {
    version: 'v1.0.0',
    date: '2024-03-17',
    type: 'optimization',
    title: '性能优化',
    details: [
      '优化数据库查询性能',
      '改进前端组件加载速度',
      '优化WebSocket连接管理'
    ]
  }
])

// 按类型筛选更新记录
const filteredUpdates = computed(() => {
  if (timelineMode.value === 'all') {
    return sortedUpdates.value
  }
  return sortedUpdates.value.filter(update => update.type === timelineMode.value)
})

// 按日期倒序排序
const sortedUpdates = computed(() => {
  return [...updates.value].sort((a, b) => new Date(b.date) - new Date(a.date))
})

const getIcon = (type) => {
  const icons = {
    feature: RocketOutlined,
    security: SafetyCertificateOutlined,
    bugfix: BugOutlined,
    optimization: ToolOutlined
  }
  return icons[type]
}

const getTagColor = (type) => {
  const colors = {
    feature: 'rgba(24,144,255,0.8)',
    security: 'rgba(82,196,26,0.8)',
    bugfix: 'rgba(255,77,79,0.8)',
    optimization: 'rgba(47,84,235,0.8)'
  }
  return colors[type]
}

const getTypeText = (type) => {
  const texts = {
    feature: '新功能',
    security: '安全更新',
    bugfix: '问题修复',
    optimization: '优化'
  }
  return texts[type]
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const toggleQR = () => {
  showQR.value = !showQR.value
  showDonate.value = false
}

const toggleDonate = () => {
  showDonate.value = !showDonate.value
  showQR.value = false
}

const setDonateType = (type) => {
  donateType.value = type
}
</script>

<style scoped>
.page-container {
  width: 100%;
}

.about-container {
  max-width: auto;
  margin: 0 0 0 30px;  /* 添加左边距 */
  padding: 2rem;
}

.profile-card {
  background: var(--vp-c-bg);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 16px;
  object-fit: cover;
  transition: transform 0.3s;
}

.avatar:hover {
  transform: scale(1.05);
}

.avatar-decoration {
  position: absolute;
  top: -10px;
  right: -10px;
  display: flex;
  gap: 4px;
}

.profile-info {
  text-align: left;
}

.name-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.name {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
  color: var(--vp-c-text-1);
}

.emoji-tag {
  font-size: 1.2rem;
}

.bio {
  font-size: 1rem;
  color: var(--vp-c-text-2);
  margin: 0.5rem 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.emoji {
  font-size: 1.1em;
  display: inline-block;
  vertical-align: middle;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  display: flex;
  align-items: center;
  color: var(--vp-c-text-2);
  transition: all 0.3s;
  cursor: pointer;
  padding: 0.5rem 0.8rem;
  border-radius: 10px;
  text-decoration: none;
  background: var(--vp-c-bg-soft);
}

.social-link:hover {
  color: var(--vp-c-text-1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: #ebebeb;
}

.icon {
  width: 18px;
  height: 18px;
  margin-right: 0.4rem;
}

.social-text {
  font-size: 0.9rem;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background: #ffffff;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.modal-container img {
  max-width: 300px;
  height: auto;
  display: block;
  border-radius: 8px;
}

.modal-tip {
  text-align: center;
  margin: 1rem 0 0;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.donate-container {
  width: 100%;
  max-width: 400px;
}

.donate-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.donate-header h3 {
  margin: 0;
  color: var(--vp-c-text-1);
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.donate-desc {
  margin: 0.5rem 0 0;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.donate-types {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.donate-type {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  background: var(--vp-c-bg-soft);
  transition: all 0.3s;
}

.donate-type:hover {
  transform: translateY(-2px);
  background-color: #f5f5f5;
}

.donate-type.active {
  background: #f0f0f0;
  border: 1px solid var(--vp-c-text-2);
}

.donate-icon {
  width: 18px;
  height: 18px;
  margin-right: 0.5rem;
}

.donate-qr {
  background: var(--vp-c-bg-soft);
  padding: 1rem;
  border-radius: 12px;
}

.donate-qr img {
  max-width: 280px;
  margin: 0 auto;
  border-radius: 8px;
}

.timeline-section {
  background: var(--vp-c-bg);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  color: #333;
  font-size: 1.5em;
}

.update-count {
  color: #888;
  font-size: 0.9em;
}

.timeline-wrapper {
  padding-left: 24px;
}

.timeline-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  margin-left: 12px;
  margin-bottom: 16px;
  max-width: 800px;
  border-left: 4px solid transparent;
}

.timeline-content:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.timeline-content.feature:hover { border-left-color: #1890ff; }
.timeline-content.security:hover { border-left-color: #52c41a; }
.timeline-content.bugfix:hover { border-left-color: #ff4d4f; }
.timeline-content.optimization:hover { border-left-color: #2f54eb; }

.timeline-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.version {
  font-weight: bold;
  color: #1890ff;
  font-size: 1.1em;
}

.date {
  color: #888;
}

.timeline-title {
  font-size: 1.1em;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.timeline-description ul {
  margin: 0;
  padding-left: 20px;
}

.timeline-description li {
  color: #666;
  margin-bottom: 4px;
  line-height: 1.5;
}

.custom-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.3s ease;
}

.custom-dot:hover {
  transform: scale(1.1);
}

/* 图标颜色 */
.feature { color: #1890ff; background: #e6f7ff; }
.security { color: #52c41a; background: #f6ffed; }
.bugfix { color: #ff4d4f; background: #fff2f0; }
.optimization { color: #2f54eb; background: #f0f5ff; }

/* 自定义时间轴样式 */
:deep(.ant-timeline-item-tail) {
  border-left: 2px solid #e8e8e8;
}

:deep(.ant-timeline-item:last-child .ant-timeline-item-tail) {
  display: none;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .timeline-content {
    margin-left: 8px;
    padding: 12px;
  }
  
  .timeline-header {
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  .profile-info {
    text-align: center;
  }
  .name-wrapper {
    justify-content: center;
  }
  .social-links {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>