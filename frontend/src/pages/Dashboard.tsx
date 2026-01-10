import { 
  FileText, 
  Users, 
  CheckCircle2, 
  Clock,
  TrendingUp,
  AlertCircle
} from 'lucide-react'

export function Dashboard() {
  // TODO: Pakeisti į realius duomenis iš API
  const stats = {
    totalTests: 0,
    totalStudents: 0,
    pendingSubmissions: 0,
    completedToday: 0,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Pradžia</h1>
        <p className="text-slate-500">Sveiki! Čia jūsų matematikos tikrinimo asistentas.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Kontroliniai"
          value={stats.totalTests}
          icon={FileText}
          color="blue"
        />
        <StatCard
          title="Mokiniai"
          value={stats.totalStudents}
          icon={Users}
          color="green"
        />
        <StatCard
          title="Laukia tikrinimo"
          value={stats.pendingSubmissions}
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="Patikrinta šiandien"
          value={stats.completedToday}
          icon={CheckCircle2}
          color="emerald"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Greiti veiksmai</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickAction
            title="Sukurti kontrolinį"
            description="Pridėti naują kontrolinį darbą"
            icon={FileText}
            href="/tests/new"
          />
          <QuickAction
            title="Įkelti darbus"
            description="Įkelti mokinių skanuotus darbus"
            icon={TrendingUp}
            href="/submissions/upload"
          />
          <QuickAction
            title="Peržiūrėti statistiką"
            description="Analizuoti rezultatus ir tendencijas"
            icon={AlertCircle}
            href="/statistics"
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Paskutinė veikla</h2>
        <div className="text-slate-500 text-center py-8">
          <Clock className="w-12 h-12 mx-auto mb-2 opacity-30" />
          <p>Kol kas nėra jokios veiklos.</p>
          <p className="text-sm">Pradėkite nuo kontrolinio sukūrimo!</p>
        </div>
      </div>
    </div>
  )
}

// === Pagalbiniai komponentai ===

interface StatCardProps {
  title: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color: 'blue' | 'green' | 'amber' | 'emerald'
}

function StatCard({ title, value, icon: Icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    amber: 'bg-amber-50 text-amber-600',
    emerald: 'bg-emerald-50 text-emerald-600',
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-3xl font-bold text-slate-800">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

interface QuickActionProps {
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  href: string
}

function QuickAction({ title, description, icon: Icon, href }: QuickActionProps) {
  return (
    <a
      href={href}
      className="flex items-start gap-4 p-4 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
    >
      <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <h3 className="font-medium text-slate-800">{title}</h3>
        <p className="text-sm text-slate-500">{description}</p>
      </div>
    </a>
  )
}
