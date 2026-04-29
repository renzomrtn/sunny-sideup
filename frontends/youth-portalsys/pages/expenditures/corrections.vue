<template>
  <div class="px-4 md:px-8 py-6 space-y-5 max-w-3xl mx-auto">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-[--color-primary-lt] flex items-center justify-center">
        <Pencil :size="18" class="text-[--color-primary]" />
      </div>
      <div>
        <h1 class="text-xl font-extrabold text-[--color-ink] tracking-tight">Corrections Log</h1>
        <p class="text-xs text-[--color-ink-muted]">Immutable audit trail of all corrections submitted</p>
      </div>
    </div>

    <!-- Info banner -->
    <div class="rounded-2xl border border-[--color-primary]/20 bg-[--color-primary-lt] px-4 py-3 flex items-start gap-2.5">
      <Info :size="15" class="text-[--color-primary] mt-0.5 shrink-0" />
      <p class="text-xs text-[--color-primary] leading-relaxed">
        Correction records are append-only and cannot be edited or deleted.
        Each correction references the original flagged particular and verification record.
      </p>
    </div>

    <!-- Empty state -->
    <div class="card p-10 text-center">
      <FileText :size="32" class="mx-auto text-gray-300 mb-3" />
      <p class="text-sm font-semibold text-[--color-ink]">No corrections yet</p>
      <p class="text-xs text-[--color-ink-muted] mt-1">
        Corrections will appear here once submitters respond to flagged particulars.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Pencil, Info, FileText } from 'lucide-vue-next'
definePageMeta({ layout: 'default' })
</script>
