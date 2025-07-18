import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8001/v1'

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: Message[]
}

export interface ChatResponse {
  choices: {
    message: Message
  }[]
}

export interface ScreenshotRequest {
  store_in_memory?: boolean
  analyze?: boolean
  ocr?: boolean
}

export interface ScreenshotResponse {
  id: string
  timestamp: string
  preview: string
  analysis?: string
  ocr_text?: string
}

export class LocalAPIClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  async chatCompletion(messages: Message[]): Promise<ChatResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/chat/completions`, {
        messages
      })
      return response.data
    } catch (error) {
      console.error('Chat completion error:', error)
      throw error
    }
  }

  async getModels() {
    try {
      const response = await axios.get(`${this.baseURL}/models`)
      return response.data
    } catch (error) {
      console.error('Get models error:', error)
      throw error
    }
  }

  async takeScreenshot(options: ScreenshotRequest = {}): Promise<ScreenshotResponse> {
    try {
      const response = await axios.post(`${this.baseURL.replace('/v1', '')}/api/screenshot/screenshot`, options)
      return response.data
    } catch (error) {
      console.error('Screenshot error:', error)
      throw error
    }
  }

  async getScreenshotQueue() {
    try {
      const response = await axios.get(`${this.baseURL.replace('/v1', '')}/api/screenshot/queue`)
      return response.data
    } catch (error) {
      console.error('Get screenshot queue error:', error)
      throw error
    }
  }

  async deleteScreenshot(screenshotId: string) {
    try {
      const response = await axios.delete(`${this.baseURL.replace('/v1', '')}/api/screenshot/queue/${screenshotId}`)
      return response.data
    } catch (error) {
      console.error('Delete screenshot error:', error)
      throw error
    }
  }

  async clearQueue() {
    try {
      const response = await axios.post(`${this.baseURL.replace('/v1', '')}/api/screenshot/queue/clear`)
      return response.data
    } catch (error) {
      console.error('Clear queue error:', error)
      throw error
    }
  }

  async analyzeScreenshot(screenshotId: string) {
    try {
      const response = await axios.get(`${this.baseURL.replace('/v1', '')}/api/screenshot/queue/${screenshotId}/analyze`)
      return response.data
    } catch (error) {
      console.error('Analyze screenshot error:', error)
      throw error
    }
  }

  // Tool functions
  async clickAt(x: number, y: number) {
    try {
      const response = await axios.post(`${this.baseURL.replace('/v1', '')}/api/tools/click`, { x, y })
      return response.data
    } catch (error) {
      console.error('Click tool error:', error)
      throw error
    }
  }

  async typeText(text: string) {
    try {
      const response = await axios.post(`${this.baseURL.replace('/v1', '')}/api/tools/type`, { text })
      return response.data
    } catch (error) {
      console.error('Type tool error:', error)
      throw error
    }
  }

  async readClipboard() {
    try {
      const response = await axios.get(`${this.baseURL.replace('/v1', '')}/api/tools/clipboard`)
      return response.data
    } catch (error) {
      console.error('Read clipboard error:', error)
      throw error
    }
  }

  async writeClipboard(text: string) {
    try {
      const response = await axios.post(`${this.baseURL.replace('/v1', '')}/api/tools/clipboard`, { text })
      return response.data
    } catch (error) {
      console.error('Write clipboard error:', error)
      throw error
    }
  }

  async getScreenSize() {
    try {
      const response = await axios.get(`${this.baseURL.replace('/v1', '')}/api/tools/screen-size`)
      return response.data
    } catch (error) {
      console.error('Get screen size error:', error)
      throw error
    }
  }

  async getMousePosition() {
    try {
      const response = await axios.get(`${this.baseURL.replace('/v1', '')}/api/tools/mouse-position`)
      return response.data
    } catch (error) {
      console.error('Get mouse position error:', error)
      throw error
    }
  }

  async healthCheck() {
    try {
      const response = await axios.get(`${this.baseURL.replace('/v1', '')}/health`)
      return response.data
    } catch (error) {
      console.error('Health check error:', error)
      throw error
    }
  }
}

export const apiClient = new LocalAPIClient()