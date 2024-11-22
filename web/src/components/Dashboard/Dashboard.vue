<template>
  <div class="dashboard-container">
    <!-- 数据概览卡片 -->
    <a-row :gutter="[16, 16]">
      <a-col :span="6" v-for="(card, index) in statCards" :key="index">
        <div class="stat-item">
          <div class="stat-icon">
            <img :width="28" :height="28" :src="card.icon" :alt="card.title"/>
          </div>
          <div class="stat-info">
            <div class="stat-title">{{ card.title }}</div>
            <div class="stat-value">{{ statistics[card.key] }}</div>
          </div>
        </div>
      </a-col>
    </a-row>

    <!-- 系统概览 -->
    <a-row :gutter="[16, 16]" class="section-margin">
      <a-col :span="6" v-for="(item, key) in systemOverview" :key="key">
        <div class="overview-item">
          <div class="overview-icon">
            <img :width="28" :height="28" :src="item.icon" :alt="item.label"/>
          </div>
          <div class="overview-content">
            <div class="overview-value">{{ statistics[item.key] }}</div>
            <div class="overview-label">{{ item.label }}</div>
          </div>
        </div>
      </a-col>
    </a-row>

    <!-- 图表区域 -->
    <a-row :gutter="[16, 16]" class="section-margin">
      <!-- 主机类型分布 -->
      <a-col :span="6">
        <a-card class="chart-card" :bordered="true" title="主机类型分布">
          <div ref="hostChartRef" style="height: 280px"></div>
        </a-card>
      </a-col>
      
      <!-- 网站连通性占比 -->
      <a-col :span="6">
        <a-card class="chart-card" :bordered="true" title="网站连通性占比">
          <div ref="websiteChartRef" style="height: 280px"></div>
        </a-card>
      </a-col>
      
      <!-- 用户登录统计 -->
      <a-col :span="12">
        <a-card class="chart-card" :bordered="true" title="用户登录统计">
          <template #extra>
            <a-radio-group v-model:value="dateRange" @change="handleDateRangeChange" size="small">
              <a-radio-button value="7">近7天</a-radio-button>
              <a-radio-button value="14">近14天</a-radio-button>
              <a-radio-button value="30">近30天</a-radio-button>
            </a-radio-group>
          </template>
          <div ref="loginChartRef" style="height: 280px"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 最近记录区域 -->
    <a-row :gutter="[16, 16]" class="section-margin">
      <!-- 最近登录记录 -->
      <a-col :span="12">
        <a-card class="info-card" :bordered="true" title="最近登录失败记录">
          <a-table
            :columns="loginColumns"
            :data-source="recentLogins"
            :pagination="false"
            size="small"
          />
        </a-card>
      </a-col>
      
      <!-- 最近告警记录 -->
      <a-col :span="12">
        <a-card class="info-card" :bordered="true" title="最近告警记录">
          <a-table
            :columns="alertColumns"
            :data-source="recentAlerts"
            :pagination="false"
            size="small"
          />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

// 统计数据
const statistics = ref({
  hostCount: 0,
  userCount: 0,
  alertCount: 0,
  lockedUserCount: 0,
  onlineSessionCount: 0,
  failedLoginCount: 0,
  assetCount: 0,
  websiteCount: 0
})

// 图表DOM引用
const hostChartRef = ref(null)
const loginChartRef = ref(null)
const websiteChartRef = ref(null)

// 最近登录记录表格列定义
const loginColumns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: '15%'
  },
  {
    title: 'IP地址',
    dataIndex: 'client_ip',
    key: 'client_ip',
    width: '25%'
  },
  {
    title: '失败原因',
    dataIndex: 'reason',
    key: 'reason',
    width: '25%',
    ellipsis: true  // 文字过长时显示省略号
  },
  {
    title: '时间',
    dataIndex: 'login_time',
    key: 'login_time',
    width: '25%'
  }
]

// 最近登录数据
const recentLogins = ref([])

// 添加日期范围选择的响应式变量
const dateRange = ref('7')

// 统计卡片数据
const statCards = [
  {
    title: '主机数量',
    key: 'hostCount',
    icon: 'https://img.icons8.com/parakeet-line/48/workstation.png'
  },
  {
    title: '用户数量',
    key: 'userCount',
    icon: 'https://img.icons8.com/parakeet-line/48/user-group-man-man.png'
  },
  {
    title: '告警数量',
    key: 'alertCount',
    icon: 'https://img.icons8.com/parakeet-line/48/warning-shield.png'
  },
  {
    title: '锁定用户',
    key: 'lockedUserCount',
    icon: 'https://img.icons8.com/parakeet-line/48/keyhole-shield.png'
  }
]

// 系统概况数据
const systemOverview = [
  { 
    label: '在线会话', 
    key: 'onlineSessionCount',
    icon: 'https://img.icons8.com/parakeet-line/48/speech-bubble.png'
  },
  { 
    label: '失败登录', 
    key: 'failedLoginCount',
    // icon: 'https://img.icons8.com/wired/64/cancel.png'
    icon: 'https://img.icons8.com/parakeet-line/48/cancel.png'
  },
  { 
    label: '网站监控', 
    key: 'websiteCount',
    icon: 'https://img.icons8.com/parakeet-line/48/web-shield.png'
  },
  { 
    label: '资产数量', 
    key: 'assetCount',
    icon: 'https://img.icons8.com/wired/64/database.png'
  },
]

// 初始化主机类型分布图表
const initHostChart = (data) => {
  const chart = echarts.init(hostChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      bottom: '5%'
    },
    series: [
      {
        name: '主机类型',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside',
          formatter: '{c} 台',
          padding: [0, 8]
        },
        labelLine: {
          show: true,
          length: 10,
          length2: 15,
          smooth: true
        },
        data: [
          { value: data.linux || 0, name: 'Linux' },
          { value: data.windows || 0, name: 'Windows' }
        ]
      }
    ]
  }
  chart.setOption(option)
}

// 初始化网站连通性图表
const initWebsiteChart = (data) => {
  const chart = echarts.init(websiteChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      bottom: '5%'
    },
    series: [
      {
        name: '连通性',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside',
          formatter: '{b}: {c}个',
          padding: [0, 8]
        },
        labelLine: {
          show: true,
          length: 10,
          length2: 15,
          smooth: true
        },
        data: [
          { 
            value: data.connected || 0, 
            name: '正常',
            itemStyle: { color: '#52c41a' }
          },
          { 
            value: data.disconnected || 0, 
            name: '异常',
            itemStyle: { color: '#ff4d4f' }
          }
        ]
      }
    ]
  }
  chart.setOption(option)
}

// 修改登录统计图表初始化函数
const initLoginChart = (data) => {
  const chart = echarts.init(loginChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>';  // 显示日期
        // 遍历每个系列的数据
        params.forEach(param => {
          // 使用圆点标记 + 用户名 + 具体数值 + 单位
          result += `${param.marker} ${param.seriesName}: ${param.value} 次<br/>`;
        });
        return result;
      }
    },
    legend: {
      data: data.users,
      top: 'bottom'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates,
      axisLabel: {
        rotate: data.dates.length > 7 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: '登录次数'
    },
    series: data.users.map((user, index) => ({
      name: user,
      type: 'line',
      smooth: true,
      showSymbol: false,
      symbol: 'circle',
      symbolSize: 6,
      emphasis: {
        focus: 'series',
        showSymbol: true
      },
      lineStyle: {
        width: 2.5
      },
      data: data.loginData[user],
      animationDuration: 1000,
      animationEasing: 'cubicInOut',
      animationDelay: (idx) => idx * 100 + index * 200
    })),
    animation: true,
    animationThreshold: 2000,
    animationDuration: 1000,
    animationEasing: 'cubicInOut',
    animationDurationUpdate: 500
  }
  
  // 清除之前的图表实例
  chart.clear()
  // 设置新的配置
  chart.setOption(option)
}

// 修改日期范围变化处理函数，添加加载状态
const handleDateRangeChange = async () => {
  try {
    // 获取图表实例
    const chart = echarts.getInstanceByDom(loginChartRef.value)
    if (chart) {
      // 显示加载动画
      chart.showLoading({
        text: '加载中...',
        color: '#1890ff',
        textColor: '#000',
        maskColor: 'rgba(255, 255, 255, 0.8)',
        zlevel: 0
      })
    }

    const response = await axios.get(`/api/dashboard/login_statistics/${dateRange.value}/`)
    
    // 隐藏加载动画
    chart?.hideLoading()
    // 初始化图表
    initLoginChart(response.data)
  } catch (error) {
    console.error('获取登录统计数据失败:', error)
    // 出错时也要隐藏加载动画
    const chart = echarts.getInstanceByDom(loginChartRef.value)
    chart?.hideLoading()
  }
}

// 修改获取仪表盘数据的函数
const fetchDashboardData = async () => {
  try {
    const [statsResponse, loginStatsResponse] = await Promise.all([
      axios.get('/api/dashboard/statistics/'),
      axios.get(`/api/dashboard/login_statistics/${dateRange.value}/`)
    ])
    
    statistics.value = statsResponse.data.statistics
    initHostChart(statsResponse.data.hostTypes)
    initWebsiteChart(statsResponse.data.websiteStatus)  // 初始化网站连通性图表
    initLoginChart(loginStatsResponse.data)
    recentLogins.value = statsResponse.data.recentLogins
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    // 使用模拟数据用于展示
    statistics.value = {
      hostCount: 25,
      userCount: 12,
      alertCount: 5,
      lockedUserCount: 2,
      onlineSessionCount: 3,
      failedLoginCount: 15,
      assetCount: 30,
      websiteCount: 8
    }
    
    initHostChart({
      linux: 15,
      windows: 8,
      macos: 2,
      others: 0
    })
    
    initLoginChart({
      dates: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      counts: [30, 25, 35, 45, 20, 15, 40]
    })
  }
}

onMounted(() => {
  fetchDashboardData()
  
  // 监听窗口大小变化，重绘图表
  window.addEventListener('resize', () => {
    const hostChart = echarts.getInstanceByDom(hostChartRef.value)
    const websiteChart = echarts.getInstanceByDom(websiteChartRef.value)
    const loginChart = echarts.getInstanceByDom(loginChartRef.value)
    hostChart?.resize()
    websiteChart?.resize()
    loginChart?.resize()
  })
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100%;
  background: white;
}

.section-margin {
  margin-top: 16px;
}

/* 数据概览样式 */
.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 4px;
  transition: all 0.3s;
  border: 1px solid #f0f0f0;
  height: 80px;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  background: white;
  border-radius: 6px;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
}

/* 图表卡片样式 */
.chart-card {
  background: white;
  border-radius: 4px;
  height: 100%;
  transition: all 0.3s;
}

.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.chart-card :deep(.ant-card-head) {
  min-height: 48px;
  padding: 0 16px;
}

.chart-card :deep(.ant-card-body) {
  padding: 16px;
}

.chart-card :deep(.ant-card-head-title) {
  padding: 14px 0;
  font-size: 15px;
  font-weight: 500;
}

/* 系统概览样式 */
.overview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 4px;
  transition: all 0.3s;
  border: 1px solid #f0f0f0;
  height: 80px;
}

.overview-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.overview-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  background: white;
  border-radius: 6px;
}

.overview-content {
  flex: 1;
}

.overview-value {
  font-size: 20px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  line-height: 1;
  margin-bottom: 8px;
}

.overview-label {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.45);
}

/* 表格样式 */
:deep(.ant-table-small) {
  font-size: 13px;
}

:deep(.ant-table-thead > tr > th) {
  background: white;
  padding: 12px 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.65);
}

:deep(.ant-table-tbody > tr > td) {
  padding: 12px 16px;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #fafafa;
}

/* 卡片通用样式 */
:deep(.ant-card) {
  box-shadow: none;
}

:deep(.ant-card-bordered) {
  border: none;
}

/* 响应式调整 */
@media screen and (max-width: 1400px) {
  .stat-value {
    font-size: 16px;
  }
  
  .stat-icon img {
    width: 32px;
    height: 32px;
  }
  
  .overview-value {
    font-size: 18px;
  }
}

@media screen and (max-width: 1200px) {
  .stat-icon img {
    width: 28px;
    height: 28px;
  }
  
  .overview-value {
    font-size: 16px;
  }
}
</style>