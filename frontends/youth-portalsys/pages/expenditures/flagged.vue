<template>
  <div class="px-4 md:px-8 py-6 space-y-5 max-w-5xl mx-auto">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-flagged-light flex items-center justify-center">
        <Flag :size="18" class="text-flagged" />
      </div>
      <div>
        <h1 class="text-xl font-extrabold text-[--color-ink] tracking-tight">Flagged</h1>
        <p class="text-xs text-[--color-ink-muted]">{{ flagged.length }} expenditure{{ flagged.length !== 1 ? 's' : '' }} flagged</p>
      </div>
    </div>

    <div class="rounded-2xl border border-flagged/30 bg-flagged-light px-4 py-3 flex items-start gap-2.5">
      <AlertTriangle :size="16" class="text-flagged mt-0.5 shrink-0" />
      <p class="text-xs text-flagged font-medium leading-relaxed">
        These expenditures have one or more particulars flagged by the verifier.
        The submitter must submit corrections before the record can be marked Verified.
      </p>
    </div>

    <div v-if="flagged.length" class="space-y-3">
      <ExpenditureExpenditureCard
        v-for="exp in flagged"
        :key="exp.expenditure_id"
        :expenditure="exp"
      />
    </div>

    <div v-else class="card p-12 text-center">
      <CheckCircle :size="36" class="mx-auto text-verified mb-3" />
      <p class="text-sm font-semibold text-[--color-ink]">No flagged records</p>
      <p class="text-xs text-[--color-ink-muted] mt-1">Everything is clean.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Flag, AlertTriangle, CheckCircle } from 'lucide-vue-next'

definePageMeta({ layout: 'default' })

const { expenditures } = useMockData()
const flagged = computed(() => expenditures.filter(e => e.status === 'Flagged'))
</script>
