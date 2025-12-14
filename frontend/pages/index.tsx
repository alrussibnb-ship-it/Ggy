import type { NextPage } from 'next'
import Head from 'next/head'
import FileUpload from '@/components/FileUpload'
import TaskStatus from '@/components/TaskStatus'
import { useState } from 'react'

const Home: NextPage = () => {
  const [taskId, setTaskId] = useState<string | null>(null)

  return (
    <>
      <Head>
        <title>Audio Processing API</title>
        <meta name="description" content="Upload and process audio/video files" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Audio Processing API
            </h1>
            <p className="text-xl text-gray-600">
              Upload audio or video files for transcription and translation
            </p>
          </div>

          <div className="max-w-2xl mx-auto space-y-8">
            <div className="card">
              <h2 className="text-2xl font-semibold mb-4">Upload File</h2>
              <FileUpload onTaskCreated={setTaskId} />
            </div>

            {taskId && (
              <div className="card">
                <h2 className="text-2xl font-semibold mb-4">Task Status</h2>
                <TaskStatus taskId={taskId} />
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

export default Home
