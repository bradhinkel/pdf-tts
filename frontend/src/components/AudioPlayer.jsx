import { useState, useEffect, useRef } from 'react'

function fmt(s) {
  if (!isFinite(s) || s < 0) return '--:--'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

// User-selectable TTS engines. XTTS stays dev-only via ?tts=xtts URL override.
const ENGINES = [
  { id: 'piper', label: 'Piper' },
  { id: 'azure', label: 'Azure' },
]

// Initial engine: URL flag wins (also allows ?tts=xtts), else last choice, else Piper.
function initialEngine() {
  const flag = new URLSearchParams(window.location.search).get('tts')
  return flag || localStorage.getItem('tts-engine') || 'piper'
}

export default function AudioPlayer({ filename, onClose }) {
  const audioRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [engine, setEngine] = useState(initialEngine)

  // Restore saved position when filename changes
  useEffect(() => {
    const saved = parseFloat(localStorage.getItem(`pos:${filename}`)) || 0
    setCurrentTime(saved)
    setIsPlaying(false)
  }, [filename])

  // Persist engine choice across sessions
  useEffect(() => {
    localStorage.setItem('tts-engine', engine)
  }, [engine])

  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return
    if (isPlaying) {
      audio.pause()
    } else {
      audio.play().catch((err) => {
        console.error('Playback error:', err)
        setIsPlaying(false)
      })
    }
  }

  const onSeek = (e) => {
    const t = parseFloat(e.target.value)
    if (audioRef.current) audioRef.current.currentTime = t
    setCurrentTime(t)
  }

  const pct = duration > 0 ? (currentTime / duration) * 100 : 0

  const src =
    `/api/stream-audio?filename=${encodeURIComponent(filename)}&tts=${encodeURIComponent(engine)}`

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-2xl z-20 pb-safe">
      <audio
        ref={audioRef}
        src={src}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onTimeUpdate={(e) => {
          const t = e.target.currentTime
          setCurrentTime(t)
          localStorage.setItem(`pos:${filename}`, t)
        }}
        onDurationChange={(e) => setDuration(e.target.duration)}
        onEnded={() => setIsPlaying(false)}
      />

      {/* Progress bar */}
      <div className="relative h-1 bg-gray-200 cursor-pointer">
        <div className="absolute h-full bg-blue-500 transition-all" style={{ width: `${pct}%` }} />
        <input
          type="range"
          min={0}
          max={duration || 0}
          step={1}
          value={currentTime}
          onChange={onSeek}
          className="absolute inset-0 w-full opacity-0 cursor-pointer h-full"
          aria-label="Seek"
        />
      </div>

      <div className="max-w-2xl mx-auto px-4 py-3">
        {/* Title row */}
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-gray-900 truncate flex-1 mr-3">{filename}</p>
          <button
            onClick={onClose}
            aria-label="Close player"
            className="text-gray-400 hover:text-gray-600 p-1"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Voice engine toggle */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs text-gray-400">Voice</span>
          <div className="inline-flex rounded-full bg-gray-100 p-0.5">
            {ENGINES.map((e) => (
              <button
                key={e.id}
                onClick={() => setEngine(e.id)}
                aria-pressed={engine === e.id}
                className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                  engine === e.id ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {e.label}
              </button>
            ))}
          </div>
        </div>

        {/* Controls row */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400 w-10 tabular-nums">{fmt(currentTime)}</span>

          <div className="flex-1 flex justify-center">
            <button
              onClick={togglePlay}
              aria-label={isPlaying ? 'Pause' : 'Play'}
              className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 active:scale-95 transition-transform shadow-md"
            >
              {isPlaying ? (
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 ml-0.5">
                  <path d="M8 5v14l11-7z" />
                </svg>
              )}
            </button>
          </div>

          <span className="text-xs text-gray-400 w-10 tabular-nums text-right">{fmt(duration)}</span>
        </div>
      </div>
    </div>
  )
}
