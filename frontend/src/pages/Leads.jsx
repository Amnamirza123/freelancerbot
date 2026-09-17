import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function Leads() {
  const [leads, setLeads] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => { api.listLeads().then(setLeads).catch((e) => setError(e.message)) }, [])

  if (error) return <div className="error">{error}</div>

  return (
    <div>
      <h1>Leads</h1>
      <table>
        <thead><tr><th>Caller</th><th>Phone</th><th>Service</th><th>Project Description</th><th>Status</th></tr></thead>
        <tbody>
          {leads.map((l) => (
            <tr key={l.id}>
              <td>{l.callers?.name || '—'}</td>
              <td>{l.callers?.phone || '—'}</td>
              <td>{l.service || '—'}</td>
              <td>{l.project_description || '—'}</td>
              <td>{l.status}</td>
            </tr>
          ))}
          {leads.length === 0 && <tr><td colSpan={5} className="empty">No leads yet.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}