import { useEffect, useState } from 'react'
import { createClient } from '@supabase/supabase-js'
import { api } from '../services/api'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export default function Approvals() {
  const [proposals, setProposals] = useState([])
  const [error, setError] = useState(null)
  const [approver, setApprover] = useState('')

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setApprover(session?.user?.email || 'unknown')
    })
  }, [])

  const load = () => api.listProposals().then(setProposals).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  const handle = async (id, action) => {
    try {
      if (action === 'approve') await api.approveProposal(id, approver)
      else await api.rejectProposal(id, approver)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  if (error) return <div className="error">{error}</div>

  return (
    <div>
      <h1>Pending Approvals</h1>
      <p>Acting as: <strong>{approver}</strong></p>
      {proposals.map((p) => (
        <div key={p.id} className="proposal-card">
          <p><strong>To:</strong> {p.recipient_email}</p>
          <pre className="draft-content">{p.draft_content}</pre>
          <div className="button-row">
            <button className="approve" onClick={() => handle(p.id, 'approve')}>APPROVE & SEND</button>
            <button className="reject" onClick={() => handle(p.id, 'reject')}>REJECT</button>
          </div>
        </div>
      ))}
      {proposals.length === 0 && <p className="empty">No pending proposals.</p>}
    </div>
  )
}