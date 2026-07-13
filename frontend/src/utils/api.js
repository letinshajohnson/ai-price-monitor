import axios from 'axios'
const api = axios.create({ baseURL: '/api' })
export const getStats        = ()         => api.get('/stats').then(r => r.data)
export const getIntelligence = ()         => api.get('/intelligence').then(r => r.data)
export const getAlerts       = ()         => api.get('/alerts').then(r => r.data)
export const markAlertRead   = (id)       => api.post(`/alerts/${id}/read`).then(r => r.data)
export const getProducts     = ()         => api.get('/products').then(r => r.data)
export const addProduct      = (data)     => api.post('/products', data).then(r => r.data)
export const getPriceHistory = (id, days) => api.get(`/products/${id}/history?days=${days}`).then(r => r.data)
export const triggerScrape   = ()         => api.post('/scrape').then(r => r.data)
export default api
