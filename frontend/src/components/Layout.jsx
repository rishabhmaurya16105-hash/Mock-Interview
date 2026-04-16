function Layout({ children }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h2 className="app-title">Mock Interview</h2>
      </header>
      {children}
    </div>
  )
}

export default Layout
