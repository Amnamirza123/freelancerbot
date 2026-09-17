import { useEffect, useState } from 'react'
import { createClient } from '@supabase/supabase-js'
import { api } from '../services/api'
import StatusBadge from '../components/StatusBadge'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export default function Escalations() {
  const [escalations, setEscalations] = useState([])
  const [error, setError] = useState(null)
  const [assignee, setAssignee] = useState('')

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setAssignee(session?.user?.email || 'unknown')
    })
  }, [])

  const load = () => api.listEscalations().then(setEscalations).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  const resolve = async (id) => {
    try { await api.resolveEscalation(id, assignee); load() } catch (e) { setError(e.message) }
  }

  if (error) return <div className="error">{error}</div>

  return (
    <div>
      <h1>Escalations</h1>
      <p>Resolving as: <strong>{assignee}</strong></p>
      <table>
        <thead><tr><th>Reason</th><th>Priority</th><th>Status</th><th>Assigned</th><th></th></tr></thead>
        <tbody>
          {escalations.map((e) => (
            <tr key={e.id}>
              <td>{e.reason}</td>
              <td>{e.priority}</td>
              <td><StatusBadge status={e.status} /></td>
              <td>{e.assigned_human || '—'}</td>
              <td>{e.status === 'open' && <button className="approve" onClick={() => resolve(e.id)}>Resolve</button>}</td>
            </tr>
          ))}
          {escalations.length === 0 && <tr><td colSpan={5} className="empty">No escalations.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}