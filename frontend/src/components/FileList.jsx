function formatSize(bytes) {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${Math.round(bytes / 1024)} KB`
}

function PlayIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
      <path d="M8 5v14l11-7z" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  )
}

export default function FileList({ pdfs, playing, onPlay, onDelete }) {
  if (pdfs.length === 0) {
    return (
      <p className="text-center text-sm text-gray-400 py-10">
        No PDFs yet — upload one above.
      </p>
    )
  }

  return (
    <div className="space-y-2">
      {pdfs.map((pdf) => {
        const isPlaying = playing === pdf.name
        return (
          <div
            key={pdf.name}
            className={`bg-white rounded-2xl px-4 py-3 flex items-center gap-3 border transition-colors ${
              isPlaying ? 'border-blue-400 shadow-md' : 'border-gray-100 shadow-sm'
            }`}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{pdf.name}</p>
              <p className="text-xs text-gray-400 mt-0.5">{formatSize(pdf.size)}</p>
            </div>

            <button
              onClick={() => onPlay(pdf.name)}
              aria-label={`Play ${pdf.name}`}
              className={`flex items-center justify-center w-9 h-9 rounded-full transition-colors ${
                isPlaying
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-500 hover:bg-blue-50 hover:text-blue-600'
              }`}
            >
              <PlayIcon />
            </button>

            <button
              onClick={() => onDelete(pdf.name)}
              aria-label={`Delete ${pdf.name}`}
              className="flex items-center justify-center w-9 h-9 rounded-full bg-gray-100 text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
            >
              <TrashIcon />
            </button>
          </div>
        )
      })}
    </div>
  )
}
