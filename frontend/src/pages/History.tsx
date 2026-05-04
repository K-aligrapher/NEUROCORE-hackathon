import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analysisApi } from '../api/client'
import { motion } from 'framer-motion'
import { FileText, Clock, AlertCircle, Trash2, Search } from 'lucide-react'
import { useState } from 'react'

export default function History() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')

  const { data: history, isLoading, refetch } = useQuery({
    queryKey: ['history'],
    queryFn: () => analysisApi.getHistory(50),
  })

  const handleDelete = async (jobId: string) => {
    if (confirm('Delete this analysis?')) {
      await analysisApi.delete(jobId)
      refetch()
    }
  }

  const filtered = history?.filter(h => 
    h.job_id.toLowerCase().includes(search.toLowerCase()) ||
    h.patient_id?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate('/dashboard')} className="text-slate-500 hover:text-slate-700">
            ← Back
          </button>
          <div className="w-px h-6 bg-slate-200" />
          <span className="text-xl font-display font-semibold text-slate-800">Analysis History</span>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by job ID or patient ID..."
            className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all"
          />
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-500">Job ID</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-500">Patient ID</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-500">Date</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-500">Status</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-500">Time</th>
                <th className="px-6 py-4 text-right text-sm font-medium text-slate-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    Loading...
                  </td>
                </tr>
              ) : filtered && filtered.length > 0 ? (
                filtered.map((item, i) => (
                  <motion.tr
                    key={item.job_id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.05 }}
                    className="hover:bg-slate-50 cursor-pointer"
                    onClick={() => navigate(`/analysis/${item.job_id}`)}
                  >
                    <td className="px-6 py-4">
                      <span className="font-mono text-sm">{item.job_id}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {item.patient_id || '-'}
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        item.status === 'completed' ? 'bg-green-100 text-green-700' :
                        item.status === 'failed' ? 'bg-red-100 text-red-700' :
                        'bg-sky-100 text-sky-700'
                      }`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {item.processing_time_ms ? `${Math.round(item.processing_time_ms/1000)}s` : '-'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(item.job_id) }}
                        className="p-2 text-slate-400 hover:text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </motion.tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    No analyses found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}