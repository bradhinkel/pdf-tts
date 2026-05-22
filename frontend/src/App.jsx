import { useState, useEffect, useCallback } from 'react'
import FileUploadZone from './components/FileUploadZone'
import FileList from './components/FileList'
import AudioPlayer from './components/AudioPlayer'

export default function App() {
  const [pdfs, setPdfs] = useState([])
  const [playing, setPlaying] = useState(() => localStorage.getItem('playing') || null)

  const fetchPdfs = useCallback(async () => {
    try {
      const res = await fetch('/api/list-pdfs')
      const data = await res.json()
      setPdfs(data.pdfs)
    } catch (e) {
      console.error('Failed to fetch PDFs', e)
    }
  }, [])

  useEffect(() => { fetchPdfs() }, [fetchPdfs])

  useEffect(() => {
    if (playing) localStorage.setItem('playing', playing)
    else localStorage.removeItem('playing')
  }, [playing])

  const handleDelete = async (filename) => {
    await fetch(`/api/pdf/${encodeURIComponent(filename)}`, { method: 'DELETE' })
    if (playing === filename) setPlaying(null)
    fetchPdfs()
  }

  return (
    <div className="min-h-screen bg-gray-50" style={{ paddingBottom: playing ? '9rem' : '1.5rem' }}>
      <header className="bg-white border-b border-gray-200 px-4 py-4 sticky top-0 z-10 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">PDF Reader</h1>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <FileUploadZone onUpload={fetchPdfs} />
        <FileList
          pdfs={pdfs}
          playing={playing}
          onPlay={setPlaying}
          onDelete={handleDelete}
        />
      </main>

      {playing && (
        <AudioPlayer
          filename={playing}
          onClose={() => setPlaying(null)}
        />
      )}
    </div>
  )
}
