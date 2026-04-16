import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Interview from './pages/Interview'
import Results from './pages/Results'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Layout>
              <Home />
            </Layout>
          }
        />
        <Route
          path="/interview/:sessionId"
          element={
            <Layout>
              <Interview />
            </Layout>
          }
        />
        <Route
          path="/results/:sessionId"
          element={
            <Layout>
              <Results />
            </Layout>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
