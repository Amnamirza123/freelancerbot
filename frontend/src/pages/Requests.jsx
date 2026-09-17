import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import StatusBadge from '../components/StatusBadge'

export default function Requests() {
  const [requests, setRequests] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    api.listRequests().then(setRequests).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="error">Failed to load requests: {error}</div>

  return (
    <div>
      <h1>Requests</h1>
      <table>
        <thead>
          <tr>
            <th>Caller</th><th>Phone</th><th>Email</th><th>Type</th>
            <th>Developer</th><th>Status</th><th></th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id} className={`type-${r.request_type}`}>
              <td>{r.callers?.name || '—'}</td>
              <td>{r.callers?.phone || '—'}</td>
              <td>{r.proposals?.find(p => p.recipient_email)?.recipient_email || r.callers?.email ||'—'}</td>
              <td>{r.request_type}</td>
              <td>{r.developers?.name || '—'}</td>
              <td><StatusBadge status={r.status} /></td>
              <td><Link to={`/requests/${r.id}`}>View</Link></td>
            </tr>
          ))}
          {requests.length === 0 && (
            <tr><td colSpan={7} className="empty">No requests yet.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}