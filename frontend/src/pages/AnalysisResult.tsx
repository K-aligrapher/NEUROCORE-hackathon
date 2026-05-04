import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analysisApi, AnalysisResult } from '../api/client'
import { motion } from 'framer-motion'
import { 
  Activity, AlertCircle, CheckCircle, FileText, Download, 
  Share2, Trash2, Clock, AlertTriangle, Info 
} from 'lucide-react'

export default function AnalysisResult() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()

  const { data: result, isLoading } = useQuery({
    queryKey: ['analysis', jobId],
    queryFn: () => analysisApi.getResult(jobId!),
    refetchInterval: result?.status === 'completed' ? false : 3000,
    enabled: !!jobId,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading results...</p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-600">Results not found</p>
        </div>
      </div>
    )
  }

  const getDiseaseStatus = (disease: string) => {
    const res = result.results?.[disease]
    if (!res) return { color: 'gray', label: 'Unknown', bg: 'bg-gray-100' }
    
    const diagnosis = res.diagnosis?.toLowerCase() || ''
    if (diagnosis.includes('positive') || diagnosis.includes('suggestive')) {
      return { 
        color: disease === 'malaria' ? 'red' : disease === 'sickle_cell' ? 'orange' : 'amber',
        label: res.diagnosis,
        bg: disease === 'malaria' ? 'bg-red-50 border-red-200' : disease === 'sickle_cell' ? 'bg-orange-50 border-orange-200' : 'bg-amber-50 border-amber-200'
      }
    }
    return { 
      color: 'green',
      label: 'Negative',
      bg: 'bg-green-50 border-green-200'
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate('/dashboard')} className="text-slate-500 hover:text-slate-700">
            ← Back
          </button>
          <div className="w-px h-6 bg-slate-200" />
          <span className="text-xl font-display font-semibold text-slate-800">Analysis Results</span>
          <span className="text-sm text-slate-500">• {jobId}</span>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Summary Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-6 shadow-lg mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-display font-semibold text-slate-800 mb-2">
                Analysis Complete
              </h1>
              <div className="flex items-center gap-4 text-sm text-slate-500">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {result.processing_time_ms ? `${Math.round(result.processing_time_ms/1000)}s` : '--'}
                </span>
                <span>•</span>
                <span>{result.cell_statistics?.rbc_count || 0} RBCs detected</span>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="p-3 rounded-xl border border-slate-200 hover:bg-slate-50">
                <Download className="w-5 h-5 text-slate-600" />
              </button>
              <button className="p-3 rounded-xl border border-slate-200 hover:bg-slate-50">
                <Share2 className="w-5 h-5 text-slate-600" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* Disease Results */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {['malaria', 'sickle_cell', 'thalassemia'].map((disease, i) => {
            const status = getDiseaseStatus(disease)
            const res = result.results?.[disease]
            const diseaseName = disease === 'malaria' ? 'Malaria' : disease === 'sickle_cell' ? 'Sickle Cell' : 'Thalassemia'
            const iconColor = status.color === 'red' ? 'text-red-600' : status.color === 'orange' ? 'text-orange-600' : status.color === 'amber' ? 'text-amber-600' : 'text-green-600'

            return (
              <motion.div
                key={disease}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`p-6 rounded-2xl border-2 ${status.bg}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-800">{diseaseName}</h3>
                  {status.color === 'red' ? (
                    <AlertCircle className={`w-6 h-6 ${iconColor}`} />
                  ) : status.color === 'green' ? (
                    <CheckCircle className={`w-6 h-6 ${iconColor}`} />
                  ) : (
                    <AlertTriangle className={`w-6 h-6 ${iconColor}`} />
                  )}
                </div>
                <p className={`text-2xl font-semibold ${iconColor} mb-2`}>
                  {res?.diagnosis || 'N/A'}
                </p>
                {res && (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Confidence</span>
                      <span className="font-medium">{Math.round(res.confidence * 100)}%</span>
                    </div>
                    {res.positive_rate !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Rate</span>
                        <span className="font-medium">{Math.round(res.positive_rate * 100)}%</span>
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>

        {/* Recommendation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-sky-50 rounded-2xl p-6 border border-sky-200"
        >
          <div className="flex items-start gap-4">
            <Info className="w-6 h-6 text-sky-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-sky-800 mb-2">Clinical Recommendation</h3>
              <p className="text-slate-700">
                {result.overall_recommendation || 'AI-assisted screening complete. Review results with a healthcare professional.'}
              </p>
              <p className="mt-4 text-sm text-sky-700">
                ⚠️ {result.disclaimer || 'This is an AI-assisted screening tool, not a clinical diagnosis. Results must be reviewed by a qualified medical professional.'}
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}