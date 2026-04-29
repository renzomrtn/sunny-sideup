<template>
  <!-- Overlay -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 bg-[#080C24]/50 z-[200] backdrop-blur-[3px]"
        @click="$emit('close')"
      />
    </Transition>

    <!-- Drawer -->
    <Transition name="slide-right">
      <aside
        v-if="open && expenditure"
        class="fixed right-0 top-0 bottom-0 z-[201] bg-white flex flex-col"
        style="width: min(600px, 100vw)"
      >
        <!-- Head -->
        <div class="px-6 py-5 border-b border-[--line] flex items-start gap-3 flex-shrink-0">
          <div class="flex-1 min-w-0">
            <h2 class="font-display text-[20px] font-bold text-[--ink] leading-[1.25] mb-1">
              {{ expenditure.line_item_snapshot.program_name }}
            </h2>
            <p class="text-[12px] text-[--ink-3]">
              {{ expenditure.submitted_by_snapshot.barangay ?? expenditure.submitted_by_snapshot.position }}
              · {{ expenditure.line_item_snapshot.fiscal_year }}
            </p>
          </div>
          <button
            class="w-[34px] h-[34px] rounded-[9px] border-[1.5px] border-[--line] bg-none
                   flex items-center justify-center text-[--ink-3] flex-shrink-0
                   hover:bg-[--canvas] hover:text-[--ink] transition-all"
            @click="$emit('close')"
          >
            <X :size="16" />
          </button>
        </div>

        <!-- Scrollable body -->
        <div class="flex-1 overflow-y-auto px-6 py-6 space-y-7">

          <!-- Status + meta -->
          <section>
            <div :class="['inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[.07em] px-2.5 py-1 rounded-full mb-4', tagCls]">
              {{ tagLabel }}
            </div>
            <dl class="grid grid-cols-2 gap-3">
              <div>
                <dt class="field-label">Submitted By</dt>
                <dd class="field-val">{{ expenditure.submitted_by_snapshot.full_name }}</dd>
                <dd class="field-sub">{{ expenditure.submitted_by_snapshot.position }}</dd>
              </div>
              <div>
                <dt class="field-label">Barangay / Unit</dt>
                <dd class="field-val">{{ expenditure.submitted_by_snapshot.barangay ?? '—' }}</dd>
              </div>
              <div>
                <dt class="field-label">Total Amount Claimed</dt>
                <dd class="field-val font-mono text-[16px]">{{ fmt.currency(expenditure.total_amount_spent) }}</dd>
              </div>
              <div>
                <dt class="field-label">Budget Allocation</dt>
                <dd class="field-val font-mono text-[16px] !text-[--ink-3]">{{ fmt.currency(expenditure.line_item_snapshot.budget_allocation) }}</dd>
              </div>
            </dl>

            <!-- Budget bar -->
            <div class="mt-4">
              <div class="flex justify-between text-[10px] text-[--ink-4] mb-1">
                <span>Budget utilisation</span>
                <span class="font-mono font-medium">{{ pct }}%</span>
              </div>
              <div class="h-[7px] rounded-full bg-[--line] overflow-hidden">
                <div
                  class="h-full rounded-full transition-[width_.8s_cubic-bezier(.16,1,.3,1)]"
                  :class="barCls"
                  :style="{ width: `${pct}%` }"
                />
              </div>
            </div>
          </section>

          <!-- Flag notice -->
          <div
            v-if="hasFlaggedParticulars"
            class="flex items-start gap-2.5 bg-[--amber-lt] border border-amber-200 rounded-[10px] p-3"
          >
            <AlertTriangle :size="14" class="text-[--amber] flex-shrink-0 mt-0.5" />
            <p class="text-[11px] text-[--amber] leading-relaxed">
              One or more particulars in this expenditure have been flagged and are pending
              correction by the submitter.
            </p>
          </div>

          <!-- Particulars -->
          <section>
            <h3 class="section-title">
              Expense Particulars
              <span class="ml-1.5 text-[--ink-4] font-medium">({{ expenditure.particulars?.length ?? 0 }})</span>
            </h3>

            <div v-if="expenditure.particulars?.length" class="space-y-2.5">
              <div
                v-for="p in expenditure.particulars"
                :key="p.particular_id"
                class="border border-[--line] rounded-[12px] p-[13px] bg-[--canvas]"
                :class="{ '!border-red-200 !bg-[--red-lt]': p.verifications?.some(v => v.flag_amount || v.flag_particular || v.flag_date || v.flag_attachment || v.flag_vendor) }"
              >
                <!-- Row top -->
                <div class="flex items-start justify-between gap-2.5 mb-1.5">
                  <div class="min-w-0">
                    <p class="text-[13px] font-semibold text-[--ink] leading-snug">{{ p.particular_name }}</p>
                    <p class="text-[11px] text-[--ink-3] mt-0.5">
                      {{ p.vendor?.vendor_name }}
                      <span class="text-[--ink-4]"> · {{ p.vendor?.category }}</span>
                    </p>
                  </div>
                  <p class="font-mono text-[14px] font-medium text-[--ink] flex-shrink-0">
                    {{ fmt.currency(p.amount_claimed) }}
                  </p>
                </div>

                <!-- Meta row -->
                <div class="flex items-center gap-3 text-[11px] text-[--ink-4] flex-wrap">
                  <span class="flex items-center gap-1">
                    <Calendar :size="11" />
                    {{ fmt.date(p.date_of_expense) }}
                  </span>
                  <span
                    class="flex items-center gap-1"
                    :class="p.file_ref_id ? 'text-[--ink-4]' : 'text-[--amber]'"
                  >
                    <component :is="p.file_ref_id ? Paperclip : AlertCircle" :size="11" />
                    {{ p.file_ref_id ? 'OR attached' : 'No receipt' }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="text-[13px] text-[--ink-4] text-center py-6 border border-[--line] rounded-[12px]">
              No particulars submitted yet.
            </div>
          </section>

          <!-- Data notice -->
          <div class="flex items-start gap-2.5 bg-[--blue-lt] border border-[--blue-mid] rounded-[10px] p-3">
            <Info :size="13" class="text-[--blue-dk] flex-shrink-0 mt-0.5" />
            <p class="text-[11px] text-[--blue-dk] leading-relaxed">
              All data is sourced from the official records of the SK Federation of Naga City
              and is verified by an authorized SK Auditor before publication.
            </p>
          </div>

        </div>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { X, AlertTriangle, AlertCircle, Calendar, Paperclip, Info } from 'lucide-vue-next'
import type { Expenditure } from '~/types/expenditure'

const props = defineProps<{
  expenditure: Expenditure | null
  open: boolean
}>()

defineEmits(['close'])

const fmt = useFormatters()

// Lock body scroll when open
watch(() => props.open, v => {
  if (import.meta.client) document.body.style.overflow = v ? 'hidden' : ''
})
onUnmounted(() => {
  if (import.meta.client) document.body.style.overflow = ''
})

const pct = computed(() =>
  props.expenditure
    ? useFormatters().budgetPercent(
        props.expenditure.total_amount_spent,
        props.expenditure.line_item_snapshot.budget_allocation,
      )
    : 0,
)

const tagCls = computed(() => {
  const m: Record<string, string> = {
    Verified:   'bg-[--green-lt] text-[--green]',
    Flagged:    'bg-[--red-lt] text-[--red]',
    Unverified: 'bg-[--amber-lt] text-[--amber]',
  }
  return m[props.expenditure?.status ?? 'Unverified']
})

const tagLabel = computed(() =>
  props.expenditure?.status === 'Unverified' ? 'Pending Review' : (props.expenditure?.status ?? ''),
)

const barCls = computed(() => {
  if (props.expenditure?.status === 'Flagged') return 'bg-[--red]'
  if (pct.value >= 90) return 'bg-[--amber]'
  return 'bg-[--green]'
})

const hasFlaggedParticulars = computed(() =>
  props.expenditure?.particulars?.some(p =>
    p.verifications?.some(v =>
      v.flag_amount || v.flag_particular || v.flag_date || v.flag_attachment || v.flag_vendor
    ),
  ) ?? false,
)
</script>

<style scoped>
.field-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--ink-4); margin-bottom: 3px; }
.field-val   { font-size: 13px; font-weight: 600; color: var(--ink); }
.field-sub   { font-size: 11px; color: var(--ink-3); }

.section-title {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .09em; color: var(--ink-4);
  padding-bottom: 8px; border-bottom: 1px solid var(--line);
  margin-bottom: 12px;
}

.fade-enter-active, .fade-leave-active { transition: opacity .22s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-right-enter-active, .slide-right-leave-active { transition: transform .3s cubic-bezier(.16,1,.3,1); }
.slide-right-enter-from, .slide-right-leave-to { transform: translateX(100%); }
</style>
