import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, ListTodo, CheckCircle2, CalendarClock,
  AlertTriangle,BookOpen, LogOut,
} from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', end: true, icon: LayoutDashboard },
  { to: '/requests', label: 'Requests', icon: ListTodo },
  { to: '/approvals', label: 'Pending Approvals', icon: CheckCircle2 },
  { to: '/meetings', label: 'Meetings', icon: CalendarClock },
  { to: '/escalations', label: 'Escalations', icon: AlertTriangle },
 
]

export default function Sidebar({ isAdmin, onLogout }) {
  const allLinks = isAdmin
    ? [...links, { to: '/knowledge-base', label: 'Knowledge Base', icon: BookOpen }]
    : links

  return (
    <nav className="sidebar">
      <div className="sidebar-brand">FreelancerBot</div>
      <ul>
        {allLinks.map((link) => {
          const Icon = link.icon
          return (
            <li key={link.to}>
              <NavLink to={link.to} end={link.end} className={({ isActive }) => (isActive ? 'active' : '')}>
                <Icon size={17} strokeWidth={2} />
                <span>{link.label}</span>
              </NavLink>
            </li>
          )
        })}
      </ul>
      <button className="logout-btn" onClick={onLogout}>
        <LogOut size={16} strokeWidth={2} />
        <span>Log Out</span>
      </button>
    </nav>
  )
}