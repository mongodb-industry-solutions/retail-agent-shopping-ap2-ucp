'use client'
import React, { useState } from 'react'

const TestPage = () => {
  const [responses, setResponses] = useState({})
  const [loading, setLoading] = useState({})

  // Form states for each API
  const [chatForm, setChatForm] = useState({
    message: 'I want a coffee maker',
    user_id: '123',
    session_id: 'test-session'
  })

  const [sessionForm, setSessionForm] = useState({
    user_id: '123'
  })

  const [getSessionForm, setGetSessionForm] = useState({
    session_id: 'test-session',
    user_id: '123'
  })

  const callAPI = async (apiName, url, method = 'GET', body = null) => {
    setLoading(prev => ({ ...prev, [apiName]: true }))
    
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
        }
      }
      
      if (body) {
        options.body = JSON.stringify(body)
      }

      const response = await fetch(url, options)
      const data = await response.json()
      
      setResponses(prev => ({
        ...prev,
        [apiName]: {
          status: response.status,
          data: data,
          timestamp: new Date().toLocaleTimeString()
        }
      }))
    } catch (error) {
      setResponses(prev => ({
        ...prev,
        [apiName]: {
          status: 'Error',
          data: { error: error.message },
          timestamp: new Date().toLocaleTimeString()
        }
      }))
    } finally {
      setLoading(prev => ({ ...prev, [apiName]: false }))
    }
  }

  const handleChatSubmit = () => {
    callAPI(
      'chat', 
      '/api/shopping-chat', 
      'POST',
      {
        message: chatForm.message,
        user_id: chatForm.user_id,
        session_id: chatForm.session_id
      }
    )
  }

  const handleStartSessionSubmit = () => {
    const url = `/api/shopping-start-session?user_id=${encodeURIComponent(sessionForm.user_id)}`
    callAPI('start-session', url, 'POST')
  }

  const handleGetSessionSubmit = () => {
    const url = `/api/shopping-session?session_id=${encodeURIComponent(getSessionForm.session_id)}&user_id=${encodeURIComponent(getSessionForm.user_id)}`
    callAPI('get-session', url, 'GET')
  }

  const ResponseDisplay = ({ response, apiName }) => {
    if (!response) return null
    
    return (
      <div className="mt-4 p-4 border rounded-lg bg-gray-50">
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium">Response ({apiName})</h4>
          <span className="text-sm text-gray-500">{response.timestamp}</span>
        </div>
        <div className="flex items-center gap-2 mb-2">
          <span className={`px-2 py-1 rounded text-sm font-medium ${
            response.status === 200 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            Status: {response.status}
          </span>
        </div>
        <pre className="bg-white p-3 rounded border overflow-auto text-sm">
          {JSON.stringify(response.data, null, 2)}
        </pre>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <div className=" mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">Shopping API Test Interface</h1>
        
        <div className="space-y-6">
          
          {/* Chat API */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-blue-600">Chat API</h2>
            <p className="text-sm text-gray-600 mb-4">POST /api/v1/shopping/chat</p>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                <textarea
                  value={chatForm.message}
                  onChange={(e) => setChatForm(prev => ({ ...prev, message: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  placeholder="Enter your message..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">User ID</label>
                <input
                  type="text"
                  value={chatForm.user_id}
                  onChange={(e) => setChatForm(prev => ({ ...prev, user_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="User ID"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Session ID</label>
                <input
                  type="text"
                  value={chatForm.session_id}
                  onChange={(e) => setChatForm(prev => ({ ...prev, session_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Session ID"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={handleChatSubmit}
                  disabled={loading.chat}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading.chat ? 'Sending...' : 'Send'}
                </button>
              </div>
            </div>
            
            <ResponseDisplay response={responses.chat} apiName="Chat" />
          </div>

          {/* Start Session API */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-green-600">Start Session API</h2>
            <p className="text-sm text-gray-600 mb-4">POST /api/v1/shopping/start-session</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">User ID</label>
                <input
                  type="text"
                  value={sessionForm.user_id}
                  onChange={(e) => setSessionForm(prev => ({ ...prev, user_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="User ID"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={handleStartSessionSubmit}
                  disabled={loading['start-session']}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading['start-session'] ? 'Starting...' : 'Send'}
                </button>
              </div>
            </div>
            
            <ResponseDisplay response={responses['start-session']} apiName="Start Session" />
          </div>

          {/* Get Session API */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-purple-600">Get Session API</h2>
            <p className="text-sm text-gray-600 mb-4">GET /api/v1/shopping/session/{'{session_id}'}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Session ID</label>
                <input
                  type="text"
                  value={getSessionForm.session_id}
                  onChange={(e) => setGetSessionForm(prev => ({ ...prev, session_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Session ID"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">User ID</label>
                <input
                  type="text"
                  value={getSessionForm.user_id}
                  onChange={(e) => setGetSessionForm(prev => ({ ...prev, user_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="User ID"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={handleGetSessionSubmit}
                  disabled={loading['get-session']}
                  className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading['get-session'] ? 'Getting...' : 'Send'}
                </button>
              </div>
            </div>
            
            <ResponseDisplay response={responses['get-session']} apiName="Get Session" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default TestPage