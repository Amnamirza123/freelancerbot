import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import StatusBadge from '../components/StatusBadge'

export default function RequestDetail() {
  const { id } = useParams()
  const [request, setRequest] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getRequest(id).then(setRequest).catch((e) => setError(e.message))
  }, [id])

  if (error) return <div className="error">Failed to load request: {error}</div>
  if (!request) return <div>Loading...</div>

  return (
    <div>
      <Link to="/requests">&larr; Back to Requests</Link>
      <h1>Request Detail</h1>

      <div className="detail-grid">
        <div>
          <h3>Caller</h3>
          <p>{request.callers?.name || '—'}</p>
          <p>{request.callers?.phone || '—'}</p>
          <p>{request.callers?.email || '—'}</p>
        </div>
        <div>
          <h3>Status</h3>
          <StatusBadge status={request.status} />
          <p>Type: {request.request_type}</p>
          <p>Priority: {request.priority}</p>
        </div>
        <div>
          <h3>Assigned Developer</h3>
          <p>{request.developers?.name || 'Unassigned'}</p>
        </div>
      </div>

      <h3>Project Requirements</h3>
      <p>{request.project_requirements || 'None recorded.'}</p>

      <h3>Activity Timeline</h3>
      <ul className="timeline">
        <li>Created: {new Date(request.created_at).toLocaleString()}</li>
        <li>Last updated: {new Date(request.updated_at).toLocaleString()}</li>
      </ul>
    </div>
  )
}