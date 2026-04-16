import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  createSession,
  generateQuestionsForSession,
  uploadResume,
} from '../api/client'

function Home() {
  const navigate = useNavigate()
  const [difficulty, setDifficulty] = useState('medium')
  const [resumeFile, setResumeFile] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')

    if (!resumeFile) {
      setErrorMessage('Please upload your resume file before submitting.')
      return
    }

    setIsSubmitting(true)
    try {
      const session = await createSession(difficulty)
      await uploadResume(session.id, resumeFile)
      await generateQuestionsForSession(session.id)
      navigate(`/interview/${session.id}`)
    } catch (error) {
      setErrorMessage(error.message || 'Failed to start interview session.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="card">
        <h1>Start Mock Interview</h1>
        <p className="page-description">
          Upload your resume, choose a difficulty level, and begin your mock
          interview.
        </p>

        <form className="stack-form" onSubmit={handleSubmit}>
        <label htmlFor="difficulty">Difficulty</label>
        <select
          id="difficulty"
          value={difficulty}
          onChange={(event) => setDifficulty(event.target.value)}
        >
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>

        <label htmlFor="resume">Upload Resume (PDF/DOCX)</label>
        <input
          id="resume"
          type="file"
          accept=".pdf,.docx"
          onChange={(event) => setResumeFile(event.target.files?.[0] || null)}
        />

          <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </button>
        </form>
        {errorMessage ? <p className="status-message error">{errorMessage}</p> : null}
      </section>
    </main>
  )
}

export default Home
