<template>
  <NuxtLink
    :to="`/expenditures/${expenditure.expenditure_id}`"
    class="card card-hover block p-4 animate-fade-in"
  >
    <!-- Top row -->
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="text-sm font-bold text-[--color-ink] leading-snug truncate">
          {{ expenditure.line_item_snapshot.program_name }}
        </p>
        <p class="text-xs text-[--color-ink-muted] mt-0.5">
          {{ expenditure.submitted_by_snapshot.full_name }}
          <span class="mx-1 text-gray-300">·</span>
          {{ expenditure.submitted_by_snapshot.barangay ?? expenditure.submitted_by_snapshot.position }}
        </p>
      </div>
      <UiStatusBadge :status="expenditure.status" />
    </div>

    <!-- Amounts -->
    <div class="mt-3 flex items-center justify-between">
      <div>
        <p class="text-[10px] font-semibold uppercase tracking-widest text-[--color-ink-muted]">Total Claimed</p>
        <p class="text-base font-extrabold mono text-[--color-ink]">
          {{ fmt.currency(expenditure.total_amount_spent) }}
        </p>
      </div>
      <div class="text-right">
        <p class="text-[10px] font-semibold uppercase tracking-widest text-[--color-ink-muted]">Budget</p>
        <p class="text-sm font-bold mono text-[--color-ink-muted]">
          {{ fmt.currency(expenditure.line_item_snapshot.budget_allocation) }}
        </p>
      </div>
    </div>

    <!-- Budget bar -->
    <div class="mt-2.5 h-1.5 rounded-full bg-[--color-surface] overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-700"
        :class="barColor"
        :style="{ width: `${pct}%` }"
      />
    </div>
    <p class="text-[10px] text-[--color-ink-muted] mt-1">
      {{ pct }}% of budget utilised
      <span v-if="expenditure.particulars?.length" class="ml-2 text-gray-400">
        · {{ expenditure.particulars.length }} particular{{ expenditure.particulars.length !== 1 ? 's' : '' }}
      </span>
    </p>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { Expenditure } from '~/types/expenditure'

const props = defineProps<{ expenditure: Expenditure }>()
const fmt = useFormatters()

const pct = computed(() =>
  fmt.budgetPercent(
    props.expenditure.total_amount_spent,
    props.expenditure.line_item_snapshot.budget_allocation,
  ),
)

const barColor = computed(() => {
  if (props.expenditure.status === 'Flagged') return 'bg-flagged'
  if (pct.value >= 90) return 'bg-pending'
  return 'bg-verified'
})
</script>
