import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { analysisApi, AnalysisResult } from '../api/client'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, FileImage, AlertCircle } from 'lucide-react'

export default function NewAnalysis() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const f = acceptedFiles[0]
    if (f) {
      setFile(f)
      setPreview(URL.createObjectURL(f))
      setError('')
      setResult(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    },
    maxSize: 50 * 1024 * 1024,
    multiple: false,
  })

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError('')
    setResult(null)

    try {
      const analysisResult = await analysisApi.upload(file)
      setResult(analysisResult)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const removeFile = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate('/')} className="text-slate-500 hover:text-slate-700">
            ← Back
          </button>
          <div className="w-px h-6 bg-slate-200" />
          <span className="text-xl font-display font-semibold text-slate-800">New Analysis</span>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-6 py-8">
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700"
            >
              <AlertCircle className="w-5 h-5" />
              <p>{error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Drop Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-sky-500 bg-sky-50'
              : 'border-slate-300 hover:border-sky-400'
          } ${file ? 'border-sky-500 bg-sky-50' : ''}`}
        >
          <input {...getInputProps()} />

          {preview ? (
            <div className="relative">
              <img
                src={preview}
                alt="Preview"
                className="max-h-64 mx-auto rounded-xl"
              />
              <button
                onClick={(e) => { e.stopPropagation(); removeFile() }}
                className="absolute top-2 right-2 p-2 bg-slate-800/80 rounded-full text-white hover:bg-slate-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="py-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-sky-100 rounded-2xl flex items-center justify-center">
                <Upload className="w-8 h-8 text-sky-600" />
              </div>
              <p className="text-lg font-medium text-slate-700 mb-2">
                {isDragActive ? 'Drop your blood smear image here' : 'Drag & drop your blood smear image'}
              </p>
              <p className="text-slate-500">
                or click to browse • JPG, PNG, TIFF, BMP • Max 50MB
              </p>
            </div>
          )}
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full mt-8 py-4 bg-sky-500 hover:bg-sky-600 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl font-semibold transition-all shadow-lg shadow-sky-500/25 flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <FileImage className="w-5 h-5" />
              <span>Analyze Blood Smear</span>
            </>
          )}
        </button>

        {/* Results */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 space-y-6"
          >
            <h2 className="text-xl font-semibold text-slate-800">Analysis Results</h2>

            {/* Timing & Device */}
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-500">Device:</span>{' '}
                  <span className="font-medium text-slate-700">{result.device || 'cpu'}</span>
                </div>
                {result.timing && (
                  <div>
                    <span className="text-slate-500">Total Time:</span>{' '}
                    <span className="font-medium text-slate-700">{result.timing.total.toFixed(2)}s</span>
                  </div>
                )}
              </div>
            </div>

            {/* Cell Statistics */}
            {result.cell_statistics && (
              <div className="p-4 bg-white rounded-xl border border-slate-200">
                <h3 className="text-sm font-semibold text-slate-600 mb-3">Cell Statistics</h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-slate-500">Total:</span>{' '}
                    <span className="font-medium">{result.cell_statistics.total_detected}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">RBC:</span>{' '}
                    <span className="font-medium">{result.cell_statistics.rbc_count}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Rejected:</span>{' '}
                    <span className="font-medium">{result.cell_statistics.rejected_count}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Disease Results */}
            {result.results && Object.entries(result.results).map(([disease, data]) => (
              <div
                key={disease}
                className={`p-4 rounded-xl border ${
                  data.diagnosis === 'Positive'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-green-50 border-green-200'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold capitalize">{disease}</h3>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      data.diagnosis === 'Positive'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {data.diagnosis}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-slate-500">Confidence:</span>{' '}
                    <span className="font-medium">{(data.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Positive Rate:</span>{' '}
                    <span className="font-medium">{(data.positive_rate * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Positive Count:</span>{' '}
                    <span className="font-medium">{data.positive_count}</span>
                  </div>
                  {data.severity && (
                    <div>
                      <span className="text-slate-500">Severity:</span>{' '}
                      <span className="font-medium capitalize">{data.severity}</span>
                    </div>
                  )}
                </div>
                {data.cell_distribution && (
                  <div className="mt-3 pt-3 border-t border-slate-200">
                    <span className="text-xs text-slate-500">Cell Distribution:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {Object.entries(data.cell_distribution).map(([label, count]) => (
                        <span key={label} className="px-2 py-1 bg-white rounded text-xs">
                          {label}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Disclaimer */}
            {result.disclaimer && (
              <p className="text-xs text-slate-400 text-center">{result.disclaimer}</p>
            )}
          </motion.div>
        )}
      </div>
    </div>
  )
}