import { useState } from 'react'

export default function ApiKeyModal({ initialKeys, dismissible, onSave, onDismiss }) {
  const [openai, setOpenai] = useState(initialKeys.openai)
  const [tavily, setTavily] = useState(initialKeys.tavily)
  const [langchain, setLangchain] = useState(initialKeys.langchain || '')

  function handleSubmit(e) {
    e.preventDefault()
    if (!openai.trim() || !tavily.trim()) return
    onSave({ openai: openai.trim(), tavily: tavily.trim(), langchain: langchain.trim() })
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Add your API keys</h2>
        <p className="modal-subtitle">
          This app runs your questions through OpenAI and Tavily. Your keys are stored only in
          this browser and sent directly to the backend with each request — never saved server-side.
        </p>

        <form onSubmit={handleSubmit}>
          <label>
            OpenAI API key
            <input
              type="password"
              value={openai}
              onChange={(e) => setOpenai(e.target.value)}
              placeholder="sk-..."
              autoComplete="off"
            />
          </label>

          <label>
            Tavily API key
            <input
              type="password"
              value={tavily}
              onChange={(e) => setTavily(e.target.value)}
              placeholder="tvly-..."
              autoComplete="off"
            />
          </label>

          <label>
            LangSmith API key (optional, for tracing)
            <input
              type="password"
              value={langchain}
              onChange={(e) => setLangchain(e.target.value)}
              placeholder="lsv2_pt_..."
              autoComplete="off"
            />
          </label>

          <div className="modal-actions">
            {dismissible && (
              <button type="button" className="modal-cancel" onClick={onDismiss}>
                Cancel
              </button>
            )}
            <button type="submit" className="modal-save" disabled={!openai.trim() || !tavily.trim()}>
              Save keys
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
