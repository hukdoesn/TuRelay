<template>
  <div class="rdp-container" ref="rdpContainer"></div>
  <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import Guacamole from 'guacamole-common-js';

const props = defineProps({
  hostId: {
    type: String,
    required: true,
  },
});

const errorMessage = ref('');
let guacClient = null;
let tunnel = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 3;

const rdpContainer = ref(null);

function initializeConnection() {
  const wsUrl = `ws://192.168.5.13:8100/ws/rdp/${props.hostId}/`;
  console.log("WebSocket URL:", wsUrl);
  tunnel = new Guacamole.WebSocketTunnel(wsUrl);
  
  tunnel.onerror = function(status) {
    console.error("Tunnel error:", status);
    errorMessage.value = `连接错误: ${status.code} - ${status.message}`;
    attemptReconnect();
  };

  guacClient = new Guacamole.Client(tunnel);

  rdpContainer.value.appendChild(guacClient.getDisplay().getElement());

  guacClient.onerror = function(error) {
    console.error("Client error:", error);
    errorMessage.value = `客户端错误: ${error.message}`;
    attemptReconnect();
  };

  guacClient.onstatechange = (state) => {
    console.log("Guacamole client state changed:", state);
    if (state === Guacamole.Client.State.IDLE) {
      console.log("Guacamole client is idle");
    } else if (state === Guacamole.Client.State.CONNECTING) {
      console.log("Guacamole client is connecting");
    } else if (state === Guacamole.Client.State.CONNECTED) {
      console.log("Guacamole client is connected");
      reconnectAttempts = 0;  // 重置重连尝试次数
    } else if (state === Guacamole.Client.State.DISCONNECTING) {
      console.log("Guacamole client is disconnecting");
    } else if (state === Guacamole.Client.State.DISCONNECTED) {
      console.log("Guacamole client is disconnected");
      if (guacClient.getErrorMessage()) {
        errorMessage.value = guacClient.getErrorMessage();
      } else {
        errorMessage.value = 'RDP 连接已关闭。';
      }
      attemptReconnect();
    }
  };

  guacClient.connect();
}

function attemptReconnect() {
  if (reconnectAttempts < maxReconnectAttempts) {
    reconnectAttempts++;
    console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`);
    setTimeout(() => {
      if (guacClient) {
        guacClient.disconnect();
      }
      initializeConnection();
    }, 5000);  // 5秒后尝试重连
  } else {
    console.error("Max reconnection attempts reached.");
    errorMessage.value = "无法重新连接到 RDP 服务器。请刷新页面重试。";
  }
}

let heartbeatInterval;

function startHeartbeat() {
  heartbeatInterval = setInterval(() => {
    if (guacClient && guacClient.getState() === Guacamole.Client.State.CONNECTED) {
      guacClient.sendKeyEvent(1, 0x00);  // 发送一个无害的按键事件作为心跳
    }
  }, 5000);  // 每5秒发送一次心跳
}

function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
  }
}

onMounted(() => {
  initializeConnection();
  startHeartbeat();
});

onBeforeUnmount(() => {
  if (guacClient) {
    guacClient.disconnect();
  }
  stopHeartbeat();
});
</script>

<style scoped>
.rdp-container {
  width: 100%;
  height: 100%;
  background: #000;
  position: relative;
}

.error-message {
  color: red;
  text-align: center;
  padding: 20px;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}
</style>
