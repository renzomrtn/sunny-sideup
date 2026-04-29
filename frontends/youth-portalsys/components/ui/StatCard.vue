<template>
  <div class="card p-5 flex items-start gap-4 animate-slide-up">
    <div
      class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0"
      :style="{ background: `${color}18` }"
    >
      <component :is="icon" :size="20" :style="{ color }" />
    </div>
    <div class="min-w-0">
      <p class="text-[11px] font-semibold uppercase tracking-widest text-[--color-ink-muted] leading-none mb-1.5">
        {{ label }}
      </p>
      <p class="text-2xl font-extrabold text-[--color-ink] leading-none tracking-tight">
        {{ value }}
      </p>
      <p v-if="sub" class="text-xs text-[--color-ink-muted] mt-1">{{ sub }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  label: string
  value: string | number
  sub?: string
  icon: Component
  color: string
}>()
</script>
