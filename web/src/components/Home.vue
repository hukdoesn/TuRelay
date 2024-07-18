<template>
  <a-layout style="min-height: 100vh;">
    <Sidebar />
    <a-layout style="background-color: #fff;">
      <Header />
      <a-layout-content style="margin: 0 16px; flex: 1; display: flex; flex-direction: column;">
        <Content style="flex: 1;" />
      </a-layout-content>
      <Footer />
    </a-layout>
  </a-layout>
</template>

<script setup>
import Sidebar from './Core/Sider.vue';
import Header from './Core/Header.vue';
import Content from './Core/Content.vue';
import Footer from './Core/Footer.vue';
</script>

  
  <style scoped>
  .site-layout .site-layout-background {
    background: #fff;
  }
  
  [data-theme='dark'] .site-layout .site-layout-background {
    background: #141414;
  }
  </style>
  