import { useState } from "react";
import { Outlet, useLocation, Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Upload,
  FileText,
  Users,
  BarChart3,
  Settings,
  Menu,
  X,
  Bell,
  Search,
  ChevronDown,
  FileDown,
  LayoutTemplate,
  Zap,
  ClipboardList,
  Sparkles,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Įkelti darbą", href: "/ikelti", icon: Upload },
  { name: "Peržiūrėti", href: "/perziureti", icon: FileText },
  { name: "Greitas tikrinimas", href: "/greitas-tikrinimas", icon: Zap },
  { name: "Kontroliniai", href: "/kontroliniai", icon: ClipboardList },
  { name: "Generuoti su AI", href: "/kontroliniai/generuoti", icon: Sparkles },
  { name: "Mokiniai", href: "/mokiniai", icon: Users },
  { name: "Eksportai", href: "/eksportai", icon: FileDown },
  { name: "Šablonai", href: "/sablonai", icon: LayoutTemplate },
  { name: "Analitika", href: "/statistika", icon: BarChart3 },
];

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform bg-[#1a3a2f] transition-transform duration-200 ease-in-out lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex h-20 items-center gap-3 border-b border-emerald-800/50 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 text-white text-xl font-bold shadow-lg shadow-emerald-500/30">
            M
          </div>
          <span className="text-xl font-bold text-white">Matematika</span>
          <button
            className="ml-auto lg:hidden text-emerald-300 hover:text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2 px-3 py-6">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center gap-4 rounded-xl px-4 py-3 text-base font-medium transition-all duration-200",
                  isActive
                    ? "bg-gradient-to-r from-emerald-600 to-emerald-500 text-white shadow-lg shadow-emerald-500/25"
                    : "text-emerald-100/80 hover:bg-emerald-800/50 hover:text-white hover:translate-x-1"
                )}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon
                  className={cn("h-6 w-6", isActive && "drop-shadow-lg")}
                />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Bottom section */}
        <div className="border-t border-emerald-800/50 p-4">
          <Link
            to="/nustatymai"
            className="flex items-center gap-4 rounded-xl px-4 py-3 text-base font-medium text-emerald-100/80 hover:bg-emerald-800/50 hover:text-white transition-all duration-200 hover:translate-x-1"
          >
            <Settings className="h-6 w-6" />
            Nustatymai
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-4 sm:px-6">
          <button
            className="lg:hidden text-muted-foreground hover:text-foreground"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>

          {/* Search */}
          <div className="flex flex-1 items-center gap-2">
            <div className="relative w-full max-w-md">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Ieškoti..."
                className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-medium text-white">
                3
              </span>
            </Button>

            {/* User menu */}
            <button className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-muted transition-colors">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-white text-sm font-medium">
                MM
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-sm font-medium">Mokytoja</p>
                <p className="text-xs text-muted-foreground">Matematika</p>
              </div>
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
