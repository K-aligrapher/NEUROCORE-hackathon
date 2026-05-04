import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analysisApi } from '../api/client'
import { motion } from 'framer-motion'
import { Loader2, CheckCircle, Circle } from 'lucide-react'

const STAGES = [
  { key: 'queued', label: 'Queued' },
  { key: 'preprocessing', label: 'Preprocessing' },
  { key: 'segmenting', label: 'Detecting Cells' },
  { key: 'enhancing', label: 'Enhancing' },
  { key: 'classifying', label: 'Analyzing' },
  { key: 'generating_report', label: 'Generating Report' },
  { key: 'completed', label: 'Complete' },
]

export default function AnalysisProcessing() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const [stage, setStage] = useState(0)
  const [cellCount, setCellCount] = useState(0)

  const { data } = useQuery({
    queryKey: ['analysis', jobId],
    queryFn: () => analysisApi.getResult(jobId!),
    refetchInterval: 3000,
    enabled: !!jobId,
  })

  useEffect(() => {
    if (data?.status) {
      const idx = STAGES.findIndex(s => s.key === data.status)
      if (idx >= 0) setStage(idx)
      if (data.cell_statistics) {
        setCellCount(data.cell_statistics.total_detected)
      }
    }
    
    if (data?.status === 'completed') {
      setTimeout(() => navigate(`/analysis/${jobId}`), 1000)
    }
  }, [data, jobId, navigate])

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="max-w-lg w-full mx-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-8 shadow-lg"
        >
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 bg-sky-100 rounded-2xl flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-sky-600 animate-spin" />
            </div>
            <h1 className="text-2xl font-display font-semibold text-slate-800 mb-2">
              Analyzing Blood Smear
            </h1>
            <p className="text-slate-500">
              Job ID: {jobId}
            </p>
          </div>

          {/* Progress */}
          <div className="space-y-4">
            {STAGES.slice(0, -1).map((s, i) => (
              <div key={s.key} className="flex items-center gap-4">
                {i < stage ? (
                  <CheckCircle className="w-6 h-6 text-green-500" />
                ) : i === stage ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-6 h-6 border-2 border-sky-500 border-t-transparent rounded-full"
                  />
                ) : (
                  <Circle className="w-6 h-6 text-slate-300" />
                )}
                <span className={`${
                  i <= stage ? 'text-slate-800' : 'text-slate-400'
                }`}>
                  {s.label}
                </span>
              </div>
            ))}
          </div>

          {/* Cell Counter */}
          <div className="mt-8 p-4 bg-sky-50 rounded-xl text-center">
            <p className="text-sm text-sky-600 mb-1">Cells Detected</p>
            <p className="text-3xl font-semibold text-sky-700">{cellCount}</p>
          </div>

          <p className="mt-6 text-center text-sm text-slate-500">
            This typically takes 20-30 seconds
          </p>
        </motion.div>
      </div>
    </div>
  )
}