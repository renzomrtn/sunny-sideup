<template>
  <div class="min-h-screen flex flex-col bg-[--canvas]">

    <!-- ── Topbar ── -->
    <header class="bg-white border-b border-[--line] sticky top-0 z-50">
      <div class="max-w-[1120px] mx-auto px-6 flex items-center h-[62px] gap-5">

        <!-- Brand -->
        <NuxtLink to="/" class="flex items-center gap-2.5 shrink-0">
          <div class="w-9 h-9 rounded-[9px] bg-[--blue] flex items-center justify-center">
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
              <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="leading-tight">
            <p class="font-display text-[15px] font-bold text-[--ink]">Youth Transparency Portal</p>
            <p class="text-[10px] font-medium text-[--ink-3] tracking-[.02em]">Sangguniang Kabataan · Naga City</p>
          </div>
        </NuxtLink>

        <!-- Nav -->
        <nav class="hidden md:flex items-center gap-0.5 ml-auto">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-1.5 text-[13px] font-medium text-[--ink-3] px-3 py-1.5
                   rounded-lg transition-all duration-100 hover:bg-[--blue-lt] hover:text-[--blue]"
            active-class="!bg-[--blue] !text-white !font-semibold"
            exact-active-class="!bg-[--blue] !text-white !font-semibold"
          >
            <component :is="item.icon" :size="13" />
            {{ item.label }}
          </NuxtLink>
        </nav>

        <!-- Mobile hamburger -->
        <button class="md:hidden ml-auto p-2 rounded-lg text-[--ink-3] hover:bg-[--blue-lt]" @click="mobileOpen = !mobileOpen">
          <svg v-if="!mobileOpen" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
          <svg v-else              width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Mobile drawer -->
      <Transition name="slide-down">
        <div v-if="mobileOpen" class="md:hidden border-t border-[--line] bg-white px-4 py-3 space-y-1">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium
                   text-[--ink-3] hover:bg-[--blue-lt] hover:text-[--blue] transition-all"
            active-class="!bg-[--blue] !text-white"
            @click="mobileOpen = false"
          >
            <component :is="item.icon" :size="15" />
            {{ item.label }}
          </NuxtLink>
        </div>
      </Transition>
    </header>

    <!-- ── Slot ── -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- ── Footer ── -->
    <footer class="bg-[--ink] text-white/40">
      <div class="max-w-[1120px] mx-auto px-6 py-10 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <div class="flex items-center gap-2 text-white/80 font-semibold text-sm mb-2">
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
              <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Youth Transparency Portal
          </div>
          <p class="text-[11px] text-white/35 leading-relaxed">Sangguniang Kabataan Federation<br/>City of Naga, Camarines Sur</p>
        </div>
        <div>
          <p class="text-[10px] font-bold uppercase tracking-widest text-white/25 mb-3">Navigate</p>
          <div class="space-y-2">
            <NuxtLink v-for="item in navItems" :key="item.to" :to="item.to"
              class="block text-xs text-white/40 hover:text-white transition-colors">
              {{ item.label }}
            </NuxtLink>
          </div>
        </div>
        <div>
          <p class="text-[10px] font-bold uppercase tracking-widest text-white/25 mb-3">Contact</p>
          <div class="space-y-2 text-xs">
            <a href="mailto:skfednaga@gmail.com" class="block text-white/40 hover:text-white transition-colors">skfednaga@gmail.com</a>
            <a href="#" class="block text-white/40 hover:text-white transition-colors">Facebook Page</a>
            <a href="#" class="block text-white/40 hover:text-white transition-colors">Privacy Policy</a>
          </div>
        </div>
      </div>
      <div class="border-t border-white/8 py-4 px-6">
        <p class="max-w-[1120px] mx-auto text-[11px] text-white/20">
          © 2026 Youth Transparency Portal. All rights reserved. Data published in accordance with RA 10742 (SK Reform Act of 2015).
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { Home, ClipboardList } from 'lucide-vue-next'

const mobileOpen = ref(false)

const navItems = [
  { to: '/',                     label: 'Home',              icon: Home          },
  { to: '/verified-expenses',    label: 'Verified Expenses', icon: ClipboardList },
]
</script>

<style>
:root {
  --ink:      #0A0F1E;
  --ink-2:    #2D3552;
  --ink-3:    #5A6282;
  --ink-4:    #94A0BE;
  --canvas:   #F7F9FC;
  --white:    #FFFFFF;
  --line:     #E4E8F2;
  --line-2:   #CDD3E8;
  --blue:     #1245C8;
  --blue-dk:  #0C328A;
  --blue-lt:  #EEF3FF;
  --blue-mid: #C5D3F7;
  --green:    #0E7C5F;
  --green-lt: #EDFAF5;
  --amber:    #B45309;
  --amber-lt: #FFF8ED;
  --red:      #B91C1C;
  --red-lt:   #FFF1F1;
}

.font-display { font-family: 'Source Sans 3', system-ui, sans-serif; }
.font-mono    { font-family: 'DM Mono', 'Courier New', monospace; }

/* page transition */
.page-enter-active, .page-leave-active { transition: opacity .2s, transform .2s; }
.page-enter-from { opacity: 0; transform: translateY(5px); }
.page-leave-to   { opacity: 0; }

/* mobile nav */
.slide-down-enter-active, .slide-down-leave-active { transition: all .2s; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
