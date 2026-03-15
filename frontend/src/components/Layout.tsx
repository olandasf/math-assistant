import { useState } from "react";
import { Outlet, useLocation, Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Upload,
  FileCheck,
  Users,
  LineChart,
  Settings,
  Menu,
  X,
  Bell,
  Search,
  ChevronDown,
  Download,
  FileText,
  ListChecks,
  ClipboardList,
  Brain,
  BookOpenCheck
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Įkelti darbą", href: "/ikelti", icon: Upload },
  { name: "Peržiūrėti", href: "/perziureti", icon: FileCheck },
  { name: "Greitas tikrinimas", href: "/greitas-tikrinimas", icon: ListChecks },
  { name: "Kontroliniai", href: "/kontroliniai", icon: ClipboardList },
  { name: "Generuoti su AI", href: "/kontroliniai/generuoti", icon: Brain },
  { name: "Mokiniai", href: "/mokiniai", icon: Users },
  { name: "Eksportai", href: "/eksportai", icon: Download },
  { name: "Šablonai", href: "/sablonai", icon: FileText },
  { name: "Analitika", href: "/statistika", icon: LineChart },
];

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - The Academic Architect Primary */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 transform bg-primary transition-transform duration-200 ease-in-out lg:translate-x-0 shadow-2xl",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex h-20 items-center justify-between px-6">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-tertiary to-tertiary-container text-white shadow-lg group-hover:shadow-tertiary/50 transition-all">
              <BookOpenCheck className="h-6 w-6" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">MathTeacher <span className="text-tertiary-fixed font-medium">AI</span></span>
          </Link>
          <button
            className="lg:hidden text-white/70 hover:text-white"
            onClick={() => setSidebarOpen(false)}
            title="Uždaryti meniu"
            aria-label="Uždaryti meniu"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-4 py-8">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 relative group",
                  isActive
                    ? "bg-gradient-to-r from-primary to-primary-container text-white shadow-md shadow-black/10"
                    : "text-white/70 hover:bg-white/5 hover:text-white"
                )}
                onClick={() => setSidebarOpen(false)}
              >
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 h-8 w-1 rounded-r-full bg-tertiary-fixed" />
                )}
                <item.icon
                  className={cn("h-5 w-5 transition-transform group-hover:scale-110", isActive && "text-tertiary-fixed")}
                />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Bottom section */}
        <div className="p-4 mt-auto mb-4 px-4">
          <Link
            to="/nustatymai"
            className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-white/70 hover:bg-white/5 hover:text-white transition-all duration-200"
          >
            <Settings className="h-5 w-5" />
            Nustatymai
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-72 flex flex-col min-h-screen">
        {/* Top header - Surface Container Lowest to match Academic Architect */}
        <header className="sticky top-0 z-30 flex h-20 items-center justify-between bg-surface-container-lowest px-6 lg:px-8 shadow-[0_4px_32px_rgba(0,0,0,0.02)]">
          <div className="flex items-center gap-4">
            <button
              className="lg:hidden text-muted-foreground hover:text-foreground"
              onClick={() => setSidebarOpen(true)}
              title="Atidaryti meniu"
              aria-label="Atidaryti meniu"
            >
              <Menu className="h-6 w-6" />
            </button>

            {/* Title / Breadcrumb can go here if needed, for now keeping it clean */}
            <h1 className="text-xl font-semibold text-foreground hidden sm:block">Darbalaukis</h1>
          </div>

          <div className="flex items-center gap-6">
            <div className="relative hidden w-full max-w-sm sm:block">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Ieškoti darbų, klasių..."
                className="h-10 w-full rounded-full bg-surface-container-low pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all border-0"
              />
            </div>

            <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:bg-surface-container-low rounded-full h-10 w-10">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2 right-2 flex h-2 w-2 rounded-full bg-tertiary"></span>
            </Button>

            {/* User menu */}
            <button className="flex items-center gap-3 rounded-full hover:bg-surface-container-low p-1 pr-3 transition-colors border border-transparent hover:border-border">
              <img src="https://ui-avatars.com/api/?name=Mokytoja&background=0b513d&color=fff" alt="User" className="w-8 h-8 rounded-full" />
              <div className="hidden sm:block text-left">
                <p className="text-sm font-medium text-foreground leading-tight">Mokytoja</p>
                <p className="text-xs text-muted-foreground leading-tight">Admin</p>
              </div>
              <ChevronDown className="h-4 w-4 text-muted-foreground ml-1" />
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
