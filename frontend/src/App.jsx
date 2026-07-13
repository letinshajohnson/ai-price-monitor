import { useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import Dashboard    from './pages/Dashboard'
import AlertsPage   from './pages/AlertsPage'
import ProductsPage from './pages/ProductsPage'
import { getStats, triggerScrape } from './utils/api'
import toast from 'react-hot-toast'

const NAV = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'products',  label: '🛍️ Products'  },
  { id: 'alerts',    label: '🔔 Alerts'    },
]

export default function App() {
  const [page, setPage]   = useState('dashboard')
  const [stats, setStats] = useState(null)

  useEffect(() => {
    getStats().then(setStats).catch(() => {})
    const interval = setInterval(() => getStats().then(setStats).catch(() => {}), 30000)
    return () => clearInterval(interval)
  }, [])

  const handleScrape = async () => {
    try { await triggerScrape(); toast.success('Scraping job triggered!') }
    catch { toast.error('Failed to trigger scrape') }
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Toaster position="top-right" />
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-gray-100">
          <h1 className="font-black text-blue-700 text-base">🔍 PriceWatch AI</h1>
          <p className="text-xs text-gray-400 mt-0.5">Competitor Intelligence</p>
        </div>
        <nav className="p-3 flex-1 space-y-1">
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)}
              className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold transition-colors flex items-center justify-between ${page === n.id ? 'bg-blue-700 text-white' : 'text-gray-600 hover:bg-gray-100'}`}>
              <span>{n.label}</span>
              {n.id === 'alerts' && stats?.unread_alerts > 0 && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${page === n.id ? 'bg-white text-blue-700' : 'bg-red-500 text-white'}`}>{stats.unread_alerts}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="p-3 border-t border-gray-100 space-y-2">
          {stats && (
            <div className="grid grid-cols-2 gap-1 text-center">
              <div className="bg-gray-50 rounded-lg p-2">
                <p className="text-base font-bold text-gray-800">{stats.total_products}</p>
                <p className="text-xs text-gray-400">Products</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-2">
                <p className="text-base font-bold text-gray-800">{stats.total_competitors}</p>
                <p className="text-xs text-gray-400">Competitors</p>
              </div>
            </div>
          )}
          <button onClick={handleScrape} className="w-full text-xs bg-blue-700 text-white py-2 rounded-xl hover:bg-blue-800 font-semibold transition-colors">
            ▶ Run Scrape Now
          </button>
          {stats && <p className="text-xs text-gray-400 text-center">{stats.total_prices?.toLocaleString()} price records</p>}
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        {page === 'dashboard' && <Dashboard />}
        {page === 'products'  && <ProductsPage />}
        {page === 'alerts'    && <AlertsPage />}
      </main>
    </div>
  )
}
