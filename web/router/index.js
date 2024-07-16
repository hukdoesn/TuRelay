import { createRouter, createWebHistory } from 'vue-router'

import NotFound from '../src/components/404.vue'
import dayjs from 'dayjs';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../src/components/Login.vue'),
      meta: { requiresAuth: false, breadcrumbName: '登录' }   // 登录页面不需要认证

    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../src/components/code/Home.vue'),
      meta: { requiresAuth: true }    // 主页需要认证
    },
    {
      path: '/',
      redirect: '/home' // 根路径重定向到/home
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../src/components/404.vue'),
      // component: NotFound,
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
    localStorage.removeItem('username');
    localStorage.removeItem('tokenExpiry');
    localStorage.removeItem('sessionTimeout');
  }

  if (now.isAfter(sessionTimeout)) {
    // 如果会话已超时，清除本地存储中的相关信息，并重定向到登录页面
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('username');
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
