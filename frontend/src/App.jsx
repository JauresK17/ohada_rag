import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [reponse, setReponse] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)

  const poserQuestion = async () => {
    if (!question.trim()) return   // ne rien faire si le champ est vide
    setLoading(true)
    setReponse('')
    setSources([])

    try {
      const res = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      const data = await res.json()
      setReponse(data.reponse)
      setSources(data.sources)
    } catch (err) {
      setReponse('Erreur : impossible de contacter le serveur.')
    } finally {
      setLoading(false)
    }
  }

  // Permet d'envoyer avec Ctrl+Entrée
  const onKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) poserQuestion()
  }

  const exemples = [
    "Quel est le délai de préavis pour rompre un contrat d’agent commercial la deuxième année ?",
    "Deux époux peuvent-ils être associés dans la même société ?",
    "Qu’est-ce qui a changé entre 1997 et 2014 pour les apports en industrie ?",
    "Que se passe-t-il si un seul associé détient toutes les parts d'une société ?",
  ]

  return (
    <div className="app">
      <header className="header">
        <div className="logo">⚖️</div>
        <h1>Assistant juridique <span className="accent">OHADA</span></h1>
        <p className="subtitle">
          Droit commercial général &amp; sociétés commerciales · réponses sourcées
        </p>
      </header>

      <main className="main">
        <div className="card">
          <textarea
            className="input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Posez votre question juridique…"
            rows={3}
          />

          <div className="actions">
            <span className="hint">Ctrl + Entrée pour envoyer</span>
            <button className="btn" onClick={poserQuestion} disabled={loading}>
              {loading ? (
                <span className="spinner-wrap">
                  <span className="spinner"></span> Recherche…
                </span>
              ) : (
                'Poser la question'
              )}
            </button>
          </div>

          {/* Exemples cliquables, visibles quand il n'y a pas encore de réponse */}
          {!reponse && !loading && (
            <div className="exemples">
              {exemples.map((ex, i) => (
                <button key={i} className="chip" onClick={() => setQuestion(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* État de chargement */}
        {loading && (
          <div className="card loading-card">
            <div className="skeleton"></div>
            <div className="skeleton short"></div>
            <div className="skeleton"></div>
          </div>
        )}

        {/* La réponse */}
        {reponse && !loading && (
          <div className="card reponse-card">
            <h2 className="section-title">Réponse</h2>
            <p className="reponse-text">{reponse}</p>

            {sources.length > 0 && (
              <div className="sources">
                <h3 className="sources-title">Sources</h3>
                <div className="sources-list">
                  {sources.map((s, i) => (
                    <div key={i} className="source-chip">
                      <span className="source-article">Art. {s.article}</span>
                      <span className="source-meta">
                        {s.acte.replace(/_/g, ' ')} · {s.version}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        Projet RAG · textes OHADA · à titre informatif, ne constitue pas un conseil juridique
      </footer>
    </div>
  )
}

export default App