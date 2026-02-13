/**
 * API service for communicating with the backend server
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/server/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Log user activity
 */
export async function logActivity(type, userId, data) {
  try {
    const response = await api.post('/logs', {
      type,
      user_id: userId,
      ...data
    })
    return response.data
  } catch (error) {
    console.error('Failed to log activity:', error)
    return { success: false }
  }
}

/**
 * Start a new study session
 */
export async function startStudy(language, userId = null) {
  const response = await api.post('/study/start', {
    language,
    user_id: userId
  })
  return response.data
}

/**
 * Submit static context text
 */
export async function submitContext(userId, text) {
  const response = await api.post('/context/submit', {
    user_id: userId,
    text
  })
  return response.data
}

/**
 * Generate FCQ and JC questionnaires using LLM
 */
export async function generateQuestionnaires(userId, text) {
  const response = await api.post('/llm/generate-questionnaires', {
    user_id: userId,
    text
  })
  return response.data
}

/**
 * Submit questionnaire responses
 */
export async function submitQuestionnaire(userId, contextType, fcq, jc) {
  const response = await api.post('/questionnaire/submit', {
    user_id: userId,
    contextType,
    fcq,
    jc
  })
  return response.data
}

/**
 * Submit manual review of LLM-generated context
 */
export async function submitReview(userId, fcqReview, jcReview) {
  const response = await api.post('/review/submit', {
    user_id: userId,
    fcqReview,
    jcReview
  })
  return response.data
}

/**
 * Get recipes for rating
 */
export async function getRecipes(userId) {
  const response = await api.get('/recipes', {
    params: { user_id: userId }
  })
  return response.data
}

/**
 * Submit recipe ratings (static context)
 */
export async function submitStaticRatings(userId, ratings) {
  const response = await api.post('/ratings/static/submit', {
    user_id: userId,
    ratings
  })
  return response.data
}

/**
 * Get LLM ratings for recipes (static context)
 */
export async function getLLMStaticRatings(userId, recipes, context) {
  const response = await api.post('/llm/rate-recipes-static', {
    user_id: userId,
    recipes,
    context
  })
  return response.data
}

/**
 * Get dynamic contexts
 */
export async function getDynamicContexts(userId, language) {
  const response = await api.get('/dynamic-contexts', {
    params: { user_id: userId, language }
  })
  return response.data
}

/**
 * Submit recipe ratings (dynamic context)
 */
export async function submitDynamicRatings(userId, ratings) {
  const response = await api.post('/ratings/dynamic/submit', {
    user_id: userId,
    ratings
  })
  return response.data
}

/**
 * Get LLM ratings for recipes (dynamic context)
 */
export async function getLLMDynamicRatings(userId, ratings) {
  const response = await api.post('/llm/rate-recipes-dynamic', {
    user_id: userId,
    ratings
  })
  return response.data
}

/**
 * Submit comparison feedback
 */
export async function submitComparison(userId, phase, feedback) {
  const response = await api.post('/comparison/submit', {
    user_id: userId,
    phase,
    feedback
  })
  return response.data
}

/**
 * Complete the study
 */
export async function completeStudy(userId) {
  const response = await api.post('/study/complete', {
    user_id: userId
  })
  return response.data
}

export default api
