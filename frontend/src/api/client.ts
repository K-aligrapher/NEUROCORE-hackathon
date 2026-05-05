import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ── Types ──────────────────────────────────────────────────────────────────────

export interface CellStatistics {
  total_detected: number
  rbc_count: number
  wbc_count: number
  platelet_count: number
  rejected_count: number
}

export interface DiseaseResult {
  diagnosis: string
  confidence: number
  positive_rate: number
  positive_count: number
  cell_distribution: Record<string, number>
  severity?: string
}

export interface AnalysisResult {
  job_id: string
  status: string
  created_at: string
  completed_at?: string
  processing_time_ms?: number
  cell_statistics?: CellStatistics
  results?: {
    malaria?: DiseaseResult
    thalassemia?: DiseaseResult
  }
  quality_flags: string[]
  overall_recommendation?: string
  disclaimer?: string
}

export interface HistoryItem {
  job_id: string
  status: string
  created_at: string
  completed_at?: string
  patient_id?: string
  disease_results: string[]
  processing_time_ms?: number
}

// ── API calls ──────────────────────────────────────────────────────────────────

export const analysisApi = {
  upload: async (file: File, patientId?: string, notes?: string) => {
    const form = new FormData()
    form.append('image', file)
    if (patientId) form.append('patient_id', patientId)
    if (notes) form.append('notes', notes)
    const res = await apiClient.post<{ job_id: string; status: string }>(
      '/analysis/upload',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return res.data
  },

  getResult: async (jobId: string): Promise<AnalysisResult> => {
    const res = await apiClient.get<AnalysisResult>(`/analysis/${jobId}`)
    return res.data
  },

  getHistory: async (limit = 20): Promise<HistoryItem[]> => {
    const res = await apiClient.get<HistoryItem[]>('/analysis/history', { params: { limit } })
    return res.data
  },
}
