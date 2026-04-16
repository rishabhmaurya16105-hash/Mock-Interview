const API_BASE_URL = import.meta.env.VITE_API_URL || ''

export async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options)

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || `Request failed with status ${response.status}`)
  }

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }

  return response.text()
}

export function createSession(difficulty) {
  return apiFetch('/api/sessions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty }),
  })
}

export function uploadResume(sessionId, file) {
  const formData = new FormData()
  formData.append('file', file)

  return apiFetch(`/api/sessions/${sessionId}/resume/`, {
    method: 'POST',
    body: formData,
  })
}

export function generateQuestionsForSession(sessionId, numQuestions = 5) {
  return apiFetch(`/api/sessions/${sessionId}/questions/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ num_questions: numQuestions }),
  })
}

export function getSessionDetail(sessionId) {
  return apiFetch(`/api/sessions/${sessionId}/`, {
    method: 'GET',
  })
}

export function submitAnswer(sessionId, questionId, answer) {
  return apiFetch(`/api/sessions/${sessionId}/answers/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_id: questionId, answer }),
  })
}

export function completeSession(sessionId) {
  return apiFetch(`/api/sessions/${sessionId}/complete/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  })
}

export function getSessionResult(sessionId) {
  return apiFetch(`/api/sessions/${sessionId}/result/`, {
    method: 'GET',
  })
}
