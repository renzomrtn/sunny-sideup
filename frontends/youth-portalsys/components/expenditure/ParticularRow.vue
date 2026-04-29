<template>
  <div class="rounded-xl border border-[--color-border] bg-white p-4 space-y-3">

    <!-- Header -->
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="text-sm font-semibold text-[--color-ink] leading-snug">
          {{ particular.particular_name }}
        </p>
        <p class="text-xs text-[--color-ink-muted] mt-0.5">
          {{ particular.vendor?.vendor_name ?? 'No vendor' }}
          <span v-if="particular.vendor" class="mx-1 text-gray-300">·</span>
          <span v-if="particular.vendor" class="text-gray-400">{{ particular.vendor.category }}</span>
        </p>
      </div>
      <p class="text-base font-extrabold mono text-[--color-ink] shrink-0">
        {{ fmt.currency(particular.amount_claimed) }}
      </p>
    </div>

    <!-- Date + Attachment indicator -->
    <div class="flex items-center gap-3 text-xs text-[--color-ink-muted]">
      <span class="flex items-center gap-1">
        <Calendar :size="12" />
        {{ fmt.date(particular.date_of_expense) }}
      </span>
      <span v-if="particular.file_ref_id" class="flex items-center gap-1">
        <Paperclip :size="12" />
        Receipt attached
      </span>
      <span v-else class="flex items-center gap-1 text-flagged">
        <AlertCircle :size="12" />
        No attachment
      </span>
    </div>

    <!-- Active flags from most recent verification -->
    <div v-if="activeFlags.length" class="flex flex-wrap gap-1.5 pt-1">
      <span
        v-for="f in activeFlags"
        :key="f"
        class="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5
               rounded-full bg-flagged-light text-flagged"
      >
        <Flag :size="9" />
        {{ f }}
      </span>
    </div>

    <!-- Remarks -->
    <p
      v-if="latestVerification?.remarks"
      class="text-xs text-[--color-ink-muted] italic border-l-2 border-[--color-border] pl-2"
    >
      "{{ latestVerification.remarks }}"
    </p>

    <!-- Actions slot -->
    <div v-if="$slots.actions" class="pt-1 border-t border-[--color-border]">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Calendar, Paperclip, AlertCircle, Flag } from 'lucide-vue-next'
import type { ExpenditureParticular, VerificationFlagging } from '~/types/expenditure'

const props = defineProps<{
  particular: ExpenditureParticular
  verifications?: VerificationFlagging[]
}>()

const fmt = useFormatters()

const latestVerification = computed(() =>
  props.verifications?.slice(-1)[0] ?? props.particular.verifications?.slice(-1)[0],
)

const FLAG_LABELS: Record<string, string> = {
  flag_particular: 'Invalid Particular',
  flag_amount:     'Amount Mismatch',
  flag_date:       'Date Issue',
  flag_attachment: 'Missing/Invalid OR',
  flag_vendor:     'Vendor Issue',
}

const activeFlags = computed(() => {
  const v = latestVerification.value
  if (!v) return []
  return Object.entries(FLAG_LABELS)
    .filter(([key]) => v[key as keyof VerificationFlagging])
    .map(([, label]) => label)
})
</script>
