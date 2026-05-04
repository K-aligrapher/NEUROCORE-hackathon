import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, Shield, Zap, FileText, ChevronRight, Microscope, AlertCircle, CheckCircle } from 'lucide-react'

export default function Landing() {
  const navigate = useNavigate()
  
  return (
    <div className="min-h-screen gradient-hero">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-sky-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center">
<Activity className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-display font-semibold text-slate-800">LokiVision</span>
          </div>
          <nav className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/auth')}
              className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium transition-colors"
            >
              Sign In
            </button>
            <button 
              onClick={() => navigate('/auth')}
              className="px-5 py-2.5 bg-sky-500 hover:bg-sky-600 text-white rounded-lg font-medium transition-colors shadow-lg shadow-sky-500/25"
            >
              Get Started
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-sky-100 rounded-full text-sky-700 text-sm font-medium mb-6">
                <Zap className="w-4 h-4" />
                <span>AI-Powered Blood Smear Analysis</span>
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-display font-semibold text-slate-800 leading-tight mb-6">
                Instant Blood Disease{' '}
                <span className="text-sky-600">Detection</span>
              </h1>
              
              <p className="text-xl text-slate-600 mb-8 leading-relaxed">
                Analyze blood smears in seconds. Detect Malaria, Sickle Cell Anemia, 
                and Thalassemia with clinical-grade accuracy.
              </p>
              
              <div className="flex flex-wrap gap-4">
                <button 
                  onClick={() => navigate('/analysis/new')}
                  className="px-8 py-4 bg-sky-500 hover:bg-sky-600 text-white rounded-xl font-semibold transition-all shadow-xl shadow-sky-500/25 flex items-center gap-2"
                >
                  <Microscope className="w-5 h-5" />
                  Analyze a Smear — Free
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex items-center gap-8 mt-10 text-sm text-slate-500">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>FDA disclaimer applied</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>HIPAA compliant</span>
                </div>
              </div>
            </motion.div>
            
            {/* Animated Cell Illustration */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="aspect-square rounded-3xl bg-gradient-to-br from-sky-100 to-white p-8 shadow-2xl shadow-sky-500/20">
                <div className="grid grid-cols-4 gap-3 h-full">
                  {[...Array(16)].map((_, i) => (
                    <motion.div
                      key={i}
                      className={`rounded-full ${
                        i % 5 === 0 ? 'bg-red-400' : 
                        i % 3 === 0 ? 'bg-orange-400' : 
                        i % 7 === 0 ? 'bg-amber-400' : 
                        'bg-red-300'
                      }`}
                      animate={{
                        scale: [1, 1.1, 1],
                      }}
                      transition={{
                        duration: 3 + (i % 3),
                        repeat: Infinity,
                        delay: i * 0.2,
                      }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-display font-semibold text-slate-800 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Three simple steps to get comprehensive blood disease analysis
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: FileText,
                title: "1. Upload",
                description: "Upload a blood smear image from your microscope or camera",
                color: "sky"
              },
              {
                icon: Activity,
                title: "2. Analyze",
                description: "Our AI processes the image in under 30 seconds",
                color: "sky"
              },
              {
                icon: Shield,
                title: "3. Results",
                description: "Get detailed results with disease classifications",
                color: "sky"
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                viewport={{ once: true }}
                className="p-8 rounded-2xl bg-gradient-to-br from-slate-50 to-white border border-slate-100"
              >
                <div className={`w-14 h-14 rounded-2xl bg-${feature.color}-100 flex items-center justify-center mb-6`}>
                  <feature.icon className={`w-7 h-7 text-${feature.color}-600`} />
                </div>
                <h3 className="text-xl font-semibold text-slate-800 mb-3">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Disease Coverage */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-display font-semibold text-slate-800 mb-4">
              Disease Coverage
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Detect two clinically significant blood diseases
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                name: "Malaria",
                description: "Detects parasitized red blood cells with ring-form parasites",
                stats: "95%+ Sensitivity",
                color: "malaria"
              },
              {
                name: "Thalassemia",
                description: "Screens for hypochromic, target, and microcytic red blood cells",
                stats: "93%+ AUC",
                color: "thal"
              }
            ].map((disease, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                viewport={{ once: true }}
                className={`p-8 rounded-2xl border-2 ${
                  disease.color === 'malaria' ? 'border-red-200 bg-red-50' :
                  'border-amber-200 bg-amber-50'
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className={`text-2xl font-semibold ${
                    disease.color === 'malaria' ? 'text-red-700' :
                    'text-amber-700'
                  }`}>
                    {disease.name}
                  </h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    disease.color === 'malaria' ? 'bg-red-200 text-red-700' :
                    disease.color === 'sickle' ? 'bg-orange-200 text-orange-700' :
                    'bg-amber-200 text-amber-700'
                  }`}>
                    {disease.stats}
                  </span>
                </div>
                <p className="text-slate-600">{disease.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-display font-semibold text-slate-800 mb-6">
            Ready to Transform Blood Analysis?
          </h2>
          <p className="text-xl text-slate-600 mb-8">
            Join healthcare professionals using LokiVision for faster, more accurate blood disease detection.
          </p>
          <div className="flex justify-center gap-4">
            <button 
              onClick={() => navigate('/auth')}
              className="px-8 py-4 bg-sky-500 hover:bg-sky-600 text-white rounded-xl font-semibold transition-all shadow-xl shadow-sky-500/25"
            >
              Get Started Free
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-100">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-500 flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-display font-semibold text-slate-700">LokiVision</span>
          </div>
          <p className="text-sm text-slate-500">
            AI-assisted screening. Not for clinical diagnosis.
          </p>
        </div>
      </footer>
    </div>
  )
}