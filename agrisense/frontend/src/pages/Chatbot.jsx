import { useState, useRef, useEffect } from 'react'
import { Send, RotateCcw, Loader2 } from 'lucide-react'
import { chatApi } from '../api/services'
import { getProfile } from '../utils/farmerProfile'

const LANGUAGES = [
  { code: '', label: 'Auto-detect' },
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी (Hindi)' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
  { code: 'mr', label: 'मराठी (Marathi)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
]

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Namaste! Ask me about weather, crops, soil, irrigation, or anything else on your farm.' },
  ])
  const [input, setInput] = useState('')
  const [language, setLanguage] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const send = async (text) => {
    if (!text.trim() || sending) return
    setError(null)

    // Conversation memory lives in this component's state (per browser tab),
    // not on the server — we send recent turns with each request. The new
    // user message isn't added to `history` sent to the backend since the
    // backend appends it itself; we still show it in the UI immediately.
    const historyForRequest = messages
      .filter((m) => !m.isError)
      .map((m) => ({ role: m.role, content: m.content }))

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setInput('')
    setSending(true)
    try {
      const profile = getProfile()
      const res = await chatApi.send(text, {
        language: language || undefined,
        history: historyForRequest,
        farmerProfile: profile,
      })
      setMessages((prev) => [...prev, { role: 'assistant', content: res.data.reply, sources: res.data.sources }])
    } catch (err) {
      setError(err.message)
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'AI assistant is temporarily unavailable. Please try again.',
        isError: true,
      }])
    } finally {
      setSending(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    send(input)
  }

  const clearConversation = () => {
    setMessages([{ role: 'assistant', content: 'New conversation started. What would you like to know?' }])
    setError(null)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-4rem)]">
      <div className="flex items-center justify-between pb-4 border-b border-foliage-100 mb-4">
        <h1 className="font-display text-2xl text-foliage-900">AI Chatbot</h1>
        <div className="flex items-center gap-2">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="text-sm border border-foliage-100 rounded-xs px-2 py-1.5 bg-white"
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
          <button
            onClick={clearConversation}
            className="flex items-center gap-1.5 text-sm text-foliage-800 hover:text-foliage-900 px-2 py-1.5"
          >
            <RotateCcw size={15} /> New chat
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] md:max-w-[70%] rounded-xs px-4 py-3 text-sm whitespace-pre-wrap ${
                m.role === 'user'
                  ? 'bg-foliage-800 text-white'
                  : m.isError
                  ? 'bg-clay-400/10 border border-clay-400/40 text-ink'
                  : 'bg-white border border-foliage-100 text-ink'
              }`}
            >
              {m.content}
              {m.sources?.length > 0 && (
                <div className="mt-2 pt-2 border-t border-foliage-100/60 text-xs text-ink/50">
                  Sources: {m.sources.map((s, si) => (
                    <span key={si}>{s.type === 'weather_api' ? `Live weather (${s.provider})` : s.source}{si < m.sources.length - 1 ? ', ' : ''}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-white border border-foliage-100 rounded-xs px-4 py-3 flex items-center gap-2 text-sm text-ink/60">
              <Loader2 size={15} className="animate-spin" /> AgriSense is thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 pt-2 border-t border-foliage-100">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about weather, crops, soil, irrigation…"
          className="flex-1 border border-foliage-100 rounded-xs px-4 py-3 text-sm focus:border-foliage-700 outline-none bg-white"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="bg-foliage-800 text-white rounded-xs px-4 py-3 hover:bg-foliage-900 disabled:opacity-50"
          aria-label="Send"
        >
          <Send size={18} />
        </button>
      </form>
      <p className="text-xs text-ink/40 mt-2">
        This conversation is only kept in this browser tab — it isn't saved anywhere. Refreshing the page starts fresh.
      </p>
    </div>
  )
}
