import { useEffect, useState } from 'react'
import { api } from '../services/api'
import StatusBadge from '../components/StatusBadge'

export default function Meetings() {
  const [appointments, setAppointments] = useState([])
  const [error, setError] = useState(null)

  const load = () => api.listAppointments().then(setAppointments).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  const handle = async (id, action) => {
    try {
      if (action === 'confirm') await api.confirmMeeting(id)
      else await api.declineMeeting(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  if (error) return <div className="error">{error}</div>

  return (
    <div>
      <h1>Meetings</h1>
      <table>
        <thead>
          <tr><th>Client</th><th>Developer</th><th>Date</th><th>Time</th><th>Status</th><th></th></tr>
        </thead>
        <tbody>
          {appointments.map((a) => (
            <tr key={a.id}>
              <td>{a.callers?.name || '—'}</td>
              <td>{a.developers?.name || 'Any Developer'}</td>
              <td>{a.date}</td>
              <td>{a.start_time} - {a.end_time}</td>
              <td><StatusBadge status={a.status} /></td>
              <td>
                {a.status === 'proposed' && (
                  <div className="button-row">
                    <button className="approve" onClick={() => handle(a.id, 'confirm')}>Take & Confirm</button>
                    <button className="reject" onClick={() => handle(a.id, 'decline')}>Decline</button>
                  </div>
                )}
              </td>
            </tr>
          ))}
          {appointments.length === 0 && <tr><td colSpan={6} className="empty">No meetings yet.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
