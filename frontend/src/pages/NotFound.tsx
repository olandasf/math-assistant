import { Home } from 'lucide-react'
import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-6xl font-bold text-slate-300 mb-4">404</h1>
      <h2 className="text-2xl font-semibold text-slate-700 mb-2">
        Puslapis nerastas
      </h2>
      <p className="text-slate-500 mb-8">
        Atsiprašome, bet puslapis, kurio ieškote, neegzistuoja.
      </p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Home className="w-5 h-5" />
        Grįžti į pradžią
      </Link>
    </div>
  )
}
