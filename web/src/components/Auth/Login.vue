<template>
  <div class="login-container">
    <icon-font type="icon-login" class="logo" /> 
    <h1>登录</h1>
    
    <!-- 常规登录表单 -->
    <form v-if="!showMFABind && !showMFAVerify" @submit.prevent="submitForm">
      <div class="form-group">
        <input type="text" placeholder="用户名" v-model="username" required>
      </div>
      <div class="form-group">
        <input type="password" placeholder="密码" v-model="password" required>
      </div>
      <button type="submit" :disabled="!canSubmit" :class="{ 'active': canSubmit }">登录</button>
    </form>

    <!-- MFA绑定界面 -->
    <div v-if="showMFABind" class="mfa-container">
      <h2>MFA绑定</h2>
      <div class="qr-code">
        <img :src="'data:image/png;base64,' + qrCode" alt="MFA QR Code">
      </div>
      <p class="mfa-tip">请使用Google Authenticator扫描二维码</p>
      <form @submit.prevent="handleMFABind">
        <div class="form-group">
          <input type="text" placeholder="请输入验证码" v-model="otpCode" required>
        </div>
        <button type="submit" class="active">确认绑定</button>
      </form>
    </div>

    <!-- MFA验证界面 -->
    <div v-if="showMFAVerify" class="mfa-container">
      <h2>MFA验证</h2>
      <p class="mfa-tip">请输入Google Authenticator中的验证码</p>
      <form @submit.prevent="handleMFAVerify">
        <div class="form-group">
          <input type="text" placeholder="验证码" v-model="otpCode" required>
        </div>
        <button type="submit" class="active">验证</button>
      </form>
    </div>
  </div>
</template>

<script>
import { message } from 'ant-design-vue';
import axios from 'axios';
import IconFont from '@/icons';

export default {
  components: {
    IconFont
  },
  data() {
    return {
      username: '',
      password: '',
      otpCode: '',
      showMFABind: false,
      showMFAVerify: false,
      qrCode: '',
      secretKey: '',
    };
  },
  computed: {
    canSubmit() {
      return this.username.length > 0 && this.password.length > 0;
    }
  },
  methods: {
    async submitForm() {
      try {
        const response = await axios.post('api/login/', {
          username: this.username,
          password: this.password,
        });

        if (response.data.status === 'mfa_required') {
          if (response.data.require_bind) {
            this.showMFABind = true;
            this.qrCode = response.data.qr_code;
            this.secretKey = response.data.secret_key;
          } else {
            this.showMFAVerify = true;
          }
          return;
        }

        this.handleLoginSuccess(response.data);
      } catch (error) {
        this.handleLoginError(error);
      }
    },

    async handleMFABind() {
      try {
        const response = await axios.post('api/mfa/bind/', {
          username: this.username,
          secret_key: this.secretKey,
          otp_code: this.otpCode
        });

        if (response.status === 200) {
          message.success('MFA绑定成功');
          this.showMFABind = false;
          this.showMFAVerify = true;
          this.otpCode = '';
        }
      } catch (error) {
        message.error('MFA绑定失败');
      }
    },

    async handleMFAVerify() {
      try {
        const response = await axios.post('api/login/', {
          username: this.username,
          password: this.password,
          otp_code: this.otpCode
        });

        this.handleLoginSuccess(response.data);
      } catch (error) {
        this.handleLoginError(error);
      }
    },

    handleLoginSuccess(data) {
      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('refreshToken', data.refresh_token);
      localStorage.setItem('name', data.name);
      localStorage.setItem('tokenExpiry', this.$dayjs().add(2, 'hour').format());
      localStorage.setItem('isReadOnly', data.is_read_only);
      localStorage.setItem('sessionTimeout', this.$dayjs().add(2, 'hour').format());

      this.$router.push('/home');
    },

    handleLoginError(error) {
      if (error.response) {
        const errorMessages = {
          400: '无效的凭据',
          401: error.response.data.status === 'mfa_invalid' ? 'MFA验证码错误' : '密码错误',
          403: '账号被锁定，请联系管理员',
          404: '找不到用户',
          423: '账号被锁定'
        };
        message.error(errorMessages[error.response.status] || '登录请求失败');
      } else {
        message.error('请求无响应');
      }
    }
  }
}
</script>

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
  font-size: 80px;
  /* 控制图标的大小 */
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

input[type="text"]::placeholder,
input[type="password"]::placeholder {
  font-size: 14px;
  color: #aaa;
}

button {
  margin-top: 20px;
  padding: 10px 0;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
  width: 300px;
}

button.active {
  background-color: #362A89;
  color: white;
  cursor: pointer;
}

button:disabled {
  background-color: rgba(237, 239, 252, 1);
  color: rgba(166, 172, 205, 1);
  cursor: not-allowed;
}

.mfa-container {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.qr-code {
  margin: 20px auto;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 4px;
  width: fit-content;
}

.qr-code img {
  max-width: 200px;
  height: auto;
}

.mfa-tip {
  color: #666;
  margin: 15px 0;
  font-size: 14px;
}

h2 {
  color: #333;
  font-size: 18px;
  margin-bottom: 20px;
}
</style>
