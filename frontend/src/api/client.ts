import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/auth'
    }
    return Promise.reject(error)
  }
)

export interface User {
  id: string
  email: string
  name: string
  role: string
  institution?: string
  country?: string
  is_verified: boolean
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface JobStatus {
  status: 'queued' | 'preprocessing' | 'segmenting' | 'enhancing' | 'classifying' | 'completed' | 'failed'
}

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
  image?: {
    original_url?: string
    annotated_url?: string
    thumbnail_url?: string
  }
  cell_statistics?: CellStatistics
  results?: {
    malaria: DiseaseResult
    sickle_cell: DiseaseResult
    thalassemia: DiseaseResult
  }
  quality_flags: string[]
  overall_recommendation?: string
  disclaimer?: string
  model_versions?: Record<string, string>
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

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post<Token>('/auth/login', { email, password })
    return response.data
  },
  
  register: async (userData: {
    email: string
    password: string
    name: string
    role?: string
    institution?: string
    country?: string
  }) => {
    const response = await apiClient.post<User>('/auth/register', userData)
    return response.data
  },
}

export const analysisApi = {
  upload: async (file: File, patientId?: string, notes?: string) => {
    const formData = new FormData()
    formData.append('image', file)
    if (patientId) formData.append('patient_id', patientId)
    if (notes) formData.append('notes', notes)
    
    const response = await apiClient.post<{ job_id: string; status: string }>('/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  
  getResult: async (jobId: string): Promise<AnalysisResult> => {
    const response = await apiClient.get<AnalysisResult>(`/analysis/${jobId}`)
    return response.data
  },
  
  getHistory: async (limit = 20): Promise<HistoryItem[]> => {
    const response = await apiClient.get<HistoryItem[]>('/analysis/history', { params: { limit } })
    return response.data
  },
  
  delete: async (jobId: string) => {
    const response = await apiClient.delete(`/analysis/${jobId}`)
    return response.data
  },
}