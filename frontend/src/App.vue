<template>
  <div class="d-flex flex-column min-vh-100 bg-light">
    <Navbar />
    <main class="flex-grow-1">
      <router-view />
    </main>
    <footer class="bg-white border-top py-3 text-center text-muted small mt-auto">
      <div class="container">
        <span>Trekking Management Application V2 &bull; Modern Application Development II (MAD-II) &bull; IIT Madras</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>

<style>
/* Clean Bootstrap layout enhancements */
body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #212529;
}
</style>

