import axios from "axios"

export class LocalAPIHelper {
  private baseURL: string
  private readonly systemPrompt = `You are an OS-level automation assistant. Always think step-by-step. Use screenshot(), ocr(), click(x,y), type(text), read_clipboard(), write_clipboard() and retrieve_context() as needed. For coding tasks, prefer deepseek-coder. Ask clarifying questions if uncertain.`

  constructor(baseURL: string = "http://127.0.0.1:8001/v1") {
    this.baseURL = baseURL
  }

  private async makeRequest(url: string, data: any, timeout: number = 60000) {
    try {
      const response = await axios.post(url, data, { timeout })
      return response.data
    } catch (error) {
      console.error("API request failed:", error)
      throw error
    }
  }

  public async extractProblemFromImages(imagePaths: string[]) {
    try {
      // For now, we'll use a simple approach - take the first image and analyze it
      const firstImage = imagePaths[0]
      if (!firstImage) {
        throw new Error("No image provided")
      }

      // Use the screenshot analysis endpoint
      const messages = [
        {
          role: "user",
          content: `Analyze this screenshot and extract the following information in JSON format:
{
  "problem_statement": "A clear statement of the problem or situation depicted in the image.",
  "context": "Relevant background or context from the image.",
  "suggested_responses": ["First possible answer or action", "Second possible answer or action", "..."],
  "reasoning": "Explanation of why these suggestions are appropriate."
}
Please return ONLY the JSON object.`
        }
      ]

      const response = await this.makeRequest(`${this.baseURL}/chat/completions`, {
        messages
      })

      const responseText = response.choices[0]?.message?.content || ""
      
      // Try to parse as JSON
      try {
        return JSON.parse(responseText)
      } catch (e) {
        // If parsing fails, return a structured response
        return {
          problem_statement: responseText,
          context: "Generated from screenshot analysis",
          suggested_responses: ["Analyze the situation", "Take appropriate action"],
          reasoning: "Based on AI analysis of the screenshot"
        }
      }
    } catch (error) {
      console.error("Error extracting problem from images:", error)
      throw error
    }
  }

  public async generateSolution(problemInfo: any) {
    try {
      const messages = [
        {
          role: "user",
          content: `Given this problem or situation: ${JSON.stringify(problemInfo, null, 2)}

Please provide your response in the following JSON format:
{
  "solution": {
    "code": "The code or main answer here.",
    "problem_statement": "Restate the problem or situation.",
    "context": "Relevant background/context.",
    "suggested_responses": ["First possible answer or action", "Second possible answer or action", "..."],
    "reasoning": "Explanation of why these suggestions are appropriate."
  }
}
Return ONLY the JSON object.`
        }
      ]

      console.log("[LocalAPIHelper] Calling local API for solution...")
      const response = await this.makeRequest(`${this.baseURL}/chat/completions`, {
        messages
      })

      const responseText = response.choices[0]?.message?.content || ""
      
      try {
        const parsed = JSON.parse(responseText)
        console.log("[LocalAPIHelper] Parsed API response:", parsed)
        return parsed
      } catch (e) {
        // If parsing fails, return a structured response
        return {
          solution: {
            code: responseText,
            problem_statement: problemInfo.problem_statement,
            context: problemInfo.context,
            suggested_responses: ["Implement the solution", "Test the approach"],
            reasoning: "Based on AI analysis"
          }
        }
      }
    } catch (error) {
      console.error("[LocalAPIHelper] Error in generateSolution:", error)
      throw error
    }
  }

  public async debugSolutionWithImages(problemInfo: any, currentCode: string, debugImagePaths: string[]) {
    try {
      const messages = [
        {
          role: "user",
          content: `Given:
1. The original problem or situation: ${JSON.stringify(problemInfo, null, 2)}
2. The current response or approach: ${currentCode}
3. Debug information from the provided images

Please analyze the debug information and provide feedback in this JSON format:
{
  "solution": {
    "code": "The updated code or main answer here.",
    "problem_statement": "Restate the problem or situation.",
    "context": "Relevant background/context.",
    "suggested_responses": ["First possible answer or action", "Second possible answer or action", "..."],
    "reasoning": "Explanation of why these suggestions are appropriate."
  }
}
Return ONLY the JSON object.`
        }
      ]

      const response = await this.makeRequest(`${this.baseURL}/chat/completions`, {
        messages
      })

      const responseText = response.choices[0]?.message?.content || ""
      
      try {
        const parsed = JSON.parse(responseText)
        console.log("[LocalAPIHelper] Parsed debug response:", parsed)
        return parsed
      } catch (e) {
        // If parsing fails, return a structured response
        return {
          solution: {
            code: responseText,
            problem_statement: problemInfo.problem_statement,
            context: problemInfo.context,
            suggested_responses: ["Review the debug information", "Implement the fix"],
            reasoning: "Based on debug analysis"
          }
        }
      }
    } catch (error) {
      console.error("Error debugging solution with images:", error)
      throw error
    }
  }

  public async analyzeAudioFile(audioPath: string) {
    try {
      const messages = [
        {
          role: "user",
          content: `Describe this audio clip in a short, concise answer. In addition to your main answer, suggest several possible actions or responses the user could take next based on the audio. Do not return a structured JSON object, just answer naturally as you would to a user.`
        }
      ]

      const response = await this.makeRequest(`${this.baseURL}/chat/completions`, {
        messages
      })

      const text = response.choices[0]?.message?.content || ""
      return { text, timestamp: Date.now() }
    } catch (error) {
      console.error("Error analyzing audio file:", error)
      throw error
    }
  }

  public async analyzeAudioFromBase64(data: string, mimeType: string) {
    try {
      const messages = [
        {
          role: "user",
          content: `Describe this audio clip in a short, concise answer. In addition to your main answer, suggest several possible actions or responses the user could take next based on the audio. Do not return a structured JSON object, just answer naturally as you would to a user and be concise.`
        }
      ]

      const response = await this.makeRequest(`${this.baseURL}/chat/completions`, {
        messages
      })

      const text = response.choices[0]?.message?.content || ""
      return { text, timestamp: Date.now() }
    } catch (error) {
      console.error("Error analyzing audio from base64:", error)
      throw error
    }
  }

  public async analyzeImageFile(imagePath: string) {
    try {
      const messages = [
        {
          role: "user",
          content: `Describe the content of this image in a short, concise answer. In addition to your main answer, suggest several possible actions or responses the user could take next based on the image. Do not return a structured JSON object, just answer naturally as you would to a user. Be concise and brief.`
        }
      ]

      const response = await this.makeRequest(`${this.baseURL}/chat/completions`, {
        messages
      })

      const text = response.choices[0]?.message?.content || ""
      return { text, timestamp: Date.now() }
    } catch (error) {
      console.error("Error analyzing image file:", error)
      throw error
    }
  }

  public async testConnection(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseURL.replace('/v1', '')}/health`, { timeout: 5000 })
      return response.status === 200
    } catch (error) {
      console.error("Connection test failed:", error)
      return false
    }
  }
}