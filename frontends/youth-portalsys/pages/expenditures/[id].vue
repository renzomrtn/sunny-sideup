<template>
  <div class="px-4 md:px-8 py-6 space-y-6 max-w-3xl mx-auto">

    <!-- Back -->
    <button class="flex items-center gap-1.5 text-xs font-semibold text-[--color-ink-muted] hover:text-[--color-ink] transition-colors" @click="$router.back()">
      <ArrowLeft :size="14" />
      Back
    </button>

    <!-- Not found -->
    <div v-if="!expenditure" class="card p-10 text-center text-[--color-ink-muted] text-sm">
      Expenditure not found.
    </div>

    <template v-else>

      <!-- Header card -->
      <div class="card p-5 space-y-4 animate-slide-up">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-[10px] font-bold uppercase tracking-widest text-[--color-ink-muted]">Program</p>
            <h1 class="text-lg font-extrabold text-[--color-ink] leading-snug mt-0.5">
              {{ expenditure.line_item_snapshot.program_name }}
            </h1>
          </div>
          <UiStatusBadge :status="expenditure.status" />
        </div>

        <!-- Meta grid -->
        <dl class="grid grid-cols-2 gap-3 text-xs">
          <div>
            <dt class="font-semibold text-[--color-ink-muted] uppercase tracking-widest text-[10px]">Submitted by</dt>
            <dd class="text-[--color-ink] font-semibold mt-0.5">{{ expenditure.submitted_by_snapshot.full_name }}</dd>
            <dd class="text-[--color-ink-muted]">{{ expenditure.submitted_by_snapshot.position }}</dd>
          </div>
          <div>
            <dt class="font-semibold text-[--color-ink-muted] uppercase tracking-widest text-[10px]">Barangay / Unit</dt>
            <dd class="text-[--color-ink] font-semibold mt-0.5">{{ expenditure.submitted_by_snapshot.barangay ?? '—' }}</dd>
          </div>
          <div>
            <dt class="font-semibold text-[--color-ink-muted] uppercase tracking-widest text-[10px]">Total Claimed</dt>
            <dd class="text-[--color-ink] font-bold mono mt-0.5">{{ fmt.currency(expenditure.total_amount_spent) }}</dd>
          </div>
          <div>
            <dt class="font-semibold text-[--color-ink-muted] uppercase tracking-widest text-[10px]">Budget Allocation</dt>
            <dd class="text-[--color-ink] font-bold mono mt-0.5">{{ fmt.currency(expenditure.line_item_snapshot.budget_allocation) }}</dd>
          </div>
        </dl>

        <!-- Budget bar -->
        <div>
          <div class="flex items-center justify-between text-[10px] text-[--color-ink-muted] mb-1">
            <span>Budget utilisation</span>
            <span class="font-bold mono">{{ pct }}%</span>
          </div>
          <div class="h-2 rounded-full bg-[--color-surface] overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :class="pct >= 90 ? 'bg-pending' : 'bg-verified'"
              :style="{ width: `${pct}%` }"
            />
          </div>
        </div>
      </div>

      <!-- Particulars -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-bold text-[--color-ink]">
            Particulars
            <span class="ml-1.5 text-[10px] font-semibold text-[--color-ink-muted]">({{ expenditure.particulars?.length ?? 0 }})</span>
          </h2>
        </div>

        <div class="space-y-3">
          <div
            v-for="p in expenditure.particulars"
            :key="p.particular_id"
            class="animate-fade-in"
          >
            <ExpenditureParticularRow :particular="p">
              <template v-if="expenditure.status === 'Unverified'" #actions>
                <div v-if="activeFlagForm !== p.particular_id" class="flex gap-2">
                  <button
                    class="btn btn-danger btn-sm flex-1"
                    @click="activeFlagForm = p.particular_id"
                  >
                    <Flag :size="13" /> Flag Issues
                  </button>
                  <button
                    class="btn btn-success btn-sm"
                    @click="approveParticular(p.particular_id)"
                  >
                    <Check :size="13" /> OK
                  </button>
                </div>
                <ExpenditureFlagForm
                  v-else
                  @submit="onFlagSubmit(p.particular_id, $event)"
                  @cancel="activeFlagForm = null"
                />
              </template>

              <template v-if="expenditure.status === 'Flagged'" #actions>
                <div v-if="activeCorrectionForm !== p.particular_id">
                  <button
                    class="btn btn-outline btn-sm"
                    @click="activeCorrectionForm = p.particular_id"
                  >
                    <Pencil :size="13" /> Submit Correction
                  </button>
                </div>
                <ExpenditureCorrectionForm
                  v-else
                  @submit="onCorrectionSubmit(p.particular_id, $event)"
                  @cancel="activeCorrectionForm = null"
                />
              </template>
            </ExpenditureParticularRow>
          </div>

          <div v-if="!expenditure.particulars?.length" class="card p-6 text-center text-[--color-ink-muted] text-xs">
            No particulars submitted yet.
          </div>
        </div>
      </div>

      <!-- Final action bar -->
      <div
        v-if="expenditure.status === 'Unverified'"
        class="card p-4 flex flex-col sm:flex-row gap-3 sticky bottom-20 md:bottom-4 shadow-card-md animate-slide-up"
      >
        <div class="flex-1 text-xs text-[--color-ink-muted]">
          <p class="font-semibold text-[--color-ink]">Ready to finalise?</p>
          <p>Mark as Verified only after all particulars have been reviewed.</p>
        </div>
        <div class="flex gap-2 shrink-0">
          <button class="btn btn-danger" @click="markStatus('Flagged')">
            <Flag :size="15" /> Mark Flagged
          </button>
          <button class="btn btn-success" @click="markStatus('Verified')">
            <ShieldCheck :size="15" /> Mark Verified
          </button>
        </div>
      </div>

      <!-- Audit trail toast -->
      <Transition name="slide-fade">
        <div
          v-if="toast"
          class="fixed bottom-24 md:bottom-6 left-1/2 -translate-x-1/2 z-50
                 bg-[--color-ink] text-white text-xs font-semibold px-4 py-2.5
                 rounded-xl shadow-card-md flex items-center gap-2"
        >
          <CheckCircle :size="14" />
          {{ toast }}
        </div>
      </Transition>

    </template>
  </div>
</template>

<script setup lang="ts">
import {
  ArrowLeft, Flag, Check, Pencil, ShieldCheck, CheckCircle,
} from 'lucide-vue-next'
import type { ExpenditureStatus } from '~/types/expenditure'

definePageMeta({ layout: 'default' })

const route = useRoute()
const fmt   = useFormatters()

const { expenditures } = useMockData()

// Find expenditure by ID from route param
const expenditure = computed(() =>
  expenditures.find(e => e.expenditure_id === Number(route.params.id)),
)

const pct = computed(() =>
  expenditure.value
    ? fmt.budgetPercent(
        expenditure.value.total_amount_spent,
        expenditure.value.line_item_snapshot.budget_allocation,
      )
    : 0,
)

// UI state
const activeFlagForm       = ref<number | null>(null)
const activeCorrectionForm = ref<number | null>(null)
const toast                = ref('')

const showToast = (msg: string) => {
  toast.value = msg
  setTimeout(() => (toast.value = ''), 3000)
}

const approveParticular = (id: number) => {
  showToast(`Particular #${id} marked OK`)
}

const onFlagSubmit = (particularId: number, payload: object) => {
  console.log('Flag submitted', particularId, payload)
  activeFlagForm.value = null
  showToast('Flags submitted — expenditure marked Flagged')
}

const onCorrectionSubmit = (particularId: number, payload: object) => {
  console.log('Correction submitted', particularId, payload)
  activeCorrectionForm.value = null
  showToast('Correction recorded successfully')
}

const markStatus = (status: ExpenditureStatus) => {
  console.log('Status update →', status)
  showToast(
    status === 'Verified'
      ? 'Expenditure marked Verified ✓'
      : 'Expenditure marked Flagged — submitter notified',
  )
}
</script>

<style scoped>
.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-fade-enter-from, .slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(8px);
}
</style>
