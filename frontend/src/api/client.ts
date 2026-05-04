import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// No auth interceptors needed

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
  device?: string
  timing?: {
    detection: number
    crop: number
    classify: number
    total: number
  }
  cell_statistics?: CellStatistics
  results?: {
    malaria: DiseaseResult
    thalassemia: DiseaseResult
  }
  quality_flags: string[]
  disclaimer?: string
  error_message?: string
  model_versions?: Record<string, string>
}

export const analysisApi = {
  upload: async (file: File, patientId?: string, notes?: string): Promise<AnalysisResult> => {
    const formData = new FormData()
    formData.append('image', file)
    if (patientId) formData.append('patient_id', patientId)
    if (notes) formData.append('notes', notes)

    const response = await apiClient.post<AnalysisResult>('/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}