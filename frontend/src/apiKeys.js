const OPENAI_KEY = 'research_assistant_openai_key'
const TAVILY_KEY = 'research_assistant_tavily_key'

export function loadApiKeys() {
  return {
    openai: localStorage.getItem(OPENAI_KEY) || '',
    tavily: localStorage.getItem(TAVILY_KEY) || '',
  }
}

export function saveApiKeys({ openai, tavily }) {
  localStorage.setItem(OPENAI_KEY, openai)
  localStorage.setItem(TAVILY_KEY, tavily)
}

export function hasApiKeys(keys) {
  return Boolean(keys.openai && keys.tavily)
}
