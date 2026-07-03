const OPENAI_KEY = 'research_assistant_openai_key'
const TAVILY_KEY = 'research_assistant_tavily_key'
const LANGCHAIN_KEY = 'research_assistant_langchain_key'

export function loadApiKeys() {
  return {
    openai: localStorage.getItem(OPENAI_KEY) || '',
    tavily: localStorage.getItem(TAVILY_KEY) || '',
    langchain: localStorage.getItem(LANGCHAIN_KEY) || '',
  }
}

export function saveApiKeys({ openai, tavily, langchain }) {
  localStorage.setItem(OPENAI_KEY, openai)
  localStorage.setItem(TAVILY_KEY, tavily)
  localStorage.setItem(LANGCHAIN_KEY, langchain || '')
}

export function hasApiKeys(keys) {
  return Boolean(keys.openai && keys.tavily)
}
