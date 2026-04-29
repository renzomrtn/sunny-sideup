<template>
  <div class="px-4 md:px-8 py-6 space-y-5 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-2">
      <div class="w-9 h-9 rounded-xl bg-[--color-primary-lt] flex items-center justify-center">
        <ShieldCheck :size="18" class="text-[--color-primary]" />
      </div>
      <div>
        <h1 class="text-xl font-extrabold text-[--color-ink]">Verify Expenditure</h1>
        <p class="text-xs text-[--color-ink-muted]">Select a pending expenditure to begin verification</p>
      </div>
    </div>

    <div class="space-y-3">
      <ExpenditureExpenditureCard
        v-for="exp in pending"
        :key="exp.expenditure_id"
        :expenditure="exp"
      />
      <div v-if="!pending.length" class="card p-10 text-center">
        <CheckCircle :size="32" class="mx-auto text-verified mb-3" />
        <p class="text-sm font-semibold text-[--color-ink]">No pending expenditures</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ShieldCheck, CheckCircle } from 'lucide-vue-next'
definePageMeta({ layout: 'default' })
const { expenditures } = useMockData()
const pending = computed(() => expenditures.filter(e => e.status === 'Unverified'))
</script>
