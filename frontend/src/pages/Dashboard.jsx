import { useEffect, useState, useRef } from 'react'
import Chart from 'chart.js/auto'
import { api } from '../services/api'
import StatCard from '../components/StatCard'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const chartRef = useRef(null)

  useEffect(() => {
    api.dashboardStats().then(setStats).catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    if (!stats || !chartRef.current) return
    const chart = new Chart(chartRef.current, {
      type: 'bar',
      data: {
        labels: ['Pending approvals', 'Meetings booked', 'Open escalations', 'Total leads'],
        datasets: [{
          data: [stats.pending_approvals, stats.meetings_booked, stats.open_escalations, stats.total_leads],
          backgroundColor: ['#eb6834', '#1baf7a', '#e34948', '#2a78d6'],
          borderRadius: 4,
          barThickness: 32,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1, color: '#64748b' }, grid: { color: '#1e293b' } },
          x: { ticks: { color: '#64748b' }, grid: { display: false } },
        },
      },
    })
    return () => chart.destroy()
  }, [stats])

  if (error) return <div className="error">Failed to load stats: {error}</div>
  if (!stats) return <div>Loading...</div>

  return (
    <div>
      <h1>Dashboard</h1>
      <div className="stat-grid">
        <StatCard label="Total Calls" value={stats.total_calls} />
        <StatCard label="Pending Approvals" value={stats.pending_approvals} />
        <StatCard label="Meetings Booked" value={stats.meetings_booked} />
        <StatCard label="Open Escalations" value={stats.open_escalations} />
        <StatCard label="Total Leads" value={stats.total_leads} />
      </div>

      <div style={{ background: '#131c2e', border: '1px solid #1e293b', borderRadius: 12, padding: '1.5rem', marginTop: '2rem', height: 300 }}>
        <canvas ref={chartRef}></canvas>
      </div>
    </div>
  )
}