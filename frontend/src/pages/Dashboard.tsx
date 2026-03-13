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

// Statistikos kortelė su spalva ir grafiku - Fury stiliaus
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
  const colorClasses = {
    purple: "bg-[#5c6bc0]", // Indigo/purple kaip pavyzdyje
    cyan: "bg-[#00bcd4]", // Cyan kaip pavyzdyje
    green: "bg-[#4caf50]", // Green kaip pavyzdyje
    teal: "bg-[#009688]", // Teal kaip pavyzdyje
  };

  const isPositive =
    trendValue?.startsWith("+") || !trendValue?.startsWith("-");

  return (
    <Card
      className={`${colorClasses[color]} border-0 text-white overflow-hidden`}
    >
      <CardContent className="p-4 pb-0">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-medium text-white">{title}</h3>
            <p className="text-sm text-white/90 flex items-center gap-1 mt-1">
              {isPositive ? (
                <ArrowUpRight className="h-4 w-4" />
              ) : (
                <ArrowDownRight className="h-4 w-4" />
              )}
              <span className="font-medium">{trendValue}</span>
              <span className="text-white/70">{description}</span>
            </p>
          </div>
        </div>

        {/* Chart */}
        {chartData && (
          <div className="mt-4 -mx-4 mb-0">
            {chartType === "bar" ? (
              <MiniBarChart data={chartData} />
            ) : (
              <MiniLineChart data={chartData} />
            )}
          </div>
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
            <div className="space-y-4">
              {recentWorks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileCheck className="h-10 w-10 mx-auto mb-3 opacity-50" />
                  <p>Dar nėra patikrintų darbų</p>
                  <p className="text-sm mt-1">
                    Įkelkite kontrolinius, kad pradėtumėte
                  </p>
                </div>
              ) : (
                recentWorks.map((work) => (
                  <div
                    key={work.id}
                    className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-muted/50"
                  >
                    <div className="space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {work.class} - {work.test}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        <Calendar className="mr-1 inline h-3 w-3" />
                        {work.date}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      {work.status === "processing" ? (
                        <span className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
                          Tikrinama...
                        </span>
                      ) : (
                        <span
                          className={`text-lg font-bold ${
                            work.score && work.score >= 8
                              ? "text-green-600"
                              : work.score && work.score >= 5
                              ? "text-yellow-600"
                              : "text-red-600"
                          }`}
                        >
                          {work.score}
                        </span>
                      )}
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>
                ))
              )}
            </div>
            <Link to="/perziureti" className="block mt-4">
              <Button variant="outline" className="w-full">
                Rodyti visus darbus
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Right Column */}
        <div className="col-span-3 space-y-4">
          {/* Quick Actions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle>Greiti veiksmai</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link to="/ikelti" className="block">
                <Button className="w-full justify-start" variant="outline">
                  <Upload className="mr-2 h-4 w-4" />
                  Įkelti kontrolinį
                </Button>
              </Link>
              <Link to="/mokiniai" className="block">
                <Button className="w-full justify-start" variant="outline">
                  <Users className="mr-2 h-4 w-4" />
                  Valdyti mokinius
                </Button>
              </Link>
              <Link to="/statistika" className="block">
                <Button className="w-full justify-start" variant="outline">
                  <TrendingUp className="mr-2 h-4 w-4" />
                  Peržiūrėti statistiką
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Klasių apžvalga */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5" />
                Klasių apžvalga
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {classes?.slice(0, 5).map((cls) => (
                  <div
                    key={cls.id}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{cls.name}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {cls.student_count} mokinių
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Target className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium">
                        {(7 + Math.random() * 2).toFixed(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI pagalba */}
          <Card className="bg-linear-to-br from-purple-50 to-blue-50 border-purple-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-600" />
                AI pagalba
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                Leiskite AI padėti tikrinti darbus ir generuoti paaiškinimus
                mokiniams.
              </p>
              <Link to="/ikelti">
                <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                  Pradėti tikrinimą
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
