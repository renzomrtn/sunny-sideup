<template>
  <div class="min-h-screen bg-[--color-surface] flex flex-col md:flex-row">

    <!-- ── Desktop Sidebar ──────────────────────────────────────────────── -->
    <aside
      class="hidden md:flex flex-col w-64 shrink-0 bg-white border-r border-[--color-border]
             sticky top-0 h-screen overflow-y-auto z-30"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-5 py-5 border-b border-[--color-border]">
        <div
          class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
          style="background: var(--color-primary)"
        >
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
            <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="leading-tight">
          <p class="text-[13px] font-bold text-[--color-ink] leading-none">Expense Verification</p>
          <p class="text-[11px] text-[--color-ink-muted] mt-0.5">SK Federation · Naga City</p>
        </div>
      </div>

      <!-- Nav links -->
      <nav class="flex-1 px-3 py-4 space-y-1">
        <p class="px-3 mb-2 text-[10px] font-bold uppercase tracking-widest text-gray-400">Overview</p>

        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                 text-[--color-ink-muted] transition-all duration-150
                 hover:bg-[--color-surface] hover:text-[--color-ink]"
          active-class="!bg-[--color-primary-lt] !text-[--color-primary] font-semibold"
        >
          <component :is="item.icon" :size="17" class="shrink-0" />
          <span>{{ item.label }}</span>
          <span
            v-if="item.badge"
            class="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded-full"
            :class="item.badgeClass"
          >{{ item.badge }}</span>
        </NuxtLink>

        <div class="pt-3 mt-3 border-t border-[--color-border]">
          <p class="px-3 mb-2 text-[10px] font-bold uppercase tracking-widest text-gray-400">Actions</p>
          <NuxtLink
            to="/expenditures/verify"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                   text-[--color-ink-muted] transition-all hover:bg-[--color-surface] hover:text-[--color-ink]"
            active-class="!bg-[--color-primary-lt] !text-[--color-primary] font-semibold"
          >
            <ShieldCheck :size="17" class="shrink-0" />
            <span>Verify Expenditure</span>
          </NuxtLink>
          <NuxtLink
            to="/expenditures/corrections"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                   text-[--color-ink-muted] transition-all hover:bg-[--color-surface] hover:text-[--color-ink]"
            active-class="!bg-[--color-primary-lt] !text-[--color-primary] font-semibold"
          >
            <Pencil :size="17" class="shrink-0" />
            <span>Corrections Log</span>
          </NuxtLink>
        </div>
      </nav>

      <!-- User chip -->
      <div class="px-3 pb-4">
        <div class="flex items-center gap-2.5 p-3 rounded-xl bg-[--color-surface] border border-[--color-border]">
          <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold shrink-0">AU</div>
          <div class="leading-tight min-w-0">
            <p class="text-xs font-semibold text-[--color-ink] truncate">Admin User</p>
            <p class="text-[10px] text-[--color-ink-muted]">SK Auditor</p>
          </div>
          <button class="ml-auto text-gray-400 hover:text-[--color-ink] transition-colors">
            <LogOut :size="14" />
          </button>
        </div>
      </div>
    </aside>

    <!-- ── Main content ──────────────────────────────────────────────────── -->
    <div class="flex-1 flex flex-col min-w-0">

      <!-- Mobile topbar -->
      <header
        class="md:hidden flex items-center justify-between px-4 py-3
               bg-white border-b border-[--color-border] sticky top-0 z-20"
      >
        <div class="flex items-center gap-2">
          <div
            class="w-7 h-7 rounded-lg flex items-center justify-center"
            style="background: var(--color-primary)"
          >
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
              <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="text-sm font-bold text-[--color-ink]">Expense Verification</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="w-8 h-8 rounded-full bg-[--color-surface] flex items-center justify-center">
            <Bell :size="16" class="text-[--color-ink-muted]" />
          </button>
          <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-[10px] font-bold">AU</div>
        </div>
      </header>

      <!-- Page slot -->
      <main class="flex-1 pb-20 md:pb-0">
        <slot />
      </main>
    </div>

    <!-- ── Mobile Bottom Nav ─────────────────────────────────────────────── -->
    <nav class="bottom-nav h-16 safe-bottom">
      <NuxtLink
        v-for="item in mobileNav"
        :key="item.to"
        :to="item.to"
        class="flex flex-col items-center justify-center gap-0.5 px-3 py-2 rounded-xl
               text-[--color-ink-muted] transition-all"
        active-class="!text-[--color-primary]"
      >
        <component :is="item.icon" :size="20" />
        <span class="text-[10px] font-semibold">{{ item.label }}</span>
      </NuxtLink>
    </nav>

  </div>
</template>

<script setup lang="ts">
import {
  LayoutDashboard, ClipboardList, ShieldCheck,
  Pencil, Bell, LogOut, FolderOpen, Flag,
} from 'lucide-vue-next'

const navItems = [
  { to: '/',                   label: 'Dashboard',         icon: LayoutDashboard, badge: null,  badgeClass: '' },
  { to: '/expenditures',       label: 'All Expenditures',  icon: ClipboardList,   badge: null,  badgeClass: '' },
  { to: '/expenditures/pending', label: 'Pending Review',  icon: FolderOpen,      badge: '3',   badgeClass: 'bg-pending-light text-pending' },
  { to: '/expenditures/flagged', label: 'Flagged',         icon: Flag,            badge: '1',   badgeClass: 'bg-flagged-light text-flagged' },
]

const mobileNav = [
  { to: '/',                     label: 'Home',    icon: LayoutDashboard },
  { to: '/expenditures',         label: 'Records', icon: ClipboardList   },
  { to: '/expenditures/pending', label: 'Pending', icon: FolderOpen      },
  { to: '/expenditures/verify',  label: 'Verify',  icon: ShieldCheck     },
  { to: '/expenditures/flagged', label: 'Flagged', icon: Flag            },
]
</script>
