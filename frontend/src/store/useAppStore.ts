import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  name: string
  role: string
}

interface AppState {
  user: User | null
  isAuthenticated: boolean
  selectedJobId: string | null
  uploadProgress: number
  
  setUser: (user: User | null) => void
  setSelectedJobId: (jobId: string | null) => void
  setUploadProgress: (progress: number) => void
  logout: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      selectedJobId: null,
      uploadProgress: 0,
      
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setSelectedJobId: (jobId) => set({ selectedJobId: jobId }),
      setUploadProgress: (progress) => set({ uploadProgress: progress }),
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'hemavision-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)