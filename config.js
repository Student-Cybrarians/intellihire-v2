// IntelliHire v2 - AI Configuration
// Using OpenAI GPT-4o API
const OPENAI_API_KEY = 'PLACEHOLDER_OPENAI_KEY';

// API Configuration
const API_CONFIG = {
  baseURL: 'https://api.openai.com/v1/chat/completions',
  model: 'gpt-4o',
  maxTokens: 4096
};

// Helper function for API calls (compatible with both Claude and OpenAI)
async function callClaude(messages, systemPrompt = '') {
  // Convert messages format for OpenAI
  const openaiMessages = systemPrompt 
    ? [{ role: 'system', content: systemPrompt }, ...messages]
    : messages;
  
  const response = await fetch(API_CONFIG.baseURL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: API_CONFIG.model,
      max_tokens: API_CONFIG.maxTokens,
      messages: openaiMessages,
      temperature: 0.7
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${response.status} - ${error.error?.message || 'Unknown error'}`);
  }
  
  const data = await response.json();
  
  // Convert OpenAI response format to Claude-compatible format
  return {
    content: [{
      type: 'text',
      text: data.choices[0].message.content
    }]
  };
}
