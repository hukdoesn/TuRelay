<template>
  <div class="about-container">
    <!-- 项目介绍部分重新设计 -->
    <div class="project-intro">
      <!-- Logo和版本信息区域 -->
      <div class="brand-section">
        <div class="brand-info">
          <h1 class="brand-title">Tu Relay</h1>
          <div class="brand-subtitle">翻斗花园有棵树，我叫图图你记住。</div>
        </div>
        <div class="version-badges">
          <div class="version-badge">
            <span class="badge-label">当前版本</span>
            <span class="badge-value">1.0.0</span>
          </div>
          <div class="version-badge">
            <span class="badge-label">更新时间</span>
            <span class="badge-value">{{ formatDate(latestUpdate) }}</span>
          </div>
        </div>
      </div>

      <!-- 项目描述 -->
      <div class="project-description">
        <p class="description-text">
          TuRelay 是一款专注于简化运维工作流程的现代化运维堡垒机平台。通过直观的界面设计和强大的功能集成，
          为俺图图提供高效、安全、可靠的一站式解决方案。
          <!-- 翻斗花园有棵树，我叫图图你记住。 -->
        </p>
        <div class="feature-tags">
          <a-tag color="cyan">简单高效</a-tag>
          <a-tag color="blue">安全可靠</a-tag>
          <a-tag color="geekblue">功能丰富</a-tag>
          <a-tag color="purple">持续更新</a-tag>
        </div>
      </div>

      <!-- 社交链接部分保持不变 -->
      <div class="social-links">
        <a href="https://ext4.cn" target="_blank" class="badge-link">
          <img alt="Blog" src="https://img.shields.io/badge/博客-1890ff?style=flat-square&logo=Blogger&logoColor=white" />
        </a>
        <a href="https://github.com/hukdoesn" target="_blank" class="badge-link">
          <img alt="GitHub" src="https://img.shields.io/badge/GitHub-2a3947?style=flat-square&logo=GitHub&logoColor=white" />
        </a>
        <a href="https://www.ext4.cn" target="_blank" class="badge-link">
          <img alt="Documentation" src="https://img.shields.io/badge/官网-36cfc9?style=flat-square&logo=ReadtheDocs&logoColor=white" />
        </a>
        <a href="https://gitee.com/your-gitee" target="_blank" class="badge-link">
          <img alt="Gitee" src="https://img.shields.io/badge/Gitee-28404e?style=flat-square&logo=Gitee&logoColor=white" />
        </a>
      </div>
    </div>

    <!-- 更新日志 -->
    <div class="update-section">
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
</template>

<script setup>
import { ref, computed } from 'vue';
import dayjs from 'dayjs';
import {
  BugOutlined,
  RocketOutlined,
  ToolOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons-vue';

const latestUpdate = ref('2024-11-12');
const timelineMode = ref('all');

// 更新记录
const updates = ref([
{
    version: 'v1.0.0',
    date: '2024-11-12',
    type: 'feature',
    title: '新增功能',
    details: [
      '主机管理详情页面',
      '用户列表详情页面',
      '站点管理详情页面',
      '更新日志时间轴页面',
    ]
  },
  {
    version: 'v1.0.0',
    date: '2024-11-12',
    type: 'bugfix',
    title: 'Bug修复更新',
    details: [
      '修复锁定记录last_attemp_time字段空值显示错误',
    ]
  },
  {
    version: 'v1.0.0',
    date: '2024-11-12',
    type: 'optimization',
    title: '性能优化',
    details: [
      '优化数据库查询性能',
      '改进前端组件加载速度',
      '优化WebSocket连接管理'
    ]
  },
  {
    version: 'v1.0.2',
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
    version: 'v1.0.1',
    date: '2024-03-17',
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
    date: '2024-03-16',
    type: 'feature',
    title: '首个正式版本发布',
    details: [
      '完整的用户认证和权限管理系统',
      '主机资产管理功能',
      '站点监控功能',
      'WebTerminal 终端支持',
      '告警系统集成'
    ]
  }
]);

// 按类型筛选更新记录
const filteredUpdates = computed(() => {
  if (timelineMode.value === 'all') {
    return sortedUpdates.value;
  }
  return sortedUpdates.value.filter(update => update.type === timelineMode.value);
});

// 按日期倒序排序
const sortedUpdates = computed(() => {
  return [...updates.value].sort((a, b) => new Date(b.date) - new Date(a.date));
});

const getIcon = (type) => {
  const icons = {
    feature: RocketOutlined,
    security: SafetyCertificateOutlined,
    bugfix: BugOutlined,
    optimization: ToolOutlined
  };
  return icons[type];
};

const getTagColor = (type) => {
  const colors = {
    feature: 'blue',
    security: 'green',
    bugfix: 'red',
    optimization: 'purple'
  };
  return colors[type];
};

const getTypeText = (type) => {
  const texts = {
    feature: '新功能',
    security: '安全更新',
    bugfix: '问题修复',
    optimization: '优化'
  };
  return texts[type];
};

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD');
};
</script>

<style scoped>
.about-container {
  padding: 24px;
  background: #fff;
}

.project-intro {
  margin-bottom: 40px;
  padding: 32px;
  border-radius: 8px;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.03);
}

.brand-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.brand-info {
  flex: 1;
}

.brand-title {
  font-size: 3.2em;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(45deg, #1890ff, #36cfc9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -1px;
}

.brand-subtitle {
  font-size: 1.2em;
  color: #8c8c8c;
  margin-top: 8px;
  letter-spacing: 1px;
}

.version-badges {
  display: flex;
  gap: 16px;
  padding-top: 8px;
}

.version-badge {
  background: rgba(24, 144, 255, 0.1);
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
}

.badge-label {
  font-size: 0.85em;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.badge-value {
  font-size: 1.1em;
  color: #1890ff;
  font-weight: 500;
}

.project-description {
  margin-bottom: 32px;
}

.description-text {
  font-size: 1.1em;
  line-height: 1.8;
  color: #595959;
  margin-bottom: 20px;
  max-width: 900px;
}

.feature-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.feature-tags :deep(.ant-tag) {
  padding: 4px 12px;
  font-size: 0.9em;
  border: none;
  border-radius: 4px;
}

.social-links {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
  align-items: center;
}

.badge-link {
  transition: all 0.3s ease;
  text-decoration: none;
  position: relative;
}

.badge-link:hover {
  transform: translateY(-2px);
}

.badge-link img {
  height: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.badge-link:hover img {
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}

.update-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .brand-section {
    flex-direction: column;
    gap: 24px;
  }

  .version-badges {
    width: 100%;
    justify-content: flex-start;
  }

  .brand-title {
    font-size: 2.5em;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .intro-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>