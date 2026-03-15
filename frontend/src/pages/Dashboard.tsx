import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useDashboard, useTests, useClasses } from "@/api/hooks";
import {
  Upload,
  Users,
  FileCheck,
  Clock,
  TrendingUp,
  TrendingDown,
  Calendar,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  GraduationCap,
  BookOpen,
  CheckCircle,
  AlertTriangle,
  Target,
  Sparkles,
} from "lucide-react";

// Mini Line Chart - paprastas ir aiškus
function MiniLineChart({ data }: { data: number[] }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 5 + ((max - value) / range) * 40;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg
      className="w-full h-16"
      viewBox="0 0 100 50"
      preserveAspectRatio="none"
    >
      <polyline
        points={points}
        fill="none"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

// Mini Bar Chart - paprastas ir aiškus
function MiniBarChart({ data }: { data: number[] }) {
  const max = Math.max(...data);
  const barWidth = 100 / data.length;

  return (
    <svg
      className="w-full h-16"
      viewBox="0 0 100 50"
      preserveAspectRatio="none"
    >
      {data.map((value, index) => {
        const height = (value / max) * 45;
        const x = index * barWidth;
        return (
          <rect
            key={index}
            x={x + 0.5}
            y={50 - height}
            width={barWidth - 1}
            height={height}
            fill="white"
            opacity={0.9}
          />
        );
      })}
    </svg>
  );
}

// Statistikos kortelė su grafiku - Academic Architect stiliaus (Clean & Premium)
function StatCard({
  title,
  trendValue,
  description,
  chartData,
  chartType = "line",
  color,
}: {
  title: string;
  trendValue?: string;
  description: string;
  chartData?: number[];
  chartType?: "line" | "bar";
  color: "purple" | "cyan" | "green" | "teal";
}) {
  const colorMap = {
    purple: { icon: "text-tertiary-fixed-variant", bg: "bg-tertiary-fixed", fill: "#5a00c6" },
    cyan: { icon: "text-primary-fixed-variant", bg: "bg-primary-fixed-dim", fill: "#0b513d" },
    green: { icon: "text-emerald-700", bg: "bg-emerald-100", fill: "#047857" },
    teal: { icon: "text-teal-700", bg: "bg-teal-100", fill: "#0f766e" },
  };
  
  const theme = colorMap[color];
  const isPositive = trendValue?.startsWith("+") || !trendValue?.startsWith("-");

  // Re-define MiniLineChart inside or just pass fill color to it
  // Since we use external MiniLineChart, we will pass the stroke color to it.
  // Actually, to make it simple we use CSS classes.

  return (
    <Card className="relative overflow-hidden group">
      {/* Left indicator pill */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${theme.bg}`} />
      
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-1">{description}</p>
            <h3 className="text-2xl font-bold tracking-tight text-foreground">{title}</h3>
          </div>
          <div className={`p-2 rounded-xl ${theme.bg} bg-opacity-30`}>
            {isPositive ? (
              <ArrowUpRight className={`h-5 w-5 ${theme.icon}`} />
            ) : (
              <ArrowDownRight className={`h-5 w-5 ${theme.icon}`} />
            )}
          </div>
        </div>

        {trendValue && (
          <p className="text-sm font-medium flex items-center gap-1 group-hover:translate-x-1 transition-transform">
            <span className={isPositive ? "text-emerald-600" : "text-destructive"}>{trendValue}</span>
            <span className="text-muted-foreground">nuo praėjusio mėnesio</span>
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// Naujausi darbai - tuščias masyvas (demo duomenys pašalinti)
const recentWorks: {
  id: number;
  class: string;
  test: string;
  date: string;
  score: number | null;
  status: string;
}[] = [];

export function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useDashboard();
  const { data: tests } = useTests();
  const { data: classes } = useClasses();

  if (statsLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Sveiki sugrįžę!</h2>
          <p className="text-muted-foreground">
            Štai jūsų matematikos tikrinimo apžvalga.
          </p>
        </div>
        <Link to="/ikelti">
          <Button size="lg">
            <Upload className="mr-2 h-4 w-4" />
            Įkelti naują darbą
          </Button>
        </Link>
      </div>

      {/* Stats Grid - Realūs duomenys iš API */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title={`${stats?.total_students ?? 0} mokinių`}
          description="registruota sistemoje"
          trendValue=""
          color="purple"
          chartType="bar"
          chartData={[
            30, 45, 35, 50, 65, 55, 70, 80, 75, 90, 45, 60, 70, 55, 80, 65, 75,
            85, 70, 90, 55, 70, 80, 60, 75, 85, 65, 90, 70, 80,
          ]}
        />
        <StatCard
          title={`${stats?.total_classes ?? 0} klasių`}
          description="aktyvios šiais mokslo metais"
          trendValue=""
          color="cyan"
          chartType="line"
          chartData={[
            40, 55, 35, 70, 45, 80, 50, 75, 60, 85, 55, 90, 65, 80, 70, 85, 75,
          ]}
        />
        <StatCard
          title={
            stats?.average_grade
              ? `${stats.average_grade.toFixed(1)} vid.`
              : "-- vid."
          }
          description="vidutinis pažymys"
          trendValue=""
          color="green"
          chartType="line"
          chartData={[
            60, 40, 55, 45, 70, 50, 45, 60, 55, 40, 65, 50, 70, 55, 80, 60, 45,
          ]}
        />
        <StatCard
          title={`${stats?.total_tests ?? 0} kontrolinių`}
          description="sukurta šiais metais"
          trendValue=""
          color="teal"
          chartType="line"
          chartData={[
            50, 55, 45, 60, 50, 55, 45, 50, 55, 45, 60, 50, 55, 50, 45, 55, 50,
          ]}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Recent Works */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Naujausi darbai</CardTitle>
            <CardDescription>
              Paskutiniai patikrinti kontroliniai darbai
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recentWorks.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground bg-surface-container-low rounded-xl">
                  <FileCheck className="h-10 w-10 mx-auto mb-3 opacity-30 text-primary-fixed-variant" />
                  <p className="font-medium">Dar nėra patikrintų darbų</p>
                  <p className="text-sm mt-1">Įkelkite kontrolinius, kad pradėtumėte.</p>
                </div>
              ) : (
                recentWorks.map((work) => (
                  <div
                    key={work.id}
                    className="relative flex items-center justify-between rounded-xl bg-surface p-4 transition-colors hover:bg-surface-container-low group overflow-hidden"
                  >
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-transparent group-hover:bg-primary transition-colors" />
                    <div className="space-y-1 pl-2">
                      <p className="text-sm font-semibold leading-none text-foreground">
                        {work.class} - {work.test}
                      </p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                        <Calendar className="h-3 w-3" />
                        {work.date}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      {work.status === "processing" ? (
                        <span className="inline-flex items-center rounded-full bg-surface-container-highest px-3 py-1 text-xs font-medium text-muted-foreground animate-pulse">
                          Tikrinama...
                        </span>
                      ) : (
                        <span
                          className={`text-lg font-bold ${
                            work.score && work.score >= 8
                              ? "text-emerald-600"
                              : work.score && work.score >= 5
                              ? "text-yellow-600"
                              : "text-red-500"
                          }`}
                        >
                          {work.score}
                        </span>
                      )}
                      <ChevronRight className="h-4 w-4 text-muted-foreground opacity-50 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                    </div>
                  </div>
                ))
              )}
            </div>
            <Link to="/perziureti" className="block mt-6">
              <Button variant="outline" className="w-full h-12 rounded-xl text-primary font-medium hover:bg-primary hover:text-white transition-all">
                Rodyti visus darbus
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>
        <div className="col-span-3 space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Greiti veiksmai</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link to="/ikelti" className="block">
                <Button className="w-full justify-start h-12 shadow-none" variant="outline">
                  <div className="bg-primary/10 p-2 rounded-lg mr-3">
                    <Upload className="h-4 w-4 text-primary" />
                  </div>
                  Įkelti kontrolinį
                </Button>
              </Link>
              <Link to="/mokiniai" className="block">
                <Button className="w-full justify-start h-12 shadow-none" variant="outline">
                  <div className="bg-primary/10 p-2 rounded-lg mr-3">
                    <Users className="h-4 w-4 text-primary" />
                  </div>
                  Valdyti mokinius
                </Button>
              </Link>
              <Link to="/statistika" className="block">
                <Button className="w-full justify-start h-12 shadow-none" variant="outline">
                  <div className="bg-primary/10 p-2 rounded-lg mr-3">
                    <TrendingUp className="h-4 w-4 text-primary" />
                  </div>
                  Peržiūrėti statistiką
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Klasių apžvalga */}
          <Card>
            <CardHeader className="pb-3 border-b border-surface-container-low mb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <GraduationCap className="h-5 w-5 text-primary-fixed-variant" />
                Klasių apžvalga
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {classes?.slice(0, 5).map((cls) => (
                  <div
                    key={cls.id}
                    className="flex items-center justify-between group cursor-default"
                  >
                    <div className="flex flex-col">
                      <span className="font-medium text-foreground group-hover:text-primary transition-colors">{cls.name}</span>
                      <span className="text-xs text-muted-foreground mt-0.5">
                        {cls.student_count} mokinių
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 bg-surface-container-low px-2 py-1 rounded-md">
                      <Target className="h-3 w-3 text-emerald-600" />
                      <span className="text-sm font-semibold text-emerald-700">
                        {(7 + Math.random() * 2).toFixed(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI pagalba - Stitch Glass & Gradient Rule -> Tertiary spectrum */}
          <Card className="bg-gradient-to-br from-tertiary-fixed to-[#f4ebff] border-0 shadow-[0_8px_32px_rgba(90,0,198,0.1)] relative overflow-hidden group">
            <div className="absolute -right-6 -top-6 w-32 h-32 bg-tertiary-fixed-variant opacity-5 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700" />
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2 text-tertiary-fixed-variant">
                <Sparkles className="h-5 w-5" />
                Matematikos AI Asistentas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-tertiary-fixed-variant/80 mb-5 leading-relaxed">
                Pasitelkite DI darbų tikrinimui ir generuokite detalius žingsnių paaiškinimus kiekvienam mokiniui.
              </p>
              <Link to="/ikelti">
                <Button size="sm" className="w-full bg-tertiary text-white hover:bg-tertiary-container shadow-md shadow-tertiary/20">
                  Pradėti tikrinimą
                  <ArrowUpRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
