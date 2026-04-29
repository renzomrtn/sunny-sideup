<template>
  <div>
    <!-- ── Hero ── -->
    <section class="hero-band">
      <div class="max-w-[1120px] mx-auto px-6 py-11 relative z-10">
        <div class="hero-eyebrow animate-[heroIn_.45s_ease_both]">
          <CheckCircle :size="11" />
          Verified Expenses
        </div>
        <h1 class="font-display text-[clamp(28px,4.5vw,46px)] font-bold leading-[1.12]
                   tracking-[-0.015em] text-white mb-3 animate-[heroIn_.45s_.08s_ease_both]">
          Where does the<br class="hidden sm:block" /> SK budget go?
        </h1>
        <p class="text-[14px] text-white/65 max-w-[520px] leading-relaxed
                  animate-[heroIn_.45s_.15s_ease_both]">
          All verified expenditures from the SK Federation and all barangay SK councils —
          publicly disclosed for full accountability under the Mandatory Youth Development Fund.
        </p>
      </div>
    </section>

    <!-- ── Filter bar ── -->
    <div class="bg-white border-b border-[--line] sticky top-[62px] z-40">
      <div class="max-w-[1120px] mx-auto px-6 py-2.5 flex items-center gap-2.5 flex-wrap">
        <div class="relative flex-1 min-w-[180px]">
          <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-[--ink-4] pointer-events-none" />
          <input
            v-model="searchQ"
            class="w-full pl-8 pr-3 py-2 border-[1.5px] border-[--line-2] rounded-[10px]
                   text-[13px] text-[--ink] bg-[--canvas] outline-none
                   focus:border-[--blue] focus:shadow-[0_0_0_3px_rgba(18,69,200,.1)]
                   focus:bg-white transition-all duration-100"
            placeholder="Search program, barangay, or submitter…"
          />
        </div>
        <select
          v-model="sortBy"
          class="ml-auto px-2.5 py-1.5 border-[1.5px] border-[--line-2] rounded-[10px]
                 text-[12px] text-[--ink-2] bg-white outline-none cursor-pointer focus:border-[--blue]"
        >
          <option value="date">Newest first</option>
          <option value="amt-d">Highest amount</option>
          <option value="amt-a">Lowest amount</option>
        </select>
      </div>
    </div>

    <!-- ── Loading / Error / Empty ── -->
    <div class="max-w-[1120px] mx-auto px-6 py-7 pb-20">
      <div v-if="loading" class="text-center py-16 text-[--ink-4]">
        <div class="w-8 h-8 border-2 border-[--blue] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p class="text-[13px]">Loading published expenditures…</p>
      </div>

      <div v-else-if="error" class="text-center py-16">
        <AlertCircle :size="36" class="mx-auto mb-3 text-red-400" />
        <p class="font-semibold text-[--ink-2] mb-1">Could not load data</p>
        <p class="text-[13px] text-[--ink-4]">{{ error }}</p>
        <button @click="reload" class="mt-4 px-4 py-2 text-[13px] bg-[--blue] text-white rounded-[8px]">Retry</button>
      </div>

      <template v-else>
        <p class="text-[12px] text-[--ink-4] font-medium mb-4">
          <strong class="text-[--ink-2]">{{ filtered.length }}</strong>
          publication{{ filtered.length !== 1 ? 's' : '' }} found
        </p>

        <div v-if="filtered.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <article
            v-for="(pub, i) in filtered"
            :key="pub.publication_id"
            class="pub-card"
            :style="{ animationDelay: `${i * 0.05}s` }"
            @click="selectedPub = pub"
          >
            <div class="px-[18px] pt-[18px] pb-[14px] border-b border-[--line]">
              <div class="tag tag-v">Published</div>
              <h3 class="font-display text-[16px] font-semibold text-[--ink] leading-[1.3] mb-1.5">
                {{ pub.content_snapshot.title || pub.content_snapshot.program_name || 'Untitled' }}
              </h3>
              <p class="text-[11px] text-[--ink-3] flex items-center flex-wrap gap-1">
                <span>{{ pub.content_snapshot.barangay || '—' }}</span>
                <span class="text-[--line-2]">·</span>
                <span>{{ pub.content_snapshot.fiscal_year || '—' }}</span>
              </p>
            </div>
            <div class="px-[18px] py-[14px]">
              <div class="flex items-end justify-between mb-2.5">
                <div>
                  <p class="text-[9px] font-bold uppercase tracking-[.07em] text-[--ink-4] mb-0.5">Total Claimed</p>
                  <p class="font-mono text-[22px] font-medium text-[--ink] leading-none">
                    {{ fmt(pub.content_snapshot.total_amount_spent) }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-[9px] font-bold uppercase tracking-[.07em] text-[--ink-4] mb-0.5">Budget</p>
                  <p class="font-mono text-[13px] text-[--ink-3]">
                    {{ fmt(pub.content_snapshot.budget_allocation) }}
                  </p>
                </div>
              </div>
              <p class="text-[11px] text-[--ink-4] mt-1">
                Published {{ fmtDate(pub.published_at) }}
              </p>
            </div>
          </article>
        </div>

        <div v-else class="text-center py-16 text-[--ink-4]">
          <SearchX :size="36" class="mx-auto mb-3 opacity-30" />
          <p class="font-display text-[19px] font-semibold text-[--ink-2] mb-1">No results found</p>
          <p class="text-[13px]">Try adjusting your search or check back later.</p>
        </div>
      </template>
    </div>

    <!-- ── Detail drawer ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="selectedPub" class="fixed inset-0 bg-[#080C24]/50 z-[200] backdrop-blur-[3px]" @click="selectedPub = null" />
      </Transition>
      <Transition name="slide-right">
        <aside v-if="selectedPub" class="fixed right-0 top-0 bottom-0 z-[201] bg-white flex flex-col" style="width: min(600px, 100vw)">
          <div class="px-6 py-5 border-b border-[--line] flex items-start gap-3 flex-shrink-0">
            <div class="flex-1 min-w-0">
              <h2 class="font-display text-[20px] font-bold text-[--ink] leading-[1.25] mb-1">
                {{ selectedPub.content_snapshot.title || selectedPub.content_snapshot.program_name || 'Untitled' }}
              </h2>
              <p class="text-[12px] text-[--ink-3]">
                {{ selectedPub.content_snapshot.barangay || '—' }} · {{ selectedPub.content_snapshot.fiscal_year || '—' }}
              </p>
            </div>
            <button
              class="w-[34px] h-[34px] rounded-[9px] border-[1.5px] border-[--line] bg-none
                     flex items-center justify-center text-[--ink-3] flex-shrink-0
                     hover:bg-[--canvas] hover:text-[--ink] transition-all"
              @click="selectedPub = null"
            ><X :size="16" /></button>
          </div>

          <div class="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            <!-- Summary -->
            <div v-if="selectedPub.content_snapshot.summary" class="text-[13px] text-[--ink-2] leading-relaxed bg-[--canvas] rounded-[10px] p-4 border border-[--line]">
              {{ selectedPub.content_snapshot.summary }}
            </div>

            <!-- Meta grid -->
            <dl class="grid grid-cols-2 gap-3">
              <div>
                <dt class="field-label">Submitted By</dt>
                <dd class="field-val">{{ selectedPub.content_snapshot.submitted_by || '—' }}</dd>
              </div>
              <div>
                <dt class="field-label">Barangay / Unit</dt>
                <dd class="field-val">{{ selectedPub.content_snapshot.barangay || '—' }}</dd>
              </div>
              <div>
                <dt class="field-label">Total Amount Claimed</dt>
                <dd class="field-val font-mono text-[16px]">{{ fmt(selectedPub.content_snapshot.total_amount_spent) }}</dd>
              </div>
              <div>
                <dt class="field-label">Budget Allocation</dt>
                <dd class="field-val font-mono text-[16px] !text-[--ink-3]">{{ fmt(selectedPub.content_snapshot.budget_allocation) }}</dd>
              </div>
              <div>
                <dt class="field-label">Published</dt>
                <dd class="field-val">{{ fmtDate(selectedPub.published_at) }}</dd>
              </div>
              <div v-if="selectedPub.ref_expenditure_id">
                <dt class="field-label">Expenditure Ref</dt>
                <dd class="field-val">#{{ selectedPub.ref_expenditure_id }}</dd>
              </div>
            </dl>

            <!-- Particulars if present -->
            <section v-if="selectedPub.content_snapshot.particulars?.length">
              <h3 class="section-title">Expense Particulars ({{ selectedPub.content_snapshot.particulars.length }})</h3>
              <div class="space-y-2.5">
                <div
                  v-for="(p, idx) in selectedPub.content_snapshot.particulars"
                  :key="idx"
                  class="border border-[--line] rounded-[12px] p-[13px] bg-[--canvas]"
                >
                  <div class="flex items-start justify-between gap-2.5 mb-1">
                    <div>
                      <p class="text-[13px] font-semibold text-[--ink]">{{ p.particular_name }}</p>
                      <p v-if="p.vendor_name" class="text-[11px] text-[--ink-3] mt-0.5">{{ p.vendor_name }}</p>
                    </div>
                    <p class="font-mono text-[14px] font-medium text-[--ink] flex-shrink-0">{{ fmt(p.amount_claimed) }}</p>
                  </div>
                  <p class="text-[11px] text-[--ink-4]">{{ p.date_of_expense || '—' }}</p>
                </div>
              </div>
            </section>

            <div class="flex items-start gap-2.5 bg-[--blue-lt] border border-[--blue-mid] rounded-[10px] p-3">
              <Info :size="13" class="text-[--blue-dk] flex-shrink-0 mt-0.5" />
              <p class="text-[11px] text-[--blue-dk] leading-relaxed">
                All data is sourced from the official records of the SK Federation of Naga City
                and verified by an authorized SK Auditor before publication.
              </p>
            </div>
          </div>
        </aside>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { CheckCircle, Search, SearchX, X, AlertCircle, Info } from 'lucide-vue-next'
import type { PublishedExpenditure } from '~/composables/usePortalApi'

definePageMeta({ layout: 'portal' })
useHead({ title: 'Verified Expenses — Youth Transparency Portal' })

const { fetchPublished } = usePortalApi()

const publications = ref<PublishedExpenditure[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQ = ref('')
const sortBy = ref<'date' | 'amt-d' | 'amt-a'>('date')
const selectedPub = ref<PublishedExpenditure | null>(null)

async function reload() {
  loading.value = true
  error.value = null
  try {
    publications.value = await fetchPublished()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }; message?: string }
    error.value = err?.data?.detail || err?.message || 'Failed to load'
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  const q = searchQ.value.toLowerCase()
  let list = publications.value.filter(pub => {
    if (!q) return true
    const snap = pub.content_snapshot
    return [
      snap.title, snap.program_name, snap.barangay, snap.submitted_by, String(snap.fiscal_year ?? '')
    ].some(s => s?.toLowerCase().includes(q))
  })
  if (sortBy.value === 'amt-d') list = [...list].sort((a, b) => (b.content_snapshot.total_amount_spent ?? 0) - (a.content_snapshot.total_amount_spent ?? 0))
  if (sortBy.value === 'amt-a') list = [...list].sort((a, b) => (a.content_snapshot.total_amount_spent ?? 0) - (b.content_snapshot.total_amount_spent ?? 0))
  return list
})

function fmt(val?: number | null) {
  return new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(val || 0)
}

function fmtDate(d?: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(reload)
</script>

<style scoped>
.hero-band {
  background: linear-gradient(135deg, #08165A 0%, #1245C8 55%, #2563EB 100%);
  position: relative; overflow: hidden;
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22);
  border-radius: 99px; padding: 4px 13px;
  font-size: 10px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  color: rgba(255,255,255,.85); margin-bottom: 16px;
}
@keyframes heroIn {
  from { opacity: 0; transform: translateY(7px); }
  to   { opacity: 1; transform: translateY(0); }
}

.pub-card {
  background: var(--white); border: 1px solid var(--line); border-radius: 20px;
  overflow: hidden; cursor: pointer;
  transition: box-shadow .18s, transform .18s, border-color .18s;
  animation: rise .38s cubic-bezier(.16,1,.3,1) both;
}
.pub-card:hover { box-shadow: 0 8px 36px rgba(10,15,46,.09); transform: translateY(-2px); border-color: var(--blue-mid); }
.tag { display: inline-flex; align-items: center; gap: 5px; font-size: 10px; font-weight: 700;
       text-transform: uppercase; letter-spacing: .07em; padding: 3px 9px; border-radius: 99px; margin-bottom: 10px; }
.tag-v { background: var(--green-lt); color: var(--green); }

.field-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--ink-4); margin-bottom: 3px; }
.field-val   { font-size: 13px; font-weight: 600; color: var(--ink); }
.section-title { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .09em; color: var(--ink-4);
                 padding-bottom: 8px; border-bottom: 1px solid var(--line); margin-bottom: 12px; }

.fade-enter-active, .fade-leave-active { transition: opacity .22s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-right-enter-active, .slide-right-leave-active { transition: transform .3s cubic-bezier(.16,1,.3,1); }
.slide-right-enter-from, .slide-right-leave-to { transform: translateX(100%); }

@keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
