import React, { useState } from 'react'
import LocalAIChat from './components/LocalAIChat'
import TaskDashboard from './components/TaskDashboard'
import { MessageSquare, Activity } from 'lucide-react'

const App: React.FC = () => {
  const [activeView, setActiveView] = useState<'chat' | 'dashboard'>('dashboard')

  return (
    <div className="h-screen flex flex-col">
      {/* Navigation */}
      <div className="bg-white shadow-sm border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-800">Autonomous AI Agent System</h1>
          
          <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveView('dashboard')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeView === 'dashboard'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Task Dashboard</span>
            </button>
            
            <button
              onClick={() => setActiveView('chat')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeView === 'chat'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>AI Chat</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {activeView === 'dashboard' ? <TaskDashboard /> : <LocalAIChat />}
      </div>
    </div>
  )
}

export default App
