<template>
  <article
    class="exp-card"
    role="button"
    tabindex="0"
    :aria-label="`View details for ${expenditure.line_item_snapshot.program_name}`"
    @keydown.enter="$emit('click')"
  >
    <!-- Top section -->
    <div class="px-[18px] pt-[18px] pb-[14px] border-b border-[--line]">
      <div :class="['tag', tagCls]">{{ tagLabel }}</div>
      <h3 class="font-display text-[16px] font-semibold text-[--ink] leading-[1.3] mb-1.5">
        {{ expenditure.line_item_snapshot.program_name }}
      </h3>
      <p class="text-[11px] text-[--ink-3] flex items-center flex-wrap gap-1">
        <span>{{ expenditure.submitted_by_snapshot.barangay ?? expenditure.submitted_by_snapshot.position }}</span>
        <span class="text-[--line-2]">·</span>
        <span>{{ expenditure.submitted_by_snapshot.full_name }}</span>
        <span class="text-[--line-2]">·</span>
        <span>{{ expenditure.line_item_snapshot.fiscal_year }}</span>
      </p>
    </div>

    <!-- Body -->
    <div class="px-[18px] py-[14px]">
      <div class="flex items-end justify-between mb-2.5">
        <div>
          <p class="text-[9px] font-bold uppercase tracking-[.07em] text-[--ink-4] mb-0.5">Total Claimed</p>
          <p class="font-mono text-[22px] font-medium text-[--ink] leading-none">
            {{ fmt.currency(expenditure.total_amount_spent) }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-[9px] font-bold uppercase tracking-[.07em] text-[--ink-4] mb-0.5">Budget</p>
          <p class="font-mono text-[13px] text-[--ink-3]">
            {{ fmt.currency(expenditure.line_item_snapshot.budget_allocation) }}
          </p>
        </div>
      </div>

      <!-- Progress bar -->
      <div class="h-[5px] rounded-full bg-[--line] overflow-hidden mb-1.5">
        <div
          class="h-full rounded-full transition-[width_.8s_cubic-bezier(.16,1,.3,1)]"
          :class="barCls"
          :style="{ width: `${pctUsed}%` }"
        />
      </div>
      <div class="flex items-center justify-between">
        <span class="text-[10px] text-[--ink-4]">{{ pctUsed }}% of budget utilised</span>
        <span class="inline-flex items-center gap-1 text-[10px] font-semibold text-[--ink-3]
                     bg-[--canvas] border border-[--line] rounded-full px-2 py-0.5">
          <FileText :size="9" />
          {{ expenditure.particulars?.length ?? 0 }} item{{ (expenditure.particulars?.length ?? 0) !== 1 ? 's' : '' }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { FileText } from 'lucide-vue-next'
import type { Expenditure } from '~/types/expenditure'

const props = defineProps<{ expenditure: Expenditure }>()
defineEmits(['click'])

const fmt = useFormatters()

const pctUsed = computed(() =>
  fmt.budgetPercent(
    props.expenditure.total_amount_spent,
    props.expenditure.line_item_snapshot.budget_allocation,
  ),
)

const tagCls = computed(() => {
  const m: Record<string, string> = {
    Verified:   'tag-v',
    Flagged:    'tag-f',
    Unverified: 'tag-p',
  }
  return m[props.expenditure.status] ?? 'tag-p'
})

const tagLabel = computed(() =>
  props.expenditure.status === 'Unverified' ? 'Pending Review' : props.expenditure.status,
)

const barCls = computed(() => {
  if (props.expenditure.status === 'Flagged') return 'bg-[--red]'
  if (pctUsed.value >= 90) return 'bg-[--amber]'
  return 'bg-[--green]'
})
</script>

<style scoped>
.exp-card {
  background: var(--white);
  border: 1px solid var(--line);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow .18s, transform .18s, border-color .18s;
  animation: rise .38s cubic-bezier(.16,1,.3,1) both;
}
.exp-card:hover {
  box-shadow: 0 8px 36px rgba(10,15,46,.09);
  transform: translateY(-2px);
  border-color: var(--blue-mid);
}
.exp-card:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(18,69,200,.25);
}

/* Status tags */
.tag {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .07em; padding: 3px 9px; border-radius: 99px;
  margin-bottom: 10px;
}
.tag-v { background: var(--green-lt); color: var(--green); }
.tag-p { background: var(--amber-lt); color: var(--amber); }
.tag-f { background: var(--red-lt);   color: var(--red);   }

@keyframes rise {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0);    }
}
</style>
