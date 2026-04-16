import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { getSessionResult } from '../api/client'

function Results() {
  const { sessionId } = useParams()
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let isCancelled = false

    async function loadResult() {
      setIsLoading(true)
      setErrorMessage('')
      try {
        const response = await getSessionResult(sessionId)
        if (!isCancelled) {
          setResult(response)
        }
      } catch (error) {
        if (!isCancelled) {
          setErrorMessage(error.message || 'Failed to load interview result.')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadResult()
    return () => {
      isCancelled = true
    }
  }, [sessionId])

  const feedback = result?.feedback
  const perQuestionFeedback = Array.isArray(feedback?.per_question)
    ? feedback.per_question
    : []

  return (
    <main className="page-shell">
      <section className="card">
        <h1>Results Page</h1>
        {isLoading ? <p className="status-message">Loading results...</p> : null}
        {errorMessage ? <p className="status-message error">{errorMessage}</p> : null}

      {!isLoading && result ? (
        <section className="stack-section">
          <div className="result-summary">
            <p className="score-label">Total Score</p>
            <p className="score-value">{result.total_score}</p>
            <p className="status-message">Status: {result.status}</p>
          </div>
          <p>{feedback?.overall_feedback || 'No overall feedback available.'}</p>

          {perQuestionFeedback.length > 0 ? (
            <div className="stack-section">
              <h2>Per-question Feedback</h2>
              {perQuestionFeedback.map((item) => (
                <article className="feedback-card" key={item.question_index}>
                  <h3>
                    Question {item.question_index}: {item.score}/100
                  </h3>
                  <p>{item.feedback}</p>
                </article>
              ))}
            </div>
          ) : null}
        </section>
      ) : null}
      </section>
    </main>
  )
}

export default Results
