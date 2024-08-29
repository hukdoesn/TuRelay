import { createApp } from 'vue';
import App from './App.vue';
import router from '../router';
import Antd from 'ant-design-vue';
import './assets/css/reset.css';
import axios from 'axios';
import './assets/css/global.css'; 
import dayjs from 'dayjs';

// 配置 axios
axios.defaults.baseURL = 'http://172.17.102.34:8100'; // 根据您的后端服务地址修改
//  axios.defaults.baseURL = 'http://192.168.5.30:8100';
// axios.defaults.baseURL = 'http://192.168.102.140:8100';
// axios.defaults.baseURL = 'http://localhost:8100'; // 根据您的后端服务地址修改

// 其他全局配置，例如超时时间、请求头等
axios.defaults.timeout = 10000;

// 创建 Vue 应用
const app = createApp(App);

// 将 axios 添加到 Vue 实例的全局属性中
app.config.globalProperties.$axios = axios;

// 将 dayjs 添加到 Vue 实例的全局属性中
app.config.globalProperties.$dayjs = dayjs;

// 使用 Ant Design Vue 和 Vue Router
app.use(router).use(Antd);

// 挂载 Vue 应用
app.mount('#app');
