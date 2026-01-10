import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  FileText,
  Upload,
  BarChart3,
  Settings,
  Calculator,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Pradžia' },
  { to: '/classes', icon: GraduationCap, label: 'Klasės' },
  { to: '/students', icon: Users, label: 'Mokiniai' },
  { to: '/tests', icon: FileText, label: 'Kontroliniai' },
  { to: '/submissions', icon: Upload, label: 'Pateikti darbai' },
  { to: '/statistics', icon: BarChart3, label: 'Statistika' },
  { to: '/settings', icon: Settings, label: 'Nustatymai' },
]

export function Sidebar() {
  return (
    <aside className="w-64 bg-slate-800 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
            <Calculator className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg">Matematika</h1>
            <p className="text-xs text-slate-400">Mokytojo asistentas</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700">
        <p className="text-xs text-slate-500 text-center">
          Versija 0.1.0
        </p>
      </div>
    </aside>
  )
}
