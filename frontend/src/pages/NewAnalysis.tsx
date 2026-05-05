import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { useAppStore } from '../store/useAppStore'
import { analysisApi } from '../api/client'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, FileImage, AlertCircle } from 'lucide-react'

export default function NewAnalysis() {
  const navigate = useNavigate()
  const setSelectedJobId = useAppStore((state) => state.setSelectedJobId)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [patientId, setPatientId] = useState('')
  const [notes, setNotes] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const f = acceptedFiles[0]
    if (f) {
      setFile(f)
      setPreview(URL.createObjectURL(f))
      setError('')
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

    try {
      const result = await analysisApi.upload(file, patientId || undefined, notes || undefined)
      setSelectedJobId(result.job_id)
      navigate(`/analysis/${result.job_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const removeFile = () => {
    setFile(null)
    setPreview(null)
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

        {/* Metadata */}
        <div className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Patient ID (optional)
            </label>
            <input
              type="text"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              placeholder="PT-2026-00123"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Clinical Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Fever for 3 days, returned from endemic region..."
              rows={3}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all resize-none"
            />
          </div>
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
              <span>Uploading...</span>
            </>
          ) : (
            <>
              <FileImage className="w-5 h-5" />
              <span>Analyze Blood Smear</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}