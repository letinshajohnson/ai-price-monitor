import { useEffect, useState } from 'react'
import { getIntelligence, getStats } from '../utils/api'

export default function Dashboard() {
  const [intel, setIntel] = useState({ data: [], summary: {} })
  const [stats, setStats] = useState(null)

  useEffect(() => {
    getIntelligence().then(setIntel).catch(() => {})
    getStats().then(setStats).catch(() => {})
  }, [])

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-bold text-gray-800">📊 Price Intelligence Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Products",  value: stats?.total_products    || 0,    bg: "bg-blue-50",   color: "text-blue-700"   },
          { label: "Competitors",     value: stats?.total_competitors || 0,    bg: "bg-green-50",  color: "text-green-700"  },
          { label: "Unread Alerts",   value: stats?.unread_alerts     || 0,    bg: "bg-red-50",    color: "text-red-600"    },
          { label: "Avg Price Gap",   value: `${intel.summary?.avg_price_gap || 0}%`, bg: "bg-purple-50", color: "text-purple-700" },
        ].map((c, i) => (
          <div key={i} className={`${c.bg} rounded-2xl p-4`}>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{c.label}</p>
            <p className={`text-2xl font-bold mt-1 ${c.color}`}>{c.value}</p>
          </div>
        ))}
      </div>

      {/* Position summary */}
      {intel.summary?.total_products > 0 && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "✅ Cheapest",    value: intel.summary.cheapest,    bg: "bg-green-50" },
            { label: "🟡 Competitive", value: intel.summary.competitive,  bg: "bg-yellow-50" },
            { label: "🔴 Overpriced",  value: intel.summary.overpriced,   bg: "bg-red-50" },
          ].map((c, i) => (
            <div key={i} className={`${c.bg} rounded-2xl p-4 text-center`}>
              <p className="text-3xl font-black text-gray-800">{c.value}</p>
              <p className="text-sm text-gray-500 mt-1">{c.label} products</p>
            </div>
          ))}
        </div>
      )}

      {/* Price Intelligence Table */}
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-bold text-gray-800">Competitive Price Analysis</h2>
          <span className="text-xs text-gray-400">{intel.data.length} products tracked</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {["Product", "Category", "Our Price", "Min Competitor", "Avg Competitor", "Gap %", "Position", "Cheapest At"].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {intel.data.map((row, i) => (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-800 whitespace-nowrap">{row.product_name}</td>
                  <td className="px-4 py-3 text-gray-500">{row.category}</td>
                  <td className="px-4 py-3 font-bold text-blue-700">₹{row.our_price}</td>
                  <td className="px-4 py-3 text-green-700 font-semibold">₹{row.min_competitor_price?.toFixed(0)}</td>
                  <td className="px-4 py-3 text-gray-600">₹{row.avg_competitor_price?.toFixed(0)}</td>
                  <td className={`px-4 py-3 font-bold ${row.price_gap_pct > 0 ? 'text-red-500' : 'text-green-600'}`}>
                    {row.price_gap_pct > 0 ? '+' : ''}{row.price_gap_pct}%
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">{row.position}</td>
                  <td className="px-4 py-3 text-xs text-gray-400">{row.cheapest_competitor}</td>
                </tr>
              ))}
              {intel.data.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-16 text-center text-gray-400">
                    <p className="text-3xl mb-2">🔍</p>
                    <p>No data yet. Add products and run a scrape.</p>
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
