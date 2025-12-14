import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import axios from 'axios'

interface FileUploadProps {
  onTaskCreated: (taskId: string) => void
}

interface UploadFile extends File {
  preview?: string
}

const FileUpload: React.FC<FileUploadProps> = ({ onTaskCreated }) => {
  const [files, setFiles] = useState<UploadFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [language, setLanguage] = useState('')
  const [translateTo, setTranslateTo] = useState('')

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles.map(file => Object.assign(file, {
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }))])
  }, [])

  const removeFile = (fileToRemove: UploadFile) => {
    setFiles(prev => prev.filter(file => file !== fileToRemove))
    if (fileToRemove.preview) {
      URL.revokeObjectURL(fileToRemove.preview)
    }
  }

  const uploadFiles = async () => {
    if (files.length === 0) {
      toast.error('Please select files to upload')
      return
    }

    setIsUploading(true)
    
    try {
      // Upload first file (for demo purposes)
      const file = files[0]
      const formData = new FormData()
      formData.append('file', file)
      
      if (language) {
        formData.append('language', language)
      }
      
      if (translateTo) {
        formData.append('translate_to', translateTo)
      }

      const response = await axios.post('/api/v1/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data.task_id) {
        onTaskCreated(response.data.task_id)
        toast.success('File uploaded successfully!')
        setFiles([])
        setLanguage('')
        setTranslateTo('')
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.flac'],
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    maxSize: 100 * 1024 * 1024, // 100MB
  })

  return (
    <div className="space-y-4">
      {/* Drag and drop area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-400 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag & drop audio/video files here, or click to select files'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Supported: MP3, WAV, M4A, FLAC, MP4, AVI, MOV, MKV (max 100MB)
        </p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Selected Files:</h3>
          {files.map((file) => (
            <div key={file.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {file.preview && (
                  <img
                    src={file.preview}
                    alt={file.name}
                    className="h-10 w-10 object-cover rounded"
                  />
                )}
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeFile(file)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Language options */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Source Language (optional)
          </label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="input-field"
          >
            <option value="">Auto-detect</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
            <option value="pt">Portuguese</option>
            <option value="ru">Russian</option>
            <option value="ja">Japanese</option>
            <option value="ko">Korean</option>
            <option value="zh">Chinese</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Translate To (optional)
          </label>
          <select
            value={translateTo}
            onChange={(e) => setTranslateTo(e.target.value)}
            className="input-field"
          >
            <option value="">No translation</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
            <option value="pt">Portuguese</option>
            <option value="ru">Russian</option>
            <option value="ja">Japanese</option>
            <option value="ko">Korean</option>
            <option value="zh">Chinese</option>
          </select>
        </div>
      </div>

      {/* Upload button */}
      <button
        onClick={uploadFiles}
        disabled={files.length === 0 || isUploading}
        className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isUploading ? 'Uploading...' : 'Upload and Process'}
      </button>
    </div>
  )
}

export default FileUpload
