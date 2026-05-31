<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-body">
      <AppSidebar />
      <main class="app-main">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-body {
  flex: 1;
  display: flex;
  margin-top: var(--header-height);
  overflow: hidden;
}

.app-main {
  flex: 1;
  overflow: hidden;
  display: flex;
}
</style>
