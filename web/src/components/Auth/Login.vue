<template>
  <div class="login-container">
      <img src="@/assets/svg/熊猫上班.svg" alt="Logo" class="logo">
      <h1>登录</h1>
      <form @submit.prevent="submitForm">
          <div class="form-group">
              <input type="text" placeholder="用户名" v-model="username" required>
          </div>
          <div class="form-group">
              <input type="password" placeholder="密码" v-model="password" required>
          </div>
          <button type="submit" :disabled="!canSubmit" :class="{ 'active': canSubmit }">登录</button>
      </form>
  </div>
</template>

<script>
import { message } from 'ant-design-vue';
import axios from 'axios';  // 引入axios用于请求后端API

export default {
data() {
  return {
    username: '',
    password: '',
  };
},
computed: {
  canSubmit() {
    return this.username.length > 0 && this.password.length > 0; // 按钮启用条件
  }
},
methods: {
  async submitForm() {
    try {
      const response = await axios.post('api/login/', {
        username: this.username,
        password: this.password,
      });

      if (response.status === 200) {
        const accessToken = response.data.access_token;
        const refreshToken = response.data.refresh_token;
        const name = response.data.name; // 获取 name 字段
        const loginTime = this.$dayjs(); // 获取当前时间
        const tokenExpiry = loginTime.add(2, 'hour').format(); // 格式化后的token过期时间
        const isReadOnly = response.data.is_read_only;  // 获取只读权限状态
        const sessionTimeout = loginTime.add(2, 'hour').format(); // 格式化后的登录超时时间

        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
        localStorage.setItem('name', name);
        localStorage.setItem('tokenExpiry', tokenExpiry);
        localStorage.setItem('isReadOnly', isReadOnly);  // 存储只读权限状态
        localStorage.setItem('sessionTimeout', sessionTimeout);

        // message.success('登录成功');
        this.$router.push('/home'); // 登录成功后跳转到主页
      }
    } catch (error) {
      if (error.response) {
        // 如果后端返回了特定的错误代码和消息
        switch (error.response.status) {
          case 400:
            message.error('无效的凭据');
            break;
          case 401:
            message.error('密码错误');
            break;
          case 403:
            message.error('账号被锁定，请联系管理员');
            break;
          case 404:
            message.error('找不到用户');
            break;
          case 423:
            message.error('账号被锁定');
            break;
          default:
            message.error('登录请求失败');  // 对于其他HTTP状态码，显示通用错误消息
        }
      } else {
        // 如果没有响应（网络或其他原因）
        message.error('请求无响应');
      }
      console.log('登录请求失败：', error);
    }
  }
}
}
</script>


<!-- 1 -->
<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #F6F8FF;

}

.logo {
  width: 80px;
  margin-bottom: 20px;
}

h1 {
  margin: 10px 10px;
  color: #333;
  font-size: 16px;
}

.form-group {
  margin-bottom: 15px;
}

input[type="text"],
input[type="password"] {
  width: 300px;
  height: 18px;
  padding: 5px 0;
  background-color: transparent;
  border: none;
  border-bottom: 1px solid #8A91B4;
  transition: border-color 0.3s;
  outline: none;
  font-size: 14px;
  margin-top: 20px;
}

input[type="text"]::placeholder, input[type="password"]::placeholder {
  font-size: 14px;
  color: #aaa;
}

button {
  margin-top: 20px;
  padding: 10px 0;
  /* background-color: rgba(237, 239, 252, 1); */
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
  width: 300px;
}
button.active {
  background-color: #362A89; /* 按钮激活时的背景颜色 */
  color: white;
  cursor: pointer;
}

button:disabled {
  background-color: rgba(237, 239, 252, 1); /* 禁用状态下的背景颜色 */
  color: rgba(166, 172, 205, 1);
  cursor: not-allowed;
}
</style>