import axios from 'axios'

// Configure API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface UploadFileResponse {
  message: string
  file_id: string
  filename: string
  size: number
  url: string
  task_id: string
  status: string
}

export interface TaskStatusResponse {
  task_id: string
  status: string
  result?: any
  traceback?: string
}

export interface HealthCheckResponse {
  status: string
  timestamp: string
  version: string
  app_name: string
  checks?: Record<string, any>
}

export const fileApi = {
  // Upload file
  uploadFile: async (file: File, language?: string, translateTo?: string): Promise<UploadFileResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    
    if (language) {
      formData.append('language', language)
    }
    
    if (translateTo) {
      formData.append('translate_to', translateTo)
    }

    const response = await api.post('/api/v1/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },

  // List files
  listFiles: async () => {
    const response = await api.get('/api/v1/files/list')
    return response.data
  },

  // Delete file
  deleteFile: async (fileId: string) => {
    const response = await api.delete(`/api/v1/files/${fileId}`)
    return response.data
  },

  // Download file
  downloadFile: async (fileId: string) => {
    const response = await api.get(`/api/v1/files/download/${fileId}`)
    return response.data
  },
}

export const taskApi = {
  // Get task status
  getStatus: async (taskId: string): Promise<TaskStatusResponse> => {
    const response = await api.get(`/api/v1/tasks/status/${taskId}`)
    return response.data
  },

  // Cancel task
  cancelTask: async (taskId: string) => {
    const response = await api.post(`/api/v1/tasks/cancel/${taskId}`)
    return response.data
  },

  // Get active tasks
  getActiveTasks: async () => {
    const response = await api.get('/api/v1/tasks/active')
    return response.data
  },

  // Get worker status
  getWorkerStatus: async () => {
    const response = await api.get('/api/v1/tasks/worker-status')
    return response.data
  },
}

export const healthApi = {
  // Basic health check
  check: async (): Promise<HealthCheckResponse> => {
    const response = await api.get('/api/v1/health/')
    return response.data
  },

  // Detailed health check
  detailedCheck: async (): Promise<HealthCheckResponse> => {
    const response = await api.get('/api/v1/health/detailed')
    return response.data
  },

  // Readiness check
  readinessCheck: async () => {
    const response = await api.get('/api/v1/health/ready')
    return response.data
  },

  // Liveness check
  livenessCheck: async () => {
    const response = await api.get('/api/v1/health/live')
    return response.data
  },
}

export default api
