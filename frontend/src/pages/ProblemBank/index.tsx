/**
 * ProblemBankPage — Uždavinių bazės statistika ir naršyklė.
 *
 * Rodo:
 * - Bendrą statistiką (kortelės)
 * - Šaltinių pasiskirstymą (horizontalūs barų grafikai)
 * - Sunkumo/klasių pasiskirstymą
 * - Uždavinių lentelę su filtrais
 */

import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  useProblemBankStats,
  useProblemBank,
} from "@/api/hooks";
import {
  Database,
  BarChart3,
  BookOpen,
  Shield,
  TrendingUp,
  Search,
  ChevronLeft,
  ChevronRight,
  Filter,
  Layers,
  GraduationCap,
  Zap,
} from "lucide-react";

// === Spalvos ir labeliai ===
const SOURCE_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  GSM8K: { label: "GSM8K", color: "bg-blue-500", bg: "bg-blue-50 text-blue-700" },
  NUMINA_MATH: { label: "NuminaMath", color: "bg-violet-500", bg: "bg-violet-50 text-violet-700" },
  MATH_INSTRUCT: { label: "MathInstruct", color: "bg-amber-500", bg: "bg-amber-50 text-amber-700" },
  COMPETITION_MATH: { label: "Competition", color: "bg-rose-500", bg: "bg-rose-50 text-rose-700" },
  AMPS: { label: "AMPS (Khan)", color: "bg-emerald-500", bg: "bg-emerald-50 text-emerald-700" },
  AOPS: { label: "AoPS", color: "bg-cyan-500", bg: "bg-cyan-50 text-cyan-700" },
  OPEN_MATH: { label: "OpenMath", color: "bg-indigo-500", bg: "bg-indigo-50 text-indigo-700" },
  GEMINI: { label: "Gemini AI", color: "bg-teal-500", bg: "bg-teal-50 text-teal-700" },
};

const DIFFICULTY_CONFIG: Record<string, { label: string; color: string; emoji: string }> = {
  EASY: { label: "Lengvas", color: "bg-green-500", emoji: "🟢" },
  MEDIUM: { label: "Vidutinis", color: "bg-amber-500", emoji: "🟡" },
  HARD: { label: "Sunkus", color: "bg-orange-500", emoji: "🟠" },
  OLYMPIAD: { label: "Olimpiadinis", color: "bg-red-500", emoji: "🔴" },
};

function StatCard({ icon: Icon, title, value, subtitle, color }: {
  icon: typeof Database;
  title: string;
  value: string | number;
  subtitle?: string;
  color: string;
}) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow group">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold tracking-tight text-foreground">
            {typeof value === "number" ? value.toLocaleString("lt-LT") : value}
          </p>
          {subtitle && (
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          )}
        </div>
        <div className={cn(
          "flex h-12 w-12 items-center justify-center rounded-xl transition-transform group-hover:scale-110",
          color
        )}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
}

function HorizontalBar({ label, value, max, color, percentage }: {
  label: string;
  value: number;
  max: number;
  color: string;
  percentage: number;
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-gray-700">{label}</span>
        <span className="text-gray-500 tabular-nums">
          {value.toLocaleString("lt-LT")} <span className="text-gray-400">({percentage.toFixed(1)}%)</span>
        </span>
      </div>
      <div className="h-3 rounded-full bg-gray-100 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-700 ease-out", color)}
          style={{ width: `${Math.max((value / max) * 100, 1)}%` }}
        />
      </div>
    </div>
  );
}

export function ProblemBankPage() {
  const { data: stats, isLoading: statsLoading } = useProblemBankStats();

  // Filtrų state
  const [page, setPage] = useState(1);
  const [gradeFilter, setGradeFilter] = useState<number | undefined>();
  const [difficultyFilter, setDifficultyFilter] = useState<string | undefined>();
  const [sourceFilter, setSourceFilter] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState("");

  const { data: problems, isLoading: problemsLoading } = useProblemBank({
    page,
    per_page: 15,
    grade: gradeFilter,
    difficulty: difficultyFilter,
    source: sourceFilter,
    search: searchQuery || undefined,
  });

  // Kortelių duomenys
  const totalProblems = stats?.total_problems ?? 0;
  const sourcesCount = stats?.by_source ? Object.keys(stats.by_source).length : 0;
  const maxSourceValue = stats?.by_source
    ? Math.max(...Object.values(stats.by_source))
    : 1;
  const maxDifficultyValue = stats?.by_difficulty
    ? Math.max(...Object.values(stats.by_difficulty))
    : 1;

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin inline-block w-10 h-10 border-4 border-primary border-t-transparent rounded-full" />
          <p className="text-muted-foreground">Kraunama uždavinių bazė...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Antraštė */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Uždavinių bazė</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Matematikos uždavinių statistika ir naršymas
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-surface-container-low px-3 py-1.5 rounded-full">
          <Database className="w-3.5 h-3.5" />
          {sourcesCount} šaltiniai
        </div>
      </div>

      {/* === Stat kortelės === */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Database}
          title="Viso uždavinių"
          value={totalProblems}
          subtitle="aktyvių bazėje"
          color="bg-gradient-to-br from-primary to-primary-container"
        />
        <StatCard
          icon={Layers}
          title="Šaltiniai"
          value={sourcesCount}
          subtitle="HuggingFace dataset'ai"
          color="bg-gradient-to-br from-violet-500 to-violet-600"
        />
        <StatCard
          icon={Shield}
          title="Patikrinti"
          value={stats?.verified_count ?? 0}
          subtitle={`iš ${totalProblems.toLocaleString("lt-LT")}`}
          color="bg-gradient-to-br from-emerald-500 to-emerald-600"
        />
        <StatCard
          icon={TrendingUp}
          title="Olimpiadiniai"
          value={stats?.by_difficulty?.OLYMPIAD ?? 0}
          subtitle="aukščiausias lygis"
          color="bg-gradient-to-br from-rose-500 to-rose-600"
        />
      </div>

      {/* === Grafikai === */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Šaltiniai */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-5">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground">Pagal šaltinį</h2>
          </div>
          <div className="space-y-3">
            {stats?.by_source &&
              Object.entries(stats.by_source)
                .sort(([, a], [, b]) => b - a)
                .map(([source, count]) => {
                  const config = SOURCE_CONFIG[source] || {
                    label: source,
                    color: "bg-gray-400",
                  };
                  return (
                    <HorizontalBar
                      key={source}
                      label={config.label}
                      value={count}
                      max={maxSourceValue}
                      color={config.color}
                      percentage={(count / totalProblems) * 100}
                    />
                  );
                })}
          </div>
        </div>

        {/* Sunkumas + Klasės */}
        <div className="space-y-6">
          {/* Sunkumas */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-5">
              <Zap className="w-5 h-5 text-amber-500" />
              <h2 className="text-lg font-semibold text-foreground">Pagal sunkumą</h2>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {stats?.by_difficulty &&
                Object.entries(stats.by_difficulty)
                  .sort(([, a], [, b]) => b - a)
                  .map(([diff, count]) => {
                    const config = DIFFICULTY_CONFIG[diff] || {
                      label: diff,
                      emoji: "⚪",
                      color: "bg-gray-400",
                    };
                    return (
                      <div
                        key={diff}
                        className="flex items-center gap-3 rounded-xl bg-gray-50 p-3 hover:bg-gray-100 transition-colors"
                      >
                        <span className="text-xl">{config.emoji}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-700">{config.label}</p>
                          <p className="text-lg font-bold text-gray-900 tabular-nums">
                            {count.toLocaleString("lt-LT")}
                          </p>
                        </div>
                      </div>
                    );
                  })}
            </div>
          </div>

          {/* Klasės */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-5">
              <GraduationCap className="w-5 h-5 text-tertiary" />
              <h2 className="text-lg font-semibold text-foreground">Pagal klases</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {stats?.by_grade &&
                Object.entries(stats.by_grade)
                  .sort(([a], [b]) => Number(a) - Number(b))
                  .map(([grade, count]) => (
                    <div
                      key={grade}
                      className="flex flex-col items-center px-3 py-2 rounded-xl bg-gray-50 hover:bg-primary/5 transition-colors min-w-[60px]"
                    >
                      <span className="text-xs text-muted-foreground">{grade} kl.</span>
                      <span className="text-sm font-bold text-foreground tabular-nums">
                        {count >= 1000
                          ? `${(count / 1000).toFixed(1)}K`
                          : count.toLocaleString("lt-LT")}
                      </span>
                    </div>
                  ))}
            </div>
          </div>
        </div>
      </div>

      {/* === Uždavinių naršyklė === */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
        {/* Filtrai */}
        <div className="p-5 border-b border-gray-100">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground">Uždavinių naršyklė</h2>
            {problems && (
              <span className="text-xs text-muted-foreground ml-auto">
                Rasta: {problems.total.toLocaleString("lt-LT")}
              </span>
            )}
          </div>

          <div className="flex flex-wrap gap-3">
            {/* Paieška */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Ieškoti uždavinių..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary bg-gray-50"
              />
            </div>

            {/* Klasė */}
            <select
              value={gradeFilter ?? ""}
              onChange={(e) => {
                setGradeFilter(e.target.value ? Number(e.target.value) : undefined);
                setPage(1);
              }}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 bg-gray-50"
            >
              <option value="">Visos klasės</option>
              {[5, 6, 7, 8, 9, 10, 11, 12].map((g) => (
                <option key={g} value={g}>
                  {g} klasė
                </option>
              ))}
            </select>

            {/* Sunkumas */}
            <select
              value={difficultyFilter ?? ""}
              onChange={(e) => {
                setDifficultyFilter(e.target.value || undefined);
                setPage(1);
              }}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 bg-gray-50"
            >
              <option value="">Visi sunkumai</option>
              {Object.entries(DIFFICULTY_CONFIG).map(([key, cfg]) => (
                <option key={key} value={key.toLowerCase()}>
                  {cfg.emoji} {cfg.label}
                </option>
              ))}
            </select>

            {/* Šaltinis */}
            <select
              value={sourceFilter ?? ""}
              onChange={(e) => {
                setSourceFilter(e.target.value || undefined);
                setPage(1);
              }}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 bg-gray-50"
            >
              <option value="">Visi šaltiniai</option>
              {Object.entries(SOURCE_CONFIG).map(([key, cfg]) => (
                <option key={key} value={key.toLowerCase()}>
                  {cfg.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Lentelė */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50/80 text-muted-foreground">
                <th className="text-left py-3 px-4 font-medium">ID</th>
                <th className="text-left py-3 px-4 font-medium">Šaltinis</th>
                <th className="text-left py-3 px-4 font-medium max-w-xs">Uždavinys</th>
                <th className="text-left py-3 px-4 font-medium">Klasės</th>
                <th className="text-left py-3 px-4 font-medium">Sunkumas</th>
                <th className="text-center py-3 px-4 font-medium">Naudotas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {problemsLoading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-muted-foreground">
                    <div className="animate-spin inline-block w-5 h-5 border-2 border-primary border-t-transparent rounded-full mb-2" />
                    <p>Kraunama...</p>
                  </td>
                </tr>
              ) : problems?.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-muted-foreground">
                    Nerasta uždavinių pagal filtrą
                  </td>
                </tr>
              ) : (
                problems?.items.map((p) => {
                  const srcCfg = SOURCE_CONFIG[p.source] || {
                    label: p.source,
                    bg: "bg-gray-100 text-gray-600",
                  };
                  const diffCfg = DIFFICULTY_CONFIG[p.difficulty] || {
                    emoji: "⚪",
                    label: p.difficulty,
                  };
                  return (
                    <tr
                      key={p.id}
                      className="hover:bg-gray-50/50 transition-colors"
                    >
                      <td className="py-3 px-4 text-gray-400 tabular-nums text-xs">
                        #{p.id}
                      </td>
                      <td className="py-3 px-4">
                        <span className={cn("text-xs px-2 py-1 rounded-full font-medium", srcCfg.bg)}>
                          {srcCfg.label}
                        </span>
                      </td>
                      <td className="py-3 px-4 max-w-xs">
                        <p className="line-clamp-2 text-gray-700 text-xs leading-relaxed">
                          {p.question_lt || p.question_en || "—"}
                        </p>
                      </td>
                      <td className="py-3 px-4 text-xs text-gray-500 whitespace-nowrap">
                        {p.grade_min}–{p.grade_max} kl.
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="text-xs">
                          {diffCfg.emoji} {diffCfg.label}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center text-xs text-gray-400 tabular-nums">
                        {p.times_used}×
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Puslapiavimas */}
        {problems && problems.pages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-gray-100">
            <p className="text-xs text-muted-foreground">
              Puslapis {problems.page} iš {problems.pages}
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              {Array.from({ length: Math.min(5, problems.pages) }, (_, i) => {
                const startPage = Math.max(
                  1,
                  Math.min(page - 2, problems.pages - 4),
                );
                const pageNum = startPage + i;
                if (pageNum > problems.pages) return null;
                return (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={cn(
                      "w-8 h-8 rounded-lg text-xs font-medium transition-colors",
                      pageNum === page
                        ? "bg-primary text-white shadow-sm"
                        : "hover:bg-gray-100 text-gray-600",
                    )}
                  >
                    {pageNum}
                  </button>
                );
              })}
              <button
                onClick={() => setPage((p) => Math.min(problems.pages, p + 1))}
                disabled={page >= problems.pages}
                className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProblemBankPage;
