import { computed } from 'vue'

import { useAuthStore } from '@/stores/auth'


export function useProfileView() {
  const auth = useAuthStore()

  const initials = computed(() => {
    const name = auth.fullName
    if (!name) return '?'
    const parts = name.split(' ').filter(Boolean)
    return parts.length >= 2 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : name.slice(0, 2).toUpperCase()
  })

  return {
    auth,
    initials,
  }
}
