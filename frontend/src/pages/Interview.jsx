import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import {
  completeSession,
  getSessionDetail,
  submitAnswer,
} from '../api/client'

function Interview() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answerText, setAnswerText] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let isCancelled = false

    async function loadQuestions() {
      setIsLoading(true)
      setErrorMessage('')
      try {
        const response = await getSessionDetail(sessionId)
        const sessionQuestions = response.questions || []
        if (!isCancelled) {
          setQuestions(sessionQuestions)
          setCurrentQuestionIndex(0)
          if (!sessionQuestions.length) {
            setErrorMessage('Questions are not available for this interview session.')
          }
        }
      } catch (error) {
        if (!isCancelled) {
          setErrorMessage(error.message || 'Failed to load interview questions.')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadQuestions()
    return () => {
      isCancelled = true
    }
  }, [sessionId])

  const currentQuestion = questions[currentQuestionIndex]

  async function handleNext() {
    if (!currentQuestion) {
      return
    }

    const trimmedAnswer = answerText.trim()
    if (!trimmedAnswer) {
      setErrorMessage('Please type your answer before continuing.')
      return
    }

    setIsSubmitting(true)
    setErrorMessage('')
    try {
      await submitAnswer(sessionId, currentQuestion.id, trimmedAnswer)

      const isLastQuestion = currentQuestionIndex >= questions.length - 1
      if (isLastQuestion) {
        await completeSession(sessionId)
        navigate(`/results/${sessionId}`)
        return
      }

      setCurrentQuestionIndex((prevIndex) => prevIndex + 1)
      setAnswerText('')
    } catch (error) {
      setErrorMessage(error.message || 'Failed to submit answer.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="card">
        <h1>Interview Page</h1>
        {isLoading ? <p className="status-message">Loading questions...</p> : null}
      {!isLoading && currentQuestion ? (
        <section className="stack-section">
          <p className="eyebrow">
            Question {currentQuestionIndex + 1} of {questions.length}
          </p>
          <h2 className="question-title">{currentQuestion.text}</h2>

          <label htmlFor="answer">Your answer</label>
          <textarea
            className="text-area"
            id="answer"
            rows={6}
            value={answerText}
            onChange={(event) => setAnswerText(event.target.value)}
            placeholder="Type your answer here..."
          />

          <button className="primary-button" type="button" onClick={handleNext} disabled={isSubmitting}>
            {isSubmitting
              ? 'Saving...'
              : currentQuestionIndex >= questions.length - 1
                ? 'Finish Interview'
                : 'Next Question'}
          </button>
        </section>
      ) : null}
      {!isLoading && !currentQuestion && !errorMessage ? (
        <p className="status-message">No questions found for this interview session.</p>
      ) : null}
        {errorMessage ? <p className="status-message error">{errorMessage}</p> : null}
      </section>
    </main>
  )
}

export default Interview
