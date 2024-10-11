<template>
  <div class="rdp-container">
    <div ref="display" class="rdp-display"></div>
  </div>
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

const display = ref(null);
let tunnel = null;
let client = null;

onMounted(() => {
  initializeRdpConnection();
});

onBeforeUnmount(() => {
  if (client) {
    client.disconnect();
  }
});

const initializeRdpConnection = () => {
  // 确保 hostId 被正确传递
  if (!props.hostId) {
    console.error('hostId is required but not provided.');
    return;
  }

  // Remove any non-alphanumeric characters from hostId
  const cleanHostId = props.hostId.replace(/[^a-zA-Z0-9]/g, '');

  // Create a new WebSocket tunnel
  tunnel = new Guacamole.WebSocketTunnel(
    `ws://172.17.102.69:8100/guacamole/${cleanHostId}/`
  );

  // Create a new Guacamole client using the tunnel
  client = new Guacamole.Client(tunnel);

  // Get the display div from the template
  const displayDiv = display.value;

  // Attach the client display to the display div
  displayDiv.appendChild(client.getDisplay().getElement());

  // Error handling
  client.onerror = (error) => {
    console.error('Guacamole client error:', error);
  };

  // Connect the client
  client.connect();

  // Adjust the display size when the window is resized
  window.addEventListener('resize', handleResize);
};

const handleResize = () => {
  if (client) {
    const displayWidth = display.value.offsetWidth;
    const displayHeight = display.value.offsetHeight;
    client.sendSize(displayWidth, displayHeight);
  }
};
</script>

<style scoped>
.rdp-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.rdp-display {
  width: 100%;
  height: 100%;
}
</style>