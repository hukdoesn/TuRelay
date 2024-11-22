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
axios.defaults.baseURL = 'http://172.17.103.237:8100'; // 根据您的后端服务地址修改
// axios.defaults.baseURL = 'http://192.168.222.86:8100';
//  axios.defaults.baseURL = 'http://192.168.0.104:8100';
// axios.defaults.baseURL = 'http://192.168.5.29:8100';
// axios.defaults.baseURL = 'http://localhost:8100'; // 根据您的后端服务地址修改

// 其他全局配置，例如超时时间、请求头等
axios.defaults.timeout = 10000;

// 创建 Vue 应用
const app = createApp(App);

// 将 axios 添加到 Vue 实例的全局属性中
app.config.globalProperties.$axios = axios;

// 定义 WebSocket 服务器地址为全局属性
// app.config.globalProperties.$wsServerAddress = 'ws://192.168.5.29:8100';
// app.config.globalProperties.$wsServerAddress = 'ws://192.168.222.86:8100';
app.config.globalProperties.$wsServerAddress = 'ws://172.17.103.237:8100';

// app.config.globalProperties.$wsServerAddress = 'ws://192.168.5.82:8081/guacamole';
// app.config.globalProperties.$guacamoleUrl = 'http://192.168.0.104:8081/guacamole';
app.config.globalProperties.$guacamoleUrl = 'http://172.17.103.237:8081/guacamole';

// 将 dayjs 添加到 Vue 实例的全局属性中
app.config.globalProperties.$dayjs = dayjs;

// 使用 Ant Design Vue 和 Vue Router
app.use(router).use(Antd);

// 挂载 Vue 应用
app.mount('#app');
