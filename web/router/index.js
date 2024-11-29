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

// 修改响应拦截器，处理token过期等情况
axios.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // token 过期或无效
                    if (error.response.data.code === 'token_expired') {
                        message.error('登录已过期，请重新登录');
                    } else if (error.response.data.code === 'token_invalid') {
                        message.error('登录状态无效，请重新登录');
                    }
                    // 清除本地存储
                    localStorage.clear();
                    // 跳转到登录页
                    router.push('/login');
                    break;
                case 403:
                    message.error('账号被锁定，请联系管理员');
                    localStorage.clear();
                    router.push('/login');
                    break;
                default:
                    return Promise.reject(error);
            }
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
          },
          children: [
            {
              path: ':username',
              name: 'userDetail',
              component: () => import('@/components/UserManagement/module/UserListDetail.vue'),
              meta: {
                requiresAuth: true,
                breadcrumbName: '用户详情'
              }
            }
          ]
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
          path: '/user-management/lock-record', 
          component: () => import('@/components/UserManagement/LockRecord.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '锁定记录' 
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
            breadcrumbName: '主机列表' 
          },
          children: [
            {
              path: ':id',
              name: 'hostDetail',
              component: () => import('@/components/AssetManagement/module/HostDetail.vue'),
              meta: {
                requiresAuth: true,
                breadcrumbName: '主机详情'
              }
            }
          ]
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
            breadcrumbName: '站点监控'
           },
           children: [
             {
               path: ':id',
               name: 'websiteDetail',
               component: () => import('@/components/AssetManagement/module/WebsitesDetail.vue'),
               meta: {
                 requiresAuth: true,
                 breadcrumbName: '站点监控详情'
               }
             }
           ]
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
            breadcrumbName: '告警联系人' 
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
          path: '/alert-management/command-alert',
          component: () => import('@/components/AlertManagement/CommandAlert.vue'),
          meta: {
            requiresAuth: true,
            breadcrumbName: '命令告警'
          },
          children: [
            {
              path: ':id',
              name: 'commandAlertDetail',
              component: () => import('@/components/AlertManagement/module/CommandAlertDetail.vue'),
              meta: {
                requiresAuth: true,
                breadcrumbName: '命令告警详情'
              }
            }
          ]
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
          path: '/settings/safe-settings', 
          component: () => import('@/components/Settings/SafeSettings.vue'), 
          meta: { 
            requiresAuth: true, 
            breadcrumbName: '安全设置' 
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
      path: '/web-terminal/:hostId', 
      component: () => import('@/components/Terminal/WebShellTerminal.vue'), 
      meta: { 
        requiresAuth: true, 
        breadcrumbName: 'web终端' 
      } 
    },    
    {
      path: '/web-terminal', 
      component: () => import('@/components/Terminal/WebShellTerminal.vue'), 
      meta: { 
        requiresAuth: true, 
        breadcrumbName: 'web终端' 
      } 
    },    
    {
      path: '/:pathMatch(.*)*',
      name: '404',
      component: () => import('@/components/Global/404.vue'),
      meta: { requiresAuth: true }    // 需要认证的404页面
    }
  ]
})

// 修改路由守卫
router.beforeEach((to, from, next) => {
    const accessToken = localStorage.getItem('accessToken');
    const tokenExpiry = localStorage.getItem('tokenExpiry') ? dayjs(localStorage.getItem('tokenExpiry')) : null;
    const sessionTimeout = localStorage.getItem('sessionTimeout') ? dayjs(localStorage.getItem('sessionTimeout')) : null;
    const now = dayjs();

    // 检查是否需要认证
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

    if (requiresAuth) {
        if (!accessToken) {
            message.warning('请先登录');
            next('/login');
            return;
        }

        // 检查token是否过期
        if (tokenExpiry && now.isAfter(tokenExpiry)) {
            message.error('登录已过期，请重新登录');
            // 调用登出接口，确保后端清理token
            axios.post('/api/logout/').finally(() => {
                localStorage.clear();
                next('/login');
            });
            return;
        }

        // 检查会话是否超时
        if (sessionTimeout && now.isAfter(sessionTimeout)) {
            message.error('会话已超时，请重新登录');
            // 调用登出接口，确保后端清理token
            axios.post('/api/logout/').finally(() => {
                localStorage.clear();
                next('/login');
            });
            return;
        }
    }

    next();
});

export default router
