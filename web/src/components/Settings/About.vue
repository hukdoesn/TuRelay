<template>
  <div class="about-container">
    <!-- 项目介绍 -->
    <div class="project-intro">
      <div class="intro-header">
        <h1>TuRelay</h1>
        <div class="version-info">
          <a-tag color="blue">Version 1.0.0</a-tag>
          <a-tag color="green">最后更新: {{ formatDate(latestUpdate) }}</a-tag>
        </div>
      </div>
      <p class="description">
        TuRelay 是一个现代化的运维管理平台，致力于提供简单高效的运维解决方案。
      </p>
      <div class="social-links">
        <a href="https://your-blog-url.com" target="_blank" class="badge-link">
          <img alt="Blog" src="https://img.shields.io/badge/Blog-FF4081?style=for-the-badge&logo=blogger&logoColor=white&labelColor=FF4081" />
        </a>
        <a href="https://github.com/your-github" target="_blank" class="badge-link">
          <img alt="GitHub" src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white&labelColor=181717" />
        </a>
        <a href="https://your-docs-url.com" target="_blank" class="badge-link">
          <img alt="Documentation" src="https://img.shields.io/badge/TuRelay-21BAB5?style=for-the-badge&logo=readthedocs&logoColor=white&labelColor=21BAB5" />
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

const latestUpdate = ref('2024-03-19');
const timelineMode = ref('all');

// 更新记录
const updates = ref([
  {
    version: 'v1.0.3',
    date: '2024-03-19',
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

.intro-header {
  margin-bottom: 24px;
}

.intro-header h1 {
  font-size: 2.8em;
  background: linear-gradient(45deg, #1890ff, #36cfc9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 16px;
}

.description {
  font-size: 1.2em;
  line-height: 1.8;
  color: #4a5568;
  margin-bottom: 32px;
  max-width: 800px;
}

.social-links {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.badge-link {
  transition: all 0.3s ease;
}

.badge-link:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

.badge-link img {
  height: 28px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

@media (max-width: 768px) {
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