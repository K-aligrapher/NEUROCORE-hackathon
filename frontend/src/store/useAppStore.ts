import { create } from 'zustand'

interface AppState {
  selectedJobId: string | null
  setSelectedJobId: (jobId: string | null) => void
}

export const useAppStore = create<AppState>()((set) => ({
  selectedJobId: null,
  setSelectedJobId: (jobId) => set({ selectedJobId: jobId }),
}))
