<template>
  <div class="space-y-4">
    <p class="text-sm font-semibold text-[--color-ink]">Submit Correction</p>

    <div class="grid gap-3">
      <!-- Field being corrected -->
      <div>
        <label class="block text-xs font-semibold text-[--color-ink-muted] mb-1.5">Field</label>
        <select v-model="form.field_name" class="input text-sm">
          <option value="" disabled>Select field…</option>
          <option v-for="f in FIELDS" :key="f.value" :value="f.value">{{ f.label }}</option>
        </select>
      </div>

      <!-- Old value -->
      <div>
        <label class="block text-xs font-semibold text-[--color-ink-muted] mb-1.5">Previous Value</label>
        <input v-model="form.old_value" class="input text-sm" placeholder="What was wrong…" />
      </div>

      <!-- New value -->
      <div>
        <label class="block text-xs font-semibold text-[--color-ink-muted] mb-1.5">Corrected Value</label>
        <input v-model="form.new_value" class="input text-sm" placeholder="Correct value…" />
      </div>

      <!-- Explanation -->
      <div>
        <label class="block text-xs font-semibold text-[--color-ink-muted] mb-1.5">Explanation</label>
        <textarea v-model="form.explanation" class="input resize-none text-sm" rows="2" placeholder="Reason for correction…" />
      </div>
    </div>

    <div class="flex gap-2 pt-1">
      <button
        class="btn btn-primary flex-1"
        :disabled="!isValid || submitting"
        @click="submit"
      >
        <CheckCircle :size="15" />
        {{ submitting ? 'Saving…' : 'Save Correction' }}
      </button>
      <button class="btn btn-ghost" @click="$emit('cancel')">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CheckCircle } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'submit', payload: typeof form): void
  (e: 'cancel'): void
}>()

const FIELDS = [
  { value: 'particular_name', label: 'Particular Name' },
  { value: 'amount_claimed',  label: 'Amount Claimed'  },
  { value: 'date_of_expense', label: 'Date of Expense' },
  { value: 'vendor',          label: 'Vendor'           },
  { value: 'attachment',      label: 'Attachment/OR'   },
]

const submitting = ref(false)
const form = reactive({
  field_name:  '',
  old_value:   '',
  new_value:   '',
  explanation: '',
})

const isValid = computed(() =>
  form.field_name && form.old_value && form.new_value && form.explanation,
)

const submit = async () => {
  if (!isValid.value) return
  submitting.value = true
  await new Promise(r => setTimeout(r, 600))
  emit('submit', { ...form })
  submitting.value = false
}
</script>
