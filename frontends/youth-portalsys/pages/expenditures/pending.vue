<template>
  <div class="px-4 md:px-8 py-6 space-y-5 max-w-5xl mx-auto">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-pending-light flex items-center justify-center">
        <Clock :size="18" class="text-pending" />
      </div>
      <div>
        <h1 class="text-xl font-extrabold text-[--color-ink] tracking-tight">Pending Review</h1>
        <p class="text-xs text-[--color-ink-muted]">{{ pending.length }} awaiting verification</p>
      </div>
    </div>

    <div v-if="pending.length" class="space-y-3">
      <ExpenditureExpenditureCard
        v-for="exp in pending"
        :key="exp.expenditure_id"
        :expenditure="exp"
      />
    </div>

    <div v-else class="card p-12 text-center">
      <CheckCircle :size="36" class="mx-auto text-verified mb-3" />
      <p class="text-sm font-semibold text-[--color-ink]">All caught up!</p>
      <p class="text-xs text-[--color-ink-muted] mt-1">No expenditures pending review.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Clock, CheckCircle } from 'lucide-vue-next'

definePageMeta({ layout: 'default' })

const { expenditures } = useMockData()
const pending = computed(() => expenditures.filter(e => e.status === 'Unverified'))
</script>
