<template>
  <q-layout view="lHh Lpr lFf">
    <q-header>
      <q-toolbar>
        <q-toolbar-title>
          <img src="~assets/logo-light.png" class="q-pt-sm q-pl-md" width="80"/>
        </q-toolbar-title>

        <div>Demo OCR v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
</script>
