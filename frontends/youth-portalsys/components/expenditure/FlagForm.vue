<template>
  <div class="space-y-4">
    <p class="text-sm font-semibold text-[--color-ink]">Flag Issues</p>

    <!-- Flag checkboxes -->
    <div class="grid grid-cols-2 gap-2">
      <label
        v-for="(label, key) in FLAGS"
        :key="key"
        class="flex items-center gap-2.5 p-3 rounded-xl border cursor-pointer transition-all duration-150"
        :class="form[key]
          ? 'border-flagged bg-flagged-light'
          : 'border-[--color-border] bg-white hover:border-[--color-ink-muted]/30'"
      >
        <input
          v-model="form[key]"
          type="checkbox"
          class="accent-[--color-flagged] w-4 h-4"
        />
        <span
          class="text-xs font-semibold"
          :class="form[key] ? 'text-flagged' : 'text-[--color-ink-muted]'"
        >
          {{ label }}
        </span>
      </label>
    </div>

    <!-- Remarks -->
    <div>
      <label class="block text-xs font-semibold text-[--color-ink-muted] mb-1.5">
        Remarks <span class="font-normal">(optional)</span>
      </label>
      <textarea
        v-model="form.remarks"
        class="input resize-none text-sm"
        rows="3"
        placeholder="Describe the issue in detail..."
      />
    </div>

    <!-- Submit -->
    <div class="flex gap-2 pt-1">
      <button
        class="btn btn-danger flex-1"
        :disabled="!hasAnyFlag || submitting"
        @click="submit"
      >
        <Flag :size="15" />
        {{ submitting ? 'Submitting…' : 'Submit Flags' }}
      </button>
      <button class="btn btn-ghost" @click="$emit('cancel')">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Flag } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'submit', payload: FlagForm): void
  (e: 'cancel'): void
}>()

interface FlagForm {
  flag_particular: boolean
  flag_amount:     boolean
  flag_date:       boolean
  flag_attachment: boolean
  flag_vendor:     boolean
  remarks:         string
}

const FLAGS: Record<keyof Omit<FlagForm, 'remarks'>, string> = {
  flag_particular: 'Invalid Particular',
  flag_amount:     'Amount Mismatch',
  flag_date:       'Date Issue',
  flag_attachment: 'Missing/Invalid OR',
  flag_vendor:     'Vendor Issue',
}

const submitting = ref(false)
const form = reactive<FlagForm>({
  flag_particular: false,
  flag_amount:     false,
  flag_date:       false,
  flag_attachment: false,
  flag_vendor:     false,
  remarks:         '',
})

const hasAnyFlag = computed(() =>
  Object.keys(FLAGS).some(k => form[k as keyof Omit<FlagForm, 'remarks'>]),
)

const submit = async () => {
  if (!hasAnyFlag.value) return
  submitting.value = true
  await new Promise(r => setTimeout(r, 600)) // sim network
  emit('submit', { ...form })
  submitting.value = false
}
</script>
