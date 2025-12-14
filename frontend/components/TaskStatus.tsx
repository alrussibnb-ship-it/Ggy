import { useState, useEffect } from 'react'
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline'
import axios from 'axios'

interface TaskStatusProps {
  taskId: string
}

interface TaskResult {
  status: string
  result?: any
  error?: string
}

const TaskStatus: React.FC<TaskStatusProps> = ({ taskId }) => {
  const [taskStatus, setTaskStatus] = useState<TaskResult | null>(null)
  const [isPolling, setIsPolling] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`/api/v1/tasks/status/${taskId}`)
        setTaskStatus(response.data)
        
        // Stop polling when task is completed
        if (response.data.status === 'SUCCESS' || response.data.status === 'FAILURE') {
          setIsPolling(false)
        }
      } catch (error) {
        console.error('Error fetching task status:', error)
        setIsPolling(false)
      }
    }

    // Initial fetch
    fetchStatus()

    // Set up polling
    const interval = setInterval(() => {
      if (isPolling) {
        fetchStatus()
      }
    }, 2000) // Poll every 2 seconds

    // Cleanup
    return () => {
      clearInterval(interval)
      setIsPolling(false)
    }
  }, [taskId, isPolling])

  if (!taskStatus) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading task status...</span>
      </div>
    )
  }

  const getStatusIcon = () => {
    switch (taskStatus.status) {
      case 'SUCCESS':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />
      case 'FAILURE':
        return <XCircleIcon className="h-6 w-6 text-red-500" />
      default:
        return <ClockIcon className="h-6 w-6 text-yellow-500 animate-pulse" />
    }
  }

  const getStatusText = () => {
    switch (taskStatus.status) {
      case 'PENDING':
        return 'Task is pending...'
      case 'STARTED':
        return 'Task is running...'
      case 'SUCCESS':
        return 'Task completed successfully!'
      case 'FAILURE':
        return 'Task failed'
      default:
        return 'Unknown status'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3">
        {getStatusIcon()}
        <span className="text-lg font-medium">{getStatusText()}</span>
      </div>
      
      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm text-gray-600">
          <strong>Task ID:</strong> {taskId}
        </p>
        <p className="text-sm text-gray-600">
          <strong>Status:</strong> {taskStatus.status}
        </p>
      </div>

      {taskStatus.status === 'SUCCESS' && taskStatus.result && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Results</h3>
          <div className="space-y-2 text-sm">
            <p><strong>Original Text:</strong> {taskStatus.result.text}</p>
            {taskStatus.result.language && (
              <p><strong>Detected Language:</strong> {taskStatus.result.language}</p>
            )}
            {taskStatus.result.segments && (
              <p><strong>Segments:</strong> {taskStatus.result.segments.length} segments processed</p>
            )}
          </div>
        </div>
      )}

      {taskStatus.status === 'FAILURE' && taskStatus.error && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-red-800 mb-2">Error Details</h3>
          <p className="text-sm text-red-700">{taskStatus.error}</p>
        </div>
      )}
    </div>
  )
}

export default TaskStatus
