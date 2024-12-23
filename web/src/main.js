// main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from '../router';
import Antd from 'ant-design-vue';
import './assets/css/reset.css';
import axios from 'axios';
import './assets/css/global.css';
import dayjs from 'dayjs';

// 配置 axios
axios.defaults.baseURL = 'https://admin.ext4.cn'; // 使用域名访问后端
axios.defaults.baseURL = 'http://172.17.103.22:8100';

// 其他全局配置，例如超时时间、请求头等
axios.defaults.timeout = 10000;

// 创建 Vue 应用
const app = createApp(App);

// 将 axios 添加到 Vue 实例的全局属性中
app.config.globalProperties.$axios = axios;

// 定义 WebSocket 服务器地址为全局属性
app.config.globalProperties.$wsServerAddress = 'ws://172.17.103.22:8100';

// 将 dayjs 添加到 Vue 实例的全局属性中
app.config.globalProperties.$dayjs = dayjs;

// 使用 Ant Design Vue 和 Vue Router
app.use(router).use(Antd);

// 挂载 Vue 应用
app.mount('#app');
