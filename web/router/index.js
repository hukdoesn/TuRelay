import { createRouter, createWebHistory } from 'vue-router'
import dayjs from 'dayjs';

import axios from 'axios';
import { message } from 'ant-design-vue';

// 添加请求拦截器，在每个请求头中添加 token
axios.interceptors.request.use(
    config => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers['Authorization'] = token;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 添加响应拦截器，处理 403 错误
axios.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response && error.response.status === 403) {
            // message.error('账号被锁定，请联系管理员');
            localStorage.removeItem('accessToken'); // 清除 token
            router.push('/login'); // 重定向到登录页面
        }
        return Promise.reject(error);
    }
);

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/components/Auth/Login.vue'),
      meta: { requiresAuth: false, breadcrumbName: '登录' }   // 登录页面不需要认证

    },
    {
      path: '/',
      redirect: '/home', // 根路径重定向到/home
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/components/Home.vue'),
      meta: { requiresAuth: true, breadcrumbName: '首页' },    // 主页需要认证
      redirect: '/dashboard', // 默认重定向到数据概览页面
      children: [
        {
          path: '/dashboard',
          name: 'dashboard',
          component: () => import('@/components/Dashboard/Dashboard.vue'),
          meta: { 
            requiresAuth: true ,
            breadcrumbName: '仪表盘',
          },
        },
        { 
          path: '/user-management/user-list', 
          component: () => import('@/components/UserManagement/UserList.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '用户列表' 
          } 
        },
        { 
          path: '/user-management/user-groups', 
          component: () => import('@/components/UserManagement/UserGroups.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '用户组' 
          } 
        },
        { 
          path: '/user-management/login-lock', 
          component: () => import('@/components/UserManagement/LoginLock.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '登录锁定' 
          } 
        },
        { 
          path: '/user-management/credentials', 
          component: () => import('@/components/UserManagement/Credentials.vue'), 
          meta: {
             requiresAuth: true, 
             breadcrumbName: '凭据管理' 
            } 
          },
        { 
          path: '/asset-management/hosts', 
          component: () => import('@/components/AssetManagement/Hosts.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '主机' 
          } 
        },
        { 
          path: '/asset-management/databases', 
          component: () => import('@/components/AssetManagement/Databases.vue'), 
          meta: {
             requiresAuth: true, 
             breadcrumbName: '数据库' 
            } 
          },
        { 
          path: '/asset-management/websites',
           component: () => import('@/components/AssetManagement/Websites.vue'), 
           meta: { 
            requiresAuth: true, 
            breadcrumbName: '网站'
           } 
        },
        { 
          path: '/web-terminal', 
          component: () => import('@/components/Terminal/WebTerminal.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: 'web终端' 
          } 
        },
        { 
          path: '/ci-cd-system',
          component: () => import('@/components/CI_CDSystem/CI_CDSystem.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: 'CI/CD系统' 
          } 
        },
        { 
          path: '/alert-management/alert-contacts', 
          component: () => import('@/components/AlertManagement/AlertContacts.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '报警联系人' 
          } 
        },
        { 
          path: '/alert-management/alert-rules', 
          component: () => import('@/components/AlertManagement/AlertRules.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '报警规则' 
          } 
        },
        { 
          path: '/audit-management/command-records', 
          component: () => import('@/components/AuditManagement/CommandRecords.vue'), 
          meta: {
            requiresAuth: true, 
            breadcrumbName: '命令记录' 
          } 
        },
        { 
          path: '/logs-management/login-logs', 
          component: () => import('@/components/LogsManagement/LoginLogs.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '登录日志' 
          } 
        },
        { 
          path: '/logs-management/operation-logs', 
          component: () => import('@/components/LogsManagement/OperationLogs.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '操作日志' 
          } 
        },
        { 
          path: '/settings/auth-settings', 
          component: () => import('@/components/Settings/AuthSettings.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '认证设置' 
          } 
        },
        { 
          path: '/settings/system-tools', 
          component: () => import('@/components/Settings/SystemTools.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '系统工具' 
          } 
        },
        { 
          path: '/settings/about', 
          component: () => import('@/components/Settings/About.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '关于' 
          } 
        },
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: '404',
      component: () => import('@/components/Global/404.vue'),
      meta: { requiresAuth: true }    // 需要认证的404页面
    }
  ]
})

router.beforeEach((to, from, next) => {
  const accessToken = localStorage.getItem('accessToken');  // 从本地存储中获取访问令牌
  const refreshToken = localStorage.getItem('refreshToken');    // 从本地存储中获取刷新令牌
  const username = localStorage.getItem('username');    // 从本地存储中获取用户名
  const isAuthenticated = !!accessToken;    // 检查用户是否已认证
  const tokenExpiry = localStorage.getItem('tokenExpiry') ? dayjs(localStorage.getItem('tokenExpiry')) : null; // 获取令牌过期时间
  const sessionTimeout = localStorage.getItem('sessionTimeout') ? dayjs(localStorage.getItem('sessionTimeout')) : null; // 获取会话超时时间
  // const now = new Date().getTime();
  const now = dayjs(); // 获取系统当前时间

  if (accessToken && now.isAfter(tokenExpiry)) {
    // 如果访问令牌已过期，清除本地存储中的相关信息
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('name');
    localStorage.removeItem('tokenExpiry');
    localStorage.removeItem('sessionTimeout');
  }

  if (now.isAfter(sessionTimeout)) {
    // 如果会话已超时，清除本地存储中的相关信息，并重定向到登录页面
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('name');
    localStorage.removeItem('tokenExpiry');
    localStorage.removeItem('sessionTimeout');
    if (to.name !== 'login') {
      return next({ path: '/login' });
    }
  } else {
    if (to.matched.length === 0) {
      // 如果访问的路径不存在
      if (isAuthenticated) {
        // 用户已登录，跳转到 404 页面
        return next({ name: 'NotFound' });
      } else {
        // 如果用户未登录，跳转到登录页面
        if (to.name !== 'login') {
          return next({ path: '/login' });
        }
      }
    } else {
      // 检查目标路由是否需要认证
      if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
        // 如果目标路由需要认证但用户未登录，跳转到登录页面
        if (to.name !== 'login') {
          return next({ path: '/login' });
        }
      } else {
        // 如果目标路由不需要认证或用户已登录，允许访问
        return next();
      }
    }
  }
  next(); // 保证在所有路径都能到达时调用next
});

export default router
