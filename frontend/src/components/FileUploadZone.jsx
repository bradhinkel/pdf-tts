import { useState, useRef } from 'react'

export default function FileUploadZone({ onUpload }) {
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const upload = async (file) => {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file')
      return
    }
    setError(null)
    setProgress(0)

    const form = new FormData()
    form.append('file', file)

    try {
      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) setProgress(Math.round((e.loaded / e.total) * 100))
        }
        xhr.onload = () => {
          if (xhr.status < 300) resolve()
          else {
            const msg = JSON.parse(xhr.responseText)?.detail || 'Upload failed'
            reject(new Error(msg))
          }
        }
        xhr.onerror = () => reject(new Error('Network error'))
        xhr.open('POST', '/api/upload')
        xhr.send(form)
      })
      setProgress(null)
      onUpload()
    } catch (e) {
      setError(e.message)
      setProgress(null)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    upload(e.dataTransfer.files[0])
  }

  return (
    <div
      className={`border-2 border-dashed rounded-2xl p-8 text-center transition-colors ${
        dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'
      }`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        className="hidden"
        onChange={(e) => { upload(e.target.files[0]); e.target.value = '' }}
      />

      <p className="text-gray-500 text-sm mb-3">Drag a PDF here or</p>
      <button
        onClick={() => inputRef.current.click()}
        className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 active:scale-95 transition-transform"
      >
        Choose File
      </button>

      {progress !== null && (
        <div className="mt-4 space-y-1">
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-200"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-400">Uploading… {progress}%</p>
        </div>
      )}

      {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
    </div>
  )
}
