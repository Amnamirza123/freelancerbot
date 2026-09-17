const COLORS = {
  new_call: '#94a3b8', processing: '#60a5fa', needs_approval: '#fbbf24',
  waiting_for_developer: '#fb923c', proposal_sent: '#a78bfa', meeting_booked: '#34d399',
  closed: '#4b5563', escalated: '#f87171', rejected: '#f87171',
  pending_approval: '#fbbf24', approved: '#34d399', sent: '#34d399',
  confirmed: '#34d399', proposed: '#60a5fa', declined: '#f87171', cancelled: '#4b5563',
  open: '#f87171', in_review: '#fbbf24', resolved: '#34d399',
}

const PULSING_STATUSES = new Set([
  'new_call', 'needs_approval', 'waiting_for_developer', 'pending_approval',
  'proposed', 'open', 'in_review',
])

export default function StatusBadge({ status }) {
  const color = COLORS[status] || '#94a3b8'
  const isPulsing = PULSING_STATUSES.has(status)
  return (
    <span
      className={`status-badge${isPulsing ? ' status-pulse' : ''}`}
      style={{ backgroundColor: `${color}22`, color }}
    >
      {status?.replaceAll('_', ' ')}
    </span>
  )
}