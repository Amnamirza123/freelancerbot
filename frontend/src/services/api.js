import { createClient } from '@supabase/supabase-js'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

async function getAuthHeader() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function request(path, options = {}) {
  const authHeader = await getAuthHeader()
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...authHeader },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  return res.json()
}

export const api = {
  health: () => request('/health'),
  dashboardStats: () => request('/dashboard/stats'),

  listRequests: (status) => request(`/requests${status ? `?status=${status}` : ''}`),
  getRequest: (id) => request(`/requests/${id}`),
  updateRequest: (id, payload) =>
    request(`/requests/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  listProposals: () => request('/proposals'),
  approveProposal: (id, approvedBy) =>
    request(`/proposals/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approved_by: approvedBy }),
    }),
  rejectProposal: (id, approvedBy) =>
    request(`/proposals/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ approved_by: approvedBy }),
    }),

  listAppointments: () => request('/appointments'),
  confirmMeeting: (id) => request(`/meetings/${id}/confirm`, { method: 'POST' }),
  declineMeeting: (id) => request(`/meetings/${id}/decline`, { method: 'POST' }),

  listEscalations: (status) => request(`/escalations${status ? `?status=${status}` : ''}`),
  resolveEscalation: (id, assignedHuman) =>
    request(`/escalations/${id}/resolve?assigned_human=${encodeURIComponent(assignedHuman)}`, {
      method: 'POST',
    }),

  listLeads: () => request('/leads'),
  listDevelopers: () => request('/developers'),

  listKnowledgeBase: (category) =>
    request(`/knowledge-base${category ? `?category=${category}` : ''}`),
  createKnowledgeBase: (category, content, sourceLabel) =>
    request('/knowledge-base', {
      method: 'POST',
      body: JSON.stringify({ category, content, source_label: sourceLabel }),
    }),
  updateKnowledgeBase: (id, content) =>
    request(`/knowledge-base/${id}`, { method: 'PUT', body: JSON.stringify({ content }) }),
  deleteKnowledgeBase: (id) => request(`/knowledge-base/${id}`, { method: 'DELETE' }),

  uploadKnowledgeBaseFile: async (category, file) => {
    const authHeader = await getAuthHeader()
    const formData = new FormData()
    formData.append('category', category)
    formData.append('file', file)
    return fetch(`${API_URL}/knowledge-base/upload`, {
      method: 'POST',
      headers: authHeader,
      body: formData,
    }).then((res) => {
      if (!res.ok) return res.text().then((t) => { throw new Error(t) })
      return res.json()
    })
  },
}