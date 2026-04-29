<template>
  <span :class="['badge', meta.cssClass]">
    <span class="w-1.5 h-1.5 rounded-full" :class="meta.dot" />
    {{ meta.label }}
  </span>
</template>

<script setup lang="ts">
import type { ExpenditureStatus } from '~/types/expenditure'
import { STATUS_META } from '~/types/expenditure'

const props = defineProps<{ status: ExpenditureStatus }>()
const meta = computed(() => STATUS_META[props.status])
</script>
