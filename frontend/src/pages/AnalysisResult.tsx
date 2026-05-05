import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analysisApi } from '../api/client'
import { motion } from 'framer-motion'
import {
  AlertCircle, CheckCircle, AlertTriangle, Info,
  Loader2, Clock, Microscope,
} from 'lucide-react'

// Matches backend JobStatus values
const STAGES = [
  { key: 'queued',        label: 'Queued — waiting to start' },
  { key: 'preprocessing', label: 'Loading image' },
  { key: 'classifying',   label: 'Running AI analysis' },
  { key: 'completed',     label: 'Complete' },
]

export default function AnalysisResult() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()

  const { data: result, isLoading, error } = useQuery({
    queryKey: ['analysis', jobId],
    queryFn: () => analysisApi.getResult(jobId!),
    enabled: !!jobId,
    // React Query v5: function form reads the live query state without closure issues
    refetchInterval: (query) => {
      const s = query.state.data?.status
      return s === 'completed' || s === 'failed' ? false : 2000
    },
  })

  // ── Loading skeleton ────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading…</p>
        </div>
      </div>
    )
  }

  // ── Network error ───────────────────────────────────────────────────────────
  if (error || !result) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-700 font-medium mb-1">Could not load results</p>
          <p className="text-slate-500 text-sm mb-4">{String(error ?? 'Job not found')}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-sky-500 text-white rounded-lg text-sm"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  // ── Still processing ────────────────────────────────────────────────────────
  if (result.status !== 'completed' && result.status !== 'failed') {
    const stageIdx = STAGES.findIndex(s => s.key === result.status)
    const current = stageIdx >= 0 ? stageIdx : 0

    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl p-8 shadow-lg"
          >
            <div className="text-center mb-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-sky-100 rounded-2xl flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-sky-600 animate-spin" />
              </div>
              <h1 className="text-xl font-semibold text-slate-800 mb-1">Analysing Blood Smear</h1>
              <p className="text-sm text-slate-400">{jobId}</p>
            </div>

            <div className="space-y-4 mb-8">
              {STAGES.slice(0, -1).map((s, i) => (
                <div key={s.key} className="flex items-center gap-3">
                  {i < current ? (
                    <CheckCircle className="w-5 h-5 text-green-500 shrink-0" />
                  ) : i === current ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      className="w-5 h-5 border-2 border-sky-500 border-t-transparent rounded-full shrink-0"
                    />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-slate-200 shrink-0" />
                  )}
                  <span className={i <= current ? 'text-slate-800 text-sm' : 'text-slate-400 text-sm'}>
                    {s.label}
                  </span>
                </div>
              ))}
            </div>

            {result.cell_statistics && (
              <div className="p-4 bg-sky-50 rounded-xl text-center">
                <p className="text-xs text-sky-600 mb-1">Cells detected so far</p>
                <p className="text-2xl font-semibold text-sky-700">
                  {result.cell_statistics.total_detected}
                </p>
              </div>
            )}

            <p className="mt-4 text-center text-xs text-slate-400">
              Typically takes 20–60 seconds on CPU
            </p>
          </motion.div>
        </div>
      </div>
    )
  }

  // ── Failed ──────────────────────────────────────────────────────────────────
  if (result.status === 'failed') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center max-w-sm mx-6">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-700 font-medium mb-1">Analysis failed</p>
          <p className="text-slate-500 text-sm mb-4">
            {result.disclaimer || 'An error occurred during processing. Please try again with a clearer image.'}
          </p>
          <button
            onClick={() => navigate('/analysis/new')}
            className="px-4 py-2 bg-sky-500 text-white rounded-lg text-sm"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  // ── Completed — show results ────────────────────────────────────────────────
  const diseaseConfig = [
    {
      key: 'malaria',
      label: 'Malaria',
      positiveColor: 'red',
      positiveBg: 'bg-red-50 border-red-200',
    },
    {
      key: 'thalassemia',
      label: 'Thalassemia',
      positiveColor: 'amber',
      positiveBg: 'bg-amber-50 border-amber-200',
    },
  ] as const

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-slate-500 hover:text-slate-700 text-sm"
          >
            ← Back
          </button>
          <div className="w-px h-5 bg-slate-200" />
          <Microscope className="w-5 h-5 text-sky-500" />
          <span className="font-semibold text-slate-800">Analysis Results</span>
          <span className="text-xs text-slate-400 font-mono">{jobId}</span>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">

        {/* Summary bar */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100"
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-semibold text-slate-800 mb-1">Analysis Complete</h1>
              <div className="flex items-center gap-4 text-sm text-slate-500">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {result.processing_time_ms
                    ? `${(result.processing_time_ms / 1000).toFixed(1)}s`
                    : '--'}
                </span>
                <span>•</span>
                <span>{result.cell_statistics?.rbc_count ?? 0} cells analysed</span>
              </div>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
        </motion.div>

        {/* Disease cards */}
        <div className="grid sm:grid-cols-2 gap-6">
          {diseaseConfig.map(({ key, label, positiveColor, positiveBg }, i) => {
            const res = result.results?.[key as keyof typeof result.results]

            const isPositive =
              res?.diagnosis?.toLowerCase().includes('positive') ||
              res?.diagnosis?.toLowerCase().includes('suggestive')

            const cardBg = res
              ? isPositive
                ? positiveBg
                : 'bg-green-50 border-green-200'
              : 'bg-slate-100 border-slate-200'

            const textColor = res
              ? isPositive
                ? positiveColor === 'red'
                  ? 'text-red-600'
                  : 'text-amber-600'
                : 'text-green-600'
              : 'text-slate-400'

            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`rounded-2xl border-2 p-6 ${cardBg}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-800">{label}</h3>
                  {!res ? (
                    <AlertTriangle className="w-6 h-6 text-slate-400" />
                  ) : isPositive ? (
                    positiveColor === 'red' ? (
                      <AlertCircle className="w-6 h-6 text-red-600" />
                    ) : (
                      <AlertTriangle className="w-6 h-6 text-amber-600" />
                    )
                  ) : (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  )}
                </div>

                <p className={`text-3xl font-bold mb-4 ${textColor}`}>
                  {res?.diagnosis ?? 'N/A'}
                </p>

                {res ? (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Confidence</span>
                      <span className="font-semibold text-slate-700">
                        {Math.round(res.confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Affected cells</span>
                      <span className="font-semibold text-slate-700">
                        {res.positive_count ?? 0} / {result.cell_statistics?.rbc_count ?? '—'}
                        {res.positive_rate !== undefined &&
                          ` (${Math.round(res.positive_rate * 100)}%)`}
                      </span>
                    </div>
                    {key === 'malaria' && res.severity && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Severity</span>
                        <span className={`font-semibold capitalize ${textColor}`}>
                          {res.severity}
                        </span>
                      </div>
                    )}
                    {/* Cell breakdown bar */}
                    {res.cell_distribution && res.positive_count != null && (
                      <div className="mt-3">
                        <div className="flex rounded-full overflow-hidden h-2">
                          <div
                            className={`${isPositive ? (positiveColor === 'red' ? 'bg-red-400' : 'bg-amber-400') : 'bg-green-400'}`}
                            style={{
                              width: `${Math.round(res.positive_rate! * 100)}%`,
                            }}
                          />
                          <div className="bg-slate-200 flex-1" />
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No data returned</p>
                )}
              </motion.div>
            )
          })}
        </div>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-sky-50 rounded-2xl p-5 border border-sky-200 flex items-start gap-3"
        >
          <Info className="w-5 h-5 text-sky-500 mt-0.5 shrink-0" />
          <p className="text-sm text-slate-600">
            {result.disclaimer ??
              'AI-assisted screening only. Results must be confirmed by a qualified clinician before any clinical decision is made.'}
          </p>
        </motion.div>

      </div>
    </div>
  )
}
