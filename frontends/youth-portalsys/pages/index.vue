<template>
  <div class="px-4 md:px-8 py-6 space-y-6 max-w-5xl mx-auto">

    <!-- Page header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-extrabold text-[--color-ink] tracking-tight">Dashboard</h1>
        <p class="text-xs text-[--color-ink-muted] mt-0.5">Expense Verification · FY {{ currentYear }}</p>
      </div>
      <NuxtLink to="/expenditures/pending" class="btn btn-primary btn-sm">
        <ShieldCheck :size="14" />
        Review Queue
      </NuxtLink>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <UiStatCard
        label="Total Expenditures"
        :value="stats.total"
        :icon="ClipboardList"
        color="#1A56DB"
      />
      <UiStatCard
        label="Pending Review"
        :value="stats.pending"
        sub="Awaiting verification"
        :icon="Clock"
        color="#D97706"
      />
      <UiStatCard
        label="Verified"
        :value="stats.verified"
        :icon="CheckCircle"
        color="#0D9488"
      />
      <UiStatCard
        label="Flagged"
        :value="stats.flagged"
        sub="Needs attention"
        :icon="Flag"
        color="#DC2626"
      />
    </div>

    <!-- Total budget utilisation -->
    <div class="card p-5 animate-fade-in">
      <div class="flex items-center justify-between mb-3">
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-[--color-ink-muted]">Budget Utilisation</p>
          <p class="text-2xl font-extrabold mono text-[--color-ink] mt-0.5">
            {{ fmt.currency(totalSpent) }}
          </p>
          <p class="text-xs text-[--color-ink-muted]">of {{ fmt.currency(totalBudget) }} total budget</p>
        </div>
        <div
          class="w-14 h-14 rounded-2xl flex items-center justify-center text-lg font-extrabold mono"
          :class="utilPct >= 90 ? 'bg-flagged-light text-flagged' : 'bg-verified-light text-verified'"
        >
          {{ utilPct }}%
        </div>
      </div>
      <div class="h-2.5 rounded-full bg-[--color-surface] overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-1000"
          :class="utilPct >= 90 ? 'bg-flagged' : 'bg-verified'"
          :style="{ width: `${utilPct}%` }"
        />
      </div>
    </div>

    <!-- Recent expenditures -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-bold text-[--color-ink]">Recent Submissions</h2>
        <NuxtLink to="/expenditures" class="text-xs font-semibold text-[--color-primary] hover:underline">View all</NuxtLink>
      </div>
      <div class="space-y-3">
        <ExpenditureExpenditureCard
          v-for="exp in recentExpenditures"
          :key="exp.expenditure_id"
          :expenditure="exp"
        />
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ClipboardList, Clock, CheckCircle, Flag, ShieldCheck } from 'lucide-vue-next'

definePageMeta({ layout: 'default' })

const fmt = useFormatters()
const { expenditures } = useMockData()

const currentYear = new Date().getFullYear()

const stats = computed(() => ({
  total:   expenditures.length,
  pending: expenditures.filter(e => e.status === 'Unverified').length,
  verified: expenditures.filter(e => e.status === 'Verified').length,
  flagged: expenditures.filter(e => e.status === 'Flagged').length,
}))

const totalSpent  = computed(() => expenditures.reduce((s, e) => s + e.total_amount_spent, 0))
const totalBudget = computed(() => expenditures.reduce((s, e) => s + e.line_item_snapshot.budget_allocation, 0))
const utilPct     = computed(() => fmt.budgetPercent(totalSpent.value, totalBudget.value))

const recentExpenditures = computed(() => expenditures.slice(0, 4))
</script>
