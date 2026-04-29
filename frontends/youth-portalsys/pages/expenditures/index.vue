<template>
  <div class="px-4 md:px-8 py-6 space-y-5 max-w-5xl mx-auto">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-extrabold text-[--color-ink] tracking-tight">All Expenditures</h1>
        <p class="text-xs text-[--color-ink-muted] mt-0.5">{{ filtered.length }} records</p>
      </div>
    </div>

    <!-- Search + Filter bar -->
    <div class="flex flex-col sm:flex-row gap-2">
      <div class="relative flex-1">
        <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          v-model="search"
          class="input pl-9 text-sm"
          placeholder="Search by program or submitter…"
        />
      </div>
      <div class="flex gap-2">
        <button
          v-for="s in statusFilters"
          :key="s.value"
          class="btn btn-outline btn-sm"
          :class="{ '!bg-[--color-primary-lt] !border-[--color-primary]/50 !text-[--color-primary]': activeFilter === s.value }"
          @click="activeFilter = activeFilter === s.value ? '' : s.value"
        >
          {{ s.label }}
        </button>
      </div>
    </div>

    <!-- List -->
    <div v-if="filtered.length" class="space-y-3">
      <ExpenditureExpenditureCard
        v-for="exp in filtered"
        :key="exp.expenditure_id"
        :expenditure="exp"
      />
    </div>
    <div v-else class="card p-10 text-center text-[--color-ink-muted] text-sm">
      No expenditures match your filters.
    </div>

  </div>
</template>

<script setup lang="ts">
import { Search } from 'lucide-vue-next'
import type { ExpenditureStatus } from '~/types/expenditure'

definePageMeta({ layout: 'default' })

const { expenditures } = useMockData()

const search      = ref('')
const activeFilter = ref<ExpenditureStatus | ''>('')

const statusFilters = [
  { value: 'Unverified', label: 'Pending' },
  { value: 'Verified',   label: 'Verified' },
  { value: 'Flagged',    label: 'Flagged'  },
]

const filtered = computed(() =>
  expenditures.filter(e => {
    const matchStatus = !activeFilter.value || e.status === activeFilter.value
    const q = search.value.toLowerCase()
    const matchSearch =
      !q ||
      e.line_item_snapshot.program_name.toLowerCase().includes(q) ||
      e.submitted_by_snapshot.full_name.toLowerCase().includes(q)
    return matchStatus && matchSearch
  }),
)
</script>
