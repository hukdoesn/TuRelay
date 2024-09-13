<template>
    <div class="terminal-container" ref="terminalContainer"></div>
  </template>
  
  <script setup>
  import { Terminal } from 'xterm';
  import { FitAddon } from 'xterm-addon-fit';
  import { onMounted } from 'vue';
  
  const terminalContainer = ref(null);
  let terminal;
  let fitAddon;
  
  onMounted(() => {
      terminal = new Terminal();
      fitAddon = new FitAddon();
      terminal.loadAddon(fitAddon);
      terminal.open(terminalContainer.value);
      fitAddon.fit(); // Fit terminal to container
  });
  </script>
  
  <style scoped>
  .terminal-container {
      height: 100%; /* Ensure terminal container takes up full height */
      width: 100%;  /* Ensure terminal container takes up full width */
  }
  
  /* Add left padding to the terminal content */
  .xterm {
      padding-left: 10px !important; /* Customize this value as needed */
  }
  </style>
  