import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { createClient } from '@supabase/supabase-js'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Requests from './pages/Requests'
import RequestDetail from './pages/RequestDetail'
import Approvals from './pages/Approvals'
import Meetings from './pages/Meetings'
import Escalations from './pages/Escalations'
import Leads from './pages/Leads'
import KnowledgeBase from './pages/KnowledgeBase'
import Login from './pages/Login'
import './App.css'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export default function App() {
  const [session, setSession] = useState(undefined) // undefined = loading
  const [role, setRole] = useState('employee')

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setRole(session?.user?.user_metadata?.role || 'employee')
    })
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setRole(session?.user?.user_metadata?.role || 'employee')
    })
    return () => listener.subscription.unsubscribe()
  }, [])

  if (session === undefined) return null // or a loading spinner

  if (!session) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="*" element={<Login />} />
        </Routes>
      </BrowserRouter>
    )
  }

  return (
    <BrowserRouter>
      <div className="layout">
        <Sidebar isAdmin={role === 'admin'} onLogout={() => supabase.auth.signOut()} />
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/requests" element={<Requests />} />
            <Route path="/requests/:id" element={<RequestDetail />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/meetings" element={<Meetings />} />
            <Route path="/escalations" element={<Escalations />} />
            <Route path="/leads" element={<Leads />} />
            <Route
              path="/knowledge-base"
              element={role === 'admin' ? <KnowledgeBase /> : <Navigate to="/" replace />}
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}