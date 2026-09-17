import { useEffect, useState } from 'react'
import { api } from '../services/api'



const CATEGORIES = ['services', 'pricing', 'technologies', 'packages', 'policies', 'faq']

export default function KnowledgeBase() {
  const [entries, setEntries] = useState([])
  const [error, setError] = useState(null)
  const [category, setCategory] = useState('services')
  const [content, setContent] = useState('')
  const [label, setLabel] = useState('')
  const [file, setFile] = useState(null)  
  const load = () => api.listKnowledgeBase().then(setEntries).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  const handleAdd = async () => {
    if (!content.trim()) return
    try {
      await api.createKnowledgeBase(category, content, label || undefined)
      setContent('')
      setLabel('')
      load()
    } catch (e) { setError(e.message) }
  }

    const handleUpload = async () => {
    if (!file) return
    try {
      await api.uploadKnowledgeBaseFile(category, file)
      setFile(null)
      load()
    } catch (e) { setError(e.message) }
  }

  const handleDelete = async (id) => {
    try { await api.deleteKnowledgeBase(id); load() } catch (e) { setError(e.message) }
  }

  return (
    <div>
      <h1>Knowledge Base</h1>
      {error && <div className="error">{error}</div>}

      <div className="proposal-card">
        <h3>Add new entry</h3>
        <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ marginBottom: 8 }}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <input
          placeholder="Label (optional, e.g. 'Q1 2026 Pricing')"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          style={{ display: 'block', width: '100%', marginBottom: 8, padding: 6 }}
        />
        <textarea
          rows={6}
          placeholder="Paste or write the document content here..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          style={{ width: '100%', padding: 8 }}
        />
                <div style={{ margin: '12px 0', color: '#94a3b8', fontSize: '0.85rem' }}>— or —</div>
        <input
          type="file"
          accept=".pdf,.docx,.txt,.md"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ marginBottom: 8 }}
        />
        <div className="button-row">
                  <div className="button-row">
          <button className="approve" onClick={handleAdd}>Save & Embed Text</button>
          <button className="approve" onClick={handleUpload} disabled={!file}>Upload & Embed File</button>
        </div>
        </div>
      </div>

      <h3 style={{ marginTop: '1.5rem' }}>Existing entries</h3>
      <table>
        <thead><tr><th>Category</th><th>Content</th><th>Updated</th><th></th></tr></thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.id}>
              <td>{e.category}</td>
              <td style={{ maxWidth: 400 }}>{e.content.slice(0, 120)}{e.content.length > 120 ? '…' : ''}</td>
              <td>{new Date(e.updated_at).toLocaleDateString()}</td>
              <td><button className="reject" onClick={() => handleDelete(e.id)}>Delete</button></td>
            </tr>
          ))}
          {entries.length === 0 && <tr><td colSpan={4} className="empty">No entries yet.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}