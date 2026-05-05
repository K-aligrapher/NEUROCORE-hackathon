import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Dashboard from './pages/Dashboard'
import NewAnalysis from './pages/NewAnalysis'
import AnalysisResult from './pages/AnalysisResult'
import History from './pages/History'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false, retry: 1, staleTime: 5000 },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analysis/new" element={<NewAnalysis />} />
          <Route path="/analysis/:jobId" element={<AnalysisResult />} />
          {/* Legacy processing URL — redirect to result page which now handles polling */}
          <Route path="/analysis/:jobId/processing" element={<Navigate to="/dashboard" replace />} />
          <Route path="/history" element={<History />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
