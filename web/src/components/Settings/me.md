---
layout: page
---

<div class="page-container">

<script setup>
import { ref } from 'vue'

const showQR = ref(false)
const showDonate = ref(false)
const wechatQR = '/main/wechat.png'
const donateType = ref('wechat')

const toggleQR = () => {
  showQR.value = !showQR.value
  showDonate.value = false
}

const toggleDonate = () => {
  showDonate.value = !showDonate.value
  showQR.value = false
}

const setDonateType = (type) => {
  donateType.value = type
}

const donors = [
  { name: '谢半仙', amount: 20, date: '2024-12-16 21:01:47' },
]
</script>

<div class="about-container">
  <div class="profile-card">
    <div class="profile-header">
      <div class="avatar-wrapper">
        <img class="avatar" src="/main/me.png" alt="头像" />
        <div class="avatar-decoration">
          <span class="emoji">✨</span>
          <span class="emoji">🎨</span>
        </div>
      </div>
      <div class="profile-info">
        <div class="name-wrapper">
          <h1 class="name">胡图图不涂涂</h1>
          <span class="emoji-tag">🎯</span>
        </div>
        <p class="bio">生活不易，猫猫叹气 <span class="emoji">✨</span></p>
        <div class="social-links">
          <a href="https://github.com/hukdoesn/TuRelay" target="_blank" class="social-link github">
            <img src="/main/github.svg" alt="GitHub" class="icon" />
            <span class="social-text">开源项目</span>
          </a>
          <a href="https://ext4.cn/" class="social-link blog">
            <img src="/main/blog.svg" alt="Blog" class="icon" />
            <span class="social-text">技术博客</span>
          </a>
          <div class="social-link wechat" @click="toggleQR">
            <img src="/main/wechat.svg" alt="WeChat" class="icon" />
            <span class="social-text">一起交流</span>
          </div>
          <div class="social-link donate" @click="toggleDonate">
            <img src="/main/donate.svg" alt="打赏" class="icon" />
            <span class="social-text">请我喝咖啡</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="donors-section">
    <div class="section-header">
      <div class="title-wrapper">
        <span class="emoji">🎁</span>
        <h2>打赏名单</h2>
        <span class="emoji">✨</span>
      </div>
      <p class="section-desc">感谢老板们的打赏 <span class="emoji"></span></p>
    </div>
    <div class="donors-list">
      <div v-for="donor in donors" :key="donor.date" class="donor-card">
        <div class="donor-info">
          <div class="donor-name">{{ donor.name }}</div>
          <div class="donor-amount">￥{{ donor.amount.toFixed(2) }}</div>
        </div>
        <div class="donor-meta">
          <span class="donor-date">{{ donor.date }}</span>
        </div>
      </div>
    </div>
  </div>
</div>

<div v-if="showQR" class="modal" @click.self="toggleQR">
  <div class="modal-container">
    <img :src="wechatQR" alt="微信二维码" />
    <p class="modal-tip">扫码加我微信 <span class="emoji">👻</span></p>
  </div>
</div>

<div v-if="showDonate" class="modal" @click.self="toggleDonate">
  <div class="modal-container donate-container">
    <div class="donate-header">
      <h3>请我喝杯咖啡 <span class="emoji">☕️</span></h3>
      <p class="donate-desc">谢谢你的支持哦 <span class="emoji"></span></p>
    </div>
    <div class="donate-types">
      <div 
        class="donate-type" 
        :class="{ active: donateType === 'wechat' }"
        @click="setDonateType('wechat')"
      >
        <img src="/main/wechat.svg" alt="微信支付" class="donate-icon" />
        <span>微信支付</span>
      </div>
      <div 
        class="donate-type"
        :class="{ active: donateType === 'alipay' }"
        @click="setDonateType('alipay')"
      >
        <img src="/main/alipay.svg" alt="支付宝" class="donate-icon" />
        <span>支付宝</span>
      </div>
    </div>
    <div class="donate-qr">
      <img 
        :src="donateType === 'wechat' ? '/main/wechat-pay.png' : '/main/alipay-pay.png'"
        :alt="donateType === 'wechat' ? '微信支付' : '支付宝支付'"
      />
    </div>
  </div>
</div>

<style scoped>
.page-container {
  width: 100%;
}

.about-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-card {
  background: var(--vp-c-bg);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 16px;
  object-fit: cover;
  transition: transform 0.3s;
}

.avatar:hover {
  transform: scale(1.05);
}

.avatar-decoration {
  position: absolute;
  top: -10px;
  right: -10px;
  display: flex;
  gap: 4px;
}

.profile-info {
  text-align: left;
}

.name-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.name {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
  color: var(--vp-c-text-1);
}

.emoji-tag {
  font-size: 1.2rem;
}

.bio {
  font-size: 1rem;
  color: var(--vp-c-text-2);
  margin: 0.5rem 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.emoji {
  font-size: 1.1em;
  display: inline-block;
  vertical-align: middle;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  display: flex;
  align-items: center;
  color: var(--vp-c-text-2);
  transition: all 0.3s;
  cursor: pointer;
  padding: 0.5rem 0.8rem;
  border-radius: 10px;
  text-decoration: none;
  background: var(--vp-c-bg-soft);
}

.social-link:hover {
  color: var(--vp-c-text-1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.icon {
  width: 18px;
  height: 18px;
  margin-right: 0.4rem;
}

.social-text {
  font-size: 0.9rem;
}

.donors-section {
  background: var(--vp-c-bg);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}

.section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.title-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.title-wrapper h2 {
  font-size: 1.4rem;
  color: var(--vp-c-text-1);
  margin: 0;
}

.section-desc {
  color: var(--vp-c-text-2);
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
}

.donors-list {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.donor-card {
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.3s;
}

.donor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.donor-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
}

.donor-name {
  font-weight: 500;
  color: var(--vp-c-text-1);
}

.donor-amount {
  color: #666;
  font-weight: 600;
}

.donor-meta {
  text-align: right;
  font-size: 0.85rem;
}

.donor-date {
  color: var(--vp-c-text-2);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background: var(--vp-c-bg);
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.modal-container img {
  max-width: 300px;
  height: auto;
  display: block;
  border-radius: 8px;
}

.modal-tip {
  text-align: center;
  margin: 1rem 0 0;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.donate-container {
  width: 100%;
  max-width: 400px;
}

.donate-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.donate-header h3 {
  margin: 0;
  color: var(--vp-c-text-1);
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.donate-desc {
  margin: 0.5rem 0 0;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.donate-types {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.donate-type {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  background: var(--vp-c-bg-soft);
  transition: all 0.3s;
}

.donate-type:hover {
  transform: translateY(-2px);
}

.donate-type.active {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-text-2);
}

.donate-icon {
  width: 18px;
  height: 18px;
  margin-right: 0.5rem;
}

.donate-qr {
  background: var(--vp-c-bg-soft);
  padding: 1rem;
  border-radius: 12px;
}

.donate-qr img {
  max-width: 280px;
  margin: 0 auto;
  border-radius: 8px;
}

@media (max-width: 640px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  .profile-info {
    text-align: center;
  }
  .name-wrapper {
    justify-content: center;
  }
  .social-links {
    justify-content: center;
    flex-wrap: wrap;
  }
  .donors-list {
    grid-template-columns: 1fr;
  }
}
</style>

</div>