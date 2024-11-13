<template>
  <div class="dashboard-container">
    <!-- 数据概览卡片 -->
    <a-row :gutter="[16, 16]">
      <a-col :span="6">
        <a-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-card-content">
            <div class="stat-icon">
              <img width="40" height="40" src="https://img.icons8.com/plasticine/100/monitor.png" alt="monitor"/>
            </div>
            <div class="stat-info">
              <div class="stat-title">主机数量</div>
              <div class="stat-value">{{ statistics.hostCount }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-card-content">
            <div class="stat-icon">
              <img width="40" height="40" src="https://img.icons8.com/plasticine/100/name.png" alt="name"/>
            </div>
            <div class="stat-info">
              <div class="stat-title">用户数量</div>
              <div class="stat-value">{{ statistics.userCount }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-card-content">
            <div class="stat-icon">
              <img width="40" height="40" src="https://img.icons8.com/plasticine/100/system-report.png" alt="system-report"/>
            </div>
            <div class="stat-info">
              <div class="stat-title">告警数量</div>
              <div class="stat-value">{{ statistics.alertCount }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-card-content">
            <div class="stat-icon">
              <img width="40" height="40" src="https://img.icons8.com/plasticine/100/lock.png" alt="lock"/>
            </div>
            <div class="stat-info">
              <div class="stat-title">锁定用户</div>
              <div class="stat-value">{{ statistics.lockedUserCount }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 图表区域 -->
    <a-row :gutter="[16, 16]" style="margin-top: 16px">
      <!-- 主机类型分布饼图 -->
      <a-col :span="12">
        <a-card title="主机类型分布">
          <div ref="hostChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
      
      <!-- 登录统计折线图 -->
      <a-col :span="12">
        <a-card title="用户登录统计">
          <template #extra>
            <a-radio-group v-model:value="dateRange" @change="handleDateRangeChange">
              <a-radio-button value="7">近7天</a-radio-button>
              <a-radio-button value="14">近14天</a-radio-button>
              <a-radio-button value="30">近30天</a-radio-button>
            </a-radio-group>
          </template>
          <div ref="loginChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 详细统计信息 -->
    <a-row :gutter="[16, 16]" style="margin-top: 16px">
      <a-col :span="12">
        <a-card title="系统概况">
          <a-descriptions :column="1">
            <a-descriptions-item label="在线会话">
              {{ statistics.onlineSessionCount }}
            </a-descriptions-item>
            <a-descriptions-item label="失败登录">
              {{ statistics.failedLoginCount }}
            </a-descriptions-item>
            <a-descriptions-item label="资产数量">
              {{ statistics.assetCount }}
            </a-descriptions-item>
            <a-descriptions-item label="网站监控">
              {{ statistics.websiteCount }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-col>
      
      <!-- 最近登录记录 -->
      <a-col :span="12">
        <a-card title="最近登录记录">
          <a-table
            :columns="loginColumns"
            :data-source="recentLogins"
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

// 最近登录记录表格列定义
const loginColumns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '登录时间',
    dataIndex: 'login_time',
    key: 'login_time',
  },
  {
    title: 'IP地址',
    dataIndex: 'client_ip',
    key: 'client_ip',
  },
]

// 最近登录数据
const recentLogins = ref([])

// 添加日期范围选择的响应式变量
const dateRange = ref('7')

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
      right: 10,
      top: 'center'
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
          formatter: '{b}: {c}台 ({d}%)'
        },
        labelLine: {
          show: true,
          length: 15,
          length2: 20,
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
          result += `${param.marker} ${param.seriesName}: ${param.value}次<br/>`;
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
    const loginChart = echarts.getInstanceByDom(loginChartRef.value)
    hostChart?.resize()
    loginChart?.resize()
  })
})
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.stat-card {
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: white;
  border: 1px solid #f0f0f0;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stat-card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 56px;
  height: 56px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-icon img {
  width: 40px;
  height: 40px;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-icon img {
  transform: scale(1.1);
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  line-height: 1.2;
}

/* 添加响应式样式 */
@media screen and (max-width: 1400px) {
  .stat-icon {
    width: 48px;
    height: 48px;
  }
  
  .stat-icon img {
    width: 32px;
    height: 32px;
  }
}

@media screen and (max-width: 1200px) {
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  
  .stat-icon img {
    width: 28px;
    height: 28px;
  }
}
</style>