import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAppStore } from '../store/useAppStore'
import { analysisApi } from '../api/client'
import { motion } from 'framer-motion'
import { Plus, FileText, Activity, AlertCircle, Clock, Trash2 } from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, logout } = useAppStore()
  
  const { data: history, isLoading } = useQuery({
    queryKey: ['history'],
    queryFn: () => analysisApi.getHistory(10),
    refetchInterval: 10000,
  })

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-display font-semibold text-slate-800">LokiVision</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-600">{user?.name || 'Guest'}</span>
            <button 
              onClick={logout}
              className="text-sm text-slate-500 hover:text-slate-700"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Quick Upload */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <button
            onClick={() => navigate('/analysis/new')}
            className="w-full p-6 bg-gradient-to-r from-sky-500 to-sky-600 rounded-2xl text-white flex items-center justify-center gap-3 hover:shadow-xl hover:shadow-sky-500/25 transition-all"
          >
            <Plus className="w-6 h-6" />
            <span className="text-lg font-semibold">New Blood Smear Analysis</span>
          </button>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Analyses', value: history?.length || 0, color: 'sky' },
            { label: 'Malaria +', value: 0, color: 'red' },
            { label: 'Sickle +', value: 0, color: 'orange' },
            { label: 'Elliptocytosis', value: 0, color: 'amber' },
          ].map((stat, i) => (
            <div key={i} className="bg-white rounded-xl p-6 border border-slate-100">
              <p className="text-sm text-slate-500 mb-1">{stat.label}</p>
              <p className={`text-3xl font-semibold ${
                stat.color === 'red' ? 'text-red-600' :
                stat.color === 'orange' ? 'text-orange-600' :
                stat.color === 'amber' ? 'text-amber-600' :
                'text-sky-600'
              }`}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>

        {/* Recent Analyses */}
        <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-800">Recent Analyses</h2>
            <button 
              onClick={() => navigate('/history')}
              className="text-sm text-sky-600 hover:text-sky-700"
            >
              View All
            </button>
          </div>
          
          {isLoading ? (
            <div className="p-8 text-center text-slate-500">Loading...</div>
          ) : history && history.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {history.map((item, i) => (
                <div
                  key={i}
                  className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 cursor-pointer"
                  onClick={() => navigate(`/analysis/${item.job_id}`)}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      item.status === 'completed' ? 'bg-green-100' :
                      item.status === 'failed' ? 'bg-red-100' :
                      'bg-sky-100'
                    }`}>
                      {item.status === 'completed' ? (
                        <FileText className="w-5 h-5 text-green-600" />
                      ) : item.status === 'failed' ? (
                        <AlertCircle className="w-5 h-5 text-red-600" />
                      ) : (
                        <Clock className="w-5 h-5 text-sky-600 animate-pulse" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-slate-800">{item.job_id}</p>
                      <p className="text-sm text-slate-500">
                        {new Date(item.created_at).toLocaleDateString()}
                        {item.processing_time_ms && ` • ${Math.round(item.processing_time_ms/1000)}s`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      item.status === 'completed' ? 'bg-green-100 text-green-700' :
                      item.status === 'failed' ? 'bg-red-100 text-red-700' :
                      'bg-sky-100 text-sky-700'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No analyses yet. Start by uploading a blood smear image.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}