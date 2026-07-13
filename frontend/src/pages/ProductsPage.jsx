import { useEffect, useState } from 'react'
import { getProducts, addProduct } from '../utils/api'
import toast from 'react-hot-toast'

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [form, setForm]         = useState({ name: '', our_price: '', category: '' })
  const [loading, setLoading]   = useState(false)

  useEffect(() => { getProducts().then(setProducts).catch(() => {}) }, [])

  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const handleAdd = async () => {
    if (!form.name || !form.our_price) { toast.error('Name and price required'); return }
    setLoading(true)
    try {
      const result = await addProduct({ ...form, our_price: parseFloat(form.our_price) })
      toast.success(`Added! AI normalized: "${result.normalized_name}" → ${result.category}`)
      getProducts().then(setProducts)
      setForm({ name: '', our_price: '', category: '' })
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to add product')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold text-gray-800 mb-6">🛍️ Tracked Products ({products.length})</h1>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Product list */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {["Product Name", "Category", "Our Price"].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {products.map((p, i) => (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-800">{p.name}</td>
                  <td className="px-4 py-3">
                    {p.category
                      ? <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-semibold">{p.category}</span>
                      : <span className="text-gray-300 text-xs">—</span>
                    }
                  </td>
                  <td className="px-4 py-3 font-bold text-blue-700">₹{p.our_price}</td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-4 py-16 text-center text-gray-400">
                    <p className="text-3xl mb-2">🛍️</p>
                    <p>No products yet. Add one to start tracking.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Add product form */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5 h-fit">
          <h2 className="font-bold text-gray-800 mb-1">Add Product</h2>
          <p className="text-xs text-gray-400 mb-4">
            AI will automatically normalize the name and categorize it.
          </p>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Product Name</label>
              <input value={form.name} onChange={set('name')}
                placeholder="e.g. Amul Butter 100 gms"
                className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Our Price (₹)</label>
              <input value={form.our_price} onChange={set('our_price')}
                placeholder="55.00" type="number"
                className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Category (optional)</label>
              <input value={form.category} onChange={set('category')}
                placeholder="AI will guess if left empty"
                className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <button onClick={handleAdd} disabled={loading}
              className="w-full bg-blue-700 text-white font-semibold py-2.5 rounded-xl hover:bg-blue-800 transition-colors disabled:opacity-40">
              {loading ? '🤖 AI Processing...' : '+ Add & Normalize with AI'}
            </button>
          </div>

          <div className="mt-4 bg-blue-50 rounded-xl p-3">
            <p className="text-xs font-semibold text-blue-700 mb-1">🤖 AI Does This Automatically:</p>
            <ul className="text-xs text-blue-600 space-y-0.5">
              <li>• Normalizes name ("100 gms" → "100g")</li>
              <li>• Fixes capitalization</li>
              <li>• Assigns product category</li>
              <li>• Matches to competitor products</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
