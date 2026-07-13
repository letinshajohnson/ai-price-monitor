import { useEffect, useState } from 'react'
import { getAlerts, markAlertRead } from '../utils/api'
import toast from 'react-hot-toast'

const TYPE_STYLE = {
  drop:  { bg: 'bg-green-50 border border-green-200',  badge: 'bg-green-100 text-green-700',  icon: '📉' },
  spike: { bg: 'bg-red-50 border border-red-200',      badge: 'bg-red-100 text-red-700',      icon: '📈' },
  undercut: { bg: 'bg-yellow-50 border border-yellow-200', badge: 'bg-yellow-100 text-yellow-700', icon: '⚠️' },
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([])

  useEffect(() => { getAlerts().then(setAlerts).catch(() => {}) }, [])

  const handleRead = async (id) => {
    await markAlertRead(id)
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, is_read: true } : a))
    toast.success('Marked as read')
  }

  const unread = alerts.filter(a => !a.is_read).length

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-800">🔔 Price Alerts</h1>
        {unread > 0 && (
          <span className="bg-red-100 text-red-600 text-sm font-semibold px-3 py-1 rounded-full">
            {unread} unread
          </span>
        )}
      </div>

      <div className="space-y-3">
        {alerts.length === 0 && (
          <div className="text-center py-20 text-gray-400">
            <p className="text-4xl mb-3">🔔</p>
            <p>No alerts yet. Run a scrape to detect price changes.</p>
          </div>
        )}

        {alerts.map(alert => {
          const style = TYPE_STYLE[alert.alert_type] || TYPE_STYLE.spike
          return (
            <div key={alert.id} className={`${style.bg} rounded-2xl p-4 transition-opacity ${alert.is_read ? 'opacity-50' : ''}`}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="text-2xl mt-0.5">{style.icon}</span>
                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${style.badge}`}>
                        {alert.alert_type.toUpperCase()}
                      </span>
                      <span className="text-xs font-semibold text-gray-600">{alert.product}</span>
                      <span className="text-xs text-gray-400">via {alert.competitor}</span>
                      {!alert.is_read && <span className="w-2 h-2 bg-blue-500 rounded-full" />}
                    </div>
                    <p className="text-sm text-gray-800">{alert.message}</p>
                    <div className="flex items-center gap-4 mt-2">
                      {alert.old_price && (
                        <span className="text-xs text-gray-400 line-through">₹{alert.old_price}</span>
                      )}
                      {alert.new_price && (
                        <span className={`text-xs font-bold ${alert.alert_type === 'drop' ? 'text-green-600' : 'text-red-600'}`}>
                          ₹{alert.new_price}
                        </span>
                      )}
                      {alert.change_pct && (
                        <span className={`text-xs font-semibold ${alert.change_pct < 0 ? 'text-green-600' : 'text-red-500'}`}>
                          {alert.change_pct > 0 ? '+' : ''}{alert.change_pct}%
                        </span>
                      )}
                      <span className="text-xs text-gray-400">
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                {!alert.is_read && (
                  <button onClick={() => handleRead(alert.id)}
                    className="text-xs text-gray-400 hover:text-gray-700 flex-shrink-0 mt-1">
                    ✓ Mark read
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
