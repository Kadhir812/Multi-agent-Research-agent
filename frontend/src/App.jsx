import { useEffect, useState } from 'react'
import ApiKeyModal from './ApiKeyModal'
import { hasApiKeys, loadApiKeys, saveApiKeys } from './apiKeys'
import { API_BASE } from './apiBase'
import './App.css'

const EMPTY_RESULT = {
  content: '',
  sources: [],
  confidence: 0,
}

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100)
  return (
    <div className="confidence">
      <div className="confidence-track">
        <div className="confidence-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="confidence-label">{pct}%</span>
    </div>
  )
}

function AgentCard({ title, result }) {
  const r = result || EMPTY_RESULT
  const hasContent = Boolean(r.content)

  return (
    <div className={`agent-card ${hasContent ? '' : 'agent-card--empty'}`}>
      <div className="agent-card-header">
        <h3>{title}</h3>
        <ConfidenceBar value={r.confidence} />
      </div>
      <p className="agent-card-content">
        {hasContent ? r.content : 'No contribution for this question.'}
      </p>
      {r.sources.length > 0 && (
        <ul className="agent-card-sources">
          {r.sources.map((source, i) => (
            <li key={i}>{source}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

function DocumentList({ documents }) {
  return (
    <div className="upload-panel">
      <div className="upload-panel-header">
        <h3>Documents</h3>
      </div>

      {documents.length > 0 ? (
        <ul className="document-list">
          {documents.map((doc) => (
            <li key={doc}>{doc}</li>
          ))}
        </ul>
      ) : (
        <p className="document-empty">No documents available — the docs agent has nothing to search.</p>
      )}
    </div>
  )
}

export default function App() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [documents, setDocuments] = useState([])
  const [apiKeys, setApiKeys] = useState(() => loadApiKeys())
  const [showKeyModal, setShowKeyModal] = useState(() => !hasApiKeys(loadApiKeys()))

  function handleSaveKeys(keys) {
    saveApiKeys(keys)
    setApiKeys(keys)
    setShowKeyModal(false)
  }

  async function loadDocuments() {
    try {
      const res = await fetch(`${API_BASE}/documents`)
      if (!res.ok) return
      const data = await res.json()
      setDocuments(data.documents)
    } catch {
      // ignore — document list is a non-critical enhancement
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!question.trim() || loading) return

    if (!hasApiKeys(apiKeys)) {
      setShowKeyModal(true)
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-OpenAI-Key': apiKeys.openai,
          'X-Tavily-Key': apiKeys.tavily,
          ...(apiKeys.langchain ? { 'X-Langchain-Key': apiKeys.langchain } : {}),
        },
        body: JSON.stringify({ question }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => null)
        throw new Error(body?.detail || `Request failed with status ${res.status}`)
      }

      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      {showKeyModal && (
        <ApiKeyModal
          initialKeys={apiKeys}
          dismissible={hasApiKeys(apiKeys)}
          onSave={handleSaveKeys}
          onDismiss={() => setShowKeyModal(false)}
        />
      )}

      <header className="hero">
        <div className="hero-top">
          <span />
          <button type="button" className="keys-button" onClick={() => setShowKeyModal(true)}>
            🔑 API Keys
          </button>
        </div>
        <h1>Research Assistant</h1>
        <p>Ask a question — web, docs, and math agents collaborate on the answer.</p>
      </header>

      <DocumentList documents={documents} />

      <form className="ask-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. What is the population of France plus 15% growth?"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>

      {error && <div className="error-banner">{error}</div>}

      {result && (
        <section className="results">
          <div className="final-answer">
            <div className="final-answer-header">
              <h2>Answer</h2>
              <ConfidenceBar value={result.confidence_score} />
            </div>
            <p>{result.final_answer}</p>
            {result.sources.length > 0 && (
              <div className="final-sources">
                <span>Sources:</span>
                <ul>
                  {result.sources.map((source, i) => (
                    <li key={i}>{source}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="agent-grid">
            <AgentCard title="Web" result={result.web_result} />
            <AgentCard title="Docs" result={result.docs_result} />
            <AgentCard title="Math" result={result.math_result} />
          </div>
        </section>
      )}
    </div>
  )
}
