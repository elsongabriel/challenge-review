<template>
  <div class="app">
    <header class="topbar">
      <h1>Solicitações</h1>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #f5f5f7; }
.topbar { background: #1f2937; color: white; padding: 1rem 1.5rem; }
main { padding: 1.5rem; max-width: 960px; margin: 0 auto; }
</style>
