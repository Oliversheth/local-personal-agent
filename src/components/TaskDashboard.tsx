import React, { useState, useEffect } from 'react'
import { 
  Play, Pause, CheckCircle, XCircle, Clock, Activity,
  Code, Database, Server, TrendingUp, Settings, Eye
} from 'lucide-react'

interface Task {
  id: string
  description: string
  agent: string
  status: string
  progress: number
  updated_at: string
}

interface Session {
  session_id: string
  objective: string
  status: string
  progress: number
  current_task: string | null
  tasks: Task[]
}

const TaskDashboard: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeSession, setActiveSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [newObjective, setNewObjective] = useState('')
  const [systemStats, setSystemStats] = useState({
    active_sessions: 0,
    total_sessions: 0,
    agents_available: [],
    tools_available: []
  })

  useEffect(() => {
    fetchSessions()
    fetchSystemStats()
    
    // Poll for updates every 2 seconds
    const interval = setInterval(() => {
      fetchSessions()
      if (activeSession) {
        fetchSessionStatus(activeSession.session_id)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [activeSession])

  const fetchSessions = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL?.replace('/v1', '') || 'http://127.0.0.1:8001'}/v1/tasks`)
      const data = await response.json()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
    }
  }

  const fetchSessionStatus = async (sessionId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL?.replace('/v1', '') || 'http://127.0.0.1:8001'}/v1/tasks/${sessionId}/status`)
      const data = await response.json()
      setActiveSession(data)
    } catch (error) {
      console.error('Failed to fetch session status:', error)
    }
  }

  const fetchSystemStats = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL?.replace('/v1', '') || 'http://127.0.0.1:8001'}/health`)
      const data = await response.json()
      setSystemStats({
        active_sessions: data.active_sessions || 0,
        total_sessions: sessions.length,
        agents_available: data.agents_available || [],
        tools_available: data.tools_available || []
      })
    } catch (error) {
      console.error('Failed to fetch system stats:', error)
    }
  }

  const submitTask = async () => {
    if (!newObjective.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL?.replace('/v1', '') || 'http://127.0.0.1:8001'}/v1/tasks/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          objective: newObjective,
          priority: 'normal'
        })
      })

      const data = await response.json()
      if (response.ok) {
        setNewObjective('')
        fetchSessions()
        // Auto-select the new session
        setTimeout(() => fetchSessionStatus(data.session_id), 1000)
      }
    } catch (error) {
      console.error('Failed to submit task:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed': return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing': 
      case 'in_progress': return <Activity className="w-5 h-5 text-blue-500 animate-spin" />
      default: return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }

  const getAgentIcon = (agent: string) => {
    switch (agent.toLowerCase()) {
      case 'coder': return <Code className="w-4 h-4" />
      case 'designer': return <Eye className="w-4 h-4" />
      case 'planner': return <Settings className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Autonomous AI Agent Dashboard</h1>
        <p className="text-gray-600">Monitor and manage complex task execution across multiple AI agents</p>
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Activity className="w-8 h-8 text-blue-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{systemStats.active_sessions}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Server className="w-8 h-8 text-green-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Total Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{systemStats.total_sessions}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Code className="w-8 h-8 text-purple-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Agents</p>
              <p className="text-2xl font-bold text-gray-900">{systemStats.agents_available.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Database className="w-8 h-8 text-orange-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Tools</p>
              <p className="text-2xl font-bold text-gray-900">{systemStats.tools_available.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Task Submission */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Submit New Task</h2>
        <div className="flex gap-4">
          <input
            type="text"
            value={newObjective}
            onChange={(e) => setNewObjective(e.target.value)}
            placeholder="Describe your objective (e.g., 'Build a trading bot with Bollinger Bands strategy')"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={submitTask}
            disabled={isLoading || !newObjective.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {isLoading ? 'Submitting...' : 'Execute'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sessions List */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Sessions</h2>
          </div>
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                onClick={() => fetchSessionStatus(session.session_id)}
                className={`p-4 cursor-pointer hover:bg-gray-50 ${
                  activeSession?.session_id === session.session_id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(session.status)}
                    <span className="font-medium text-gray-900">{session.session_id}</span>
                  </div>
                  <span className="text-sm text-gray-500">{session.progress.toFixed(1)}%</span>
                </div>
                <p className="text-sm text-gray-600 truncate">{session.objective}</p>
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${session.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Session Details */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              {activeSession ? 'Session Details' : 'Select a Session'}
            </h2>
          </div>
          
          {activeSession ? (
            <div className="p-6">
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                  {getStatusIcon(activeSession.status)}
                  <span className="font-medium text-gray-900">{activeSession.session_id}</span>
                </div>
                <p className="text-gray-600 mb-4">{activeSession.objective}</p>
                
                {activeSession.current_task && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                    <p className="text-sm font-medium text-blue-900">Current Task:</p>
                    <p className="text-blue-800">{activeSession.current_task}</p>
                  </div>
                )}

                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Overall Progress</span>
                    <span>{activeSession.progress.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${activeSession.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Task Details */}
              <div>
                <h3 className="font-medium text-gray-900 mb-3">Task Breakdown</h3>
                <div className="space-y-3">
                  {activeSession.tasks.map((task) => (
                    <div
                      key={task.id}
                      className="border border-gray-200 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getAgentIcon(task.agent)}
                          <span className="font-medium text-sm text-gray-900">{task.agent}</span>
                          {getStatusIcon(task.status)}
                        </div>
                        <span className="text-xs text-gray-500">{task.progress}%</span>
                      </div>
                      <p className="text-sm text-gray-600">{task.description}</p>
                      <div className="mt-2">
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-green-600 h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${task.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Select a session to view detailed progress</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TaskDashboard