<template>
  <div id="terminal" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { onMounted, ref, onBeforeUnmount } from 'vue';
import Guacamole from 'guacamole-common-js';

const props = defineProps({
  hostId: {
    type: String,
    required: true,
  },
});

let socket = null;   // WebSocket 连接
let guac = null;     // Guacamole 客户端实例

const error = ref(null);  // 错误信息

onMounted(() => {
  const initialWidth = window.innerWidth;
  const initialHeight = window.innerHeight;
  const initialDPI = 96; // 常规 DPI 值

  // 建立 WebSocket 连接，将 hostId 发送给后端
  socket = new WebSocket(`ws://localhost:8100/ws/guacamole/${props.hostId.replace(/-/g, '')}/`);

  // 处理 WebSocket 连接打开时的逻辑
  socket.onopen = function () {
    console.log('WebSocket connection opened for hostId:', props.hostId);
  };

  // 处理收到来自 WebSocket 的消息（来自 guacd）
  socket.onmessage = function (event) {
    if (!guac) {
      // 初始化 Guacamole 客户端
      guac = new Guacamole.Client(new Guacamole.WebSocketTunnel(socket));

      // 将 Guacamole 显示的内容渲染到 #terminal 容器中
      const displayElement = guac.getDisplay().getElement();
      document.getElementById('terminal').appendChild(displayElement);

      // 设置初始分辨率
      guac.sendSize(initialWidth, initialHeight, initialDPI); // 发送初始宽度、高度和 DPI

      // 自动调整显示大小以适应窗口
      window.addEventListener('resize', () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        guac.sendSize(width, height, initialDPI);
      });

      // 启动连接并接收来自 guacd 的数据
      guac.connect();

      // 处理连接状态变化
      guac.onstatechange = (state) => {
        if (state === Guacamole.Client.State.CONNECTED) {
          console.log('Connected to remote desktop via Guacamole');
        } else if (state === Guacamole.Client.State.DISCONNECTED) {
          console.log('Disconnected from remote desktop');
          error.value = 'Disconnected from remote desktop';
        }
      };

      // 处理显示上的错误
      guac.onerror = (err) => {
        console.error('Error in Guacamole client:', err);
        error.value = err.message;
      };
    }

    // 将所有收到的消息传递给 Guacamole 客户端
    guac.receive(event.data);
  };

  // 处理 WebSocket 连接关闭时的逻辑
  socket.onclose = function () {
    console.log('WebSocket connection closed');
    if (guac) {
      guac.disconnect();
      guac = null;
    }
  };

  // 处理 WebSocket 错误
  socket.onerror = function (err) {
    console.error('WebSocket error:', err);
    error.value = 'WebSocket connection error';
  };

  // 捕捉键盘按键并发送给后端
  window.addEventListener('keydown', (event) => {
    if (guac) {
      guac.sendKeyEvent(1, event.keyCode); // 按键按下事件
    }
  });

  window.addEventListener('keyup', (event) => {
    if (guac) {
      guac.sendKeyEvent(0, event.keyCode); // 按键松开事件
    }
  });
});

// 组件卸载时清理资源
onBeforeUnmount(() => {
  if (guac) {
    guac.disconnect();
    guac = null;
  }
  if (socket) {
    socket.close();
  }
});
</script>

<style scoped>
#terminal {
  width: 100%;
  height: 100%;
  background-color: black;
}
</style>
