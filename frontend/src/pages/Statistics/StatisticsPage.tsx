/**
 * Statistics Page - Statistikos ir analizės puslapis
 */

import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Target,
  AlertTriangle,
  Award,
  BookOpen,
  RefreshCw,
  Download,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";

// === Sub-components ===

interface ProgressChartProps {
  data: Array<{ month: string; average: number }>;
}

function ProgressChart({ data }: ProgressChartProps) {
  const maxValue = Math.max(...data.map((d) => d.average), 10);

  return (
    <div className="space-y-4">
      <div className="flex items-end gap-2 h-48">
        {data.map((item, idx) => (
          <div key={idx} className="flex-1 flex flex-col items-center gap-1">
            <div
              className="w-full bg-primary rounded-t transition-all hover:bg-primary/80"
              style={{ height: `${(item.average / maxValue) * 100}%` }}
            />
            <span className="text-xs text-muted-foreground">
              {item.month.split("-")[1]}
            </span>
            <span className="text-sm font-medium">
              {item.average.toFixed(1)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

interface TopicAnalysisProps {
  topics: Array<{
    topic: string;
    accuracy: number;
    total_tasks: number;
    correct_count: number;
  }>;
}

function TopicAnalysis({ topics }: TopicAnalysisProps) {
  return (
    <div className="space-y-3">
      {topics.map((topic, idx) => (
        <div key={idx} className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{topic.topic}</span>
            <span className="text-sm text-muted-foreground">
              {topic.correct_count}/{topic.total_tasks} (
              {topic.accuracy.toFixed(0)}%)
            </span>
          </div>
          <Progress
            value={topic.accuracy}
            className={`h-2 ${
              topic.accuracy >= 70
                ? "[&>div]:bg-green-500"
                : topic.accuracy >= 50
                ? "[&>div]:bg-amber-500"
                : "[&>div]:bg-red-500"
            }`}
          />
        </div>
      ))}
    </div>
  );
}

interface ErrorPatternsProps {
  errors: Array<{
    error_type: string;
    description: string;
    frequency: number;
  }>;
}

function ErrorPatterns({ errors }: ErrorPatternsProps) {
  return (
    <div className="space-y-3">
      {errors.map((error, idx) => (
        <div
          key={idx}
          className="flex items-start gap-3 p-3 rounded-lg bg-red-50 border border-red-100"
        >
          <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className="text-red-600 border-red-200">
                {error.error_type}
              </Badge>
              <span className="text-sm text-red-600 font-medium">
                {error.frequency} kartų
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {error.description}
            </p>
          </div>
        </div>
      ))}

      {errors.length === 0 && (
        <p className="text-center text-muted-foreground py-4">
          Klaidų šablonų nerasta
        </p>
      )}
    </div>
  );
}

interface GradeDistributionProps {
  distribution: Record<string, number>;
}

function GradeDistribution({ distribution }: GradeDistributionProps) {
  const maxCount = Math.max(...Object.values(distribution), 1);

  return (
    <div className="space-y-2">
      {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((grade) => {
        const count = distribution[String(grade)] || 0;
        const width = (count / maxCount) * 100;

        return (
          <div key={grade} className="flex items-center gap-2">
            <span className="w-6 text-right text-sm font-medium">{grade}</span>
            <div className="flex-1 h-6 bg-gray-100 rounded overflow-hidden">
              <div
                className={`h-full transition-all ${
                  grade >= 9
                    ? "bg-green-500"
                    : grade >= 7
                    ? "bg-blue-500"
                    : grade >= 5
                    ? "bg-amber-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${width}%` }}
              />
            </div>
            <span className="w-8 text-sm text-muted-foreground">{count}</span>
          </div>
        );
      })}
    </div>
  );
}

// === Main Component ===

export default function StatisticsPage() {
  const [selectedClass, setSelectedClass] = useState<string>("all");

  // Bendros statistikos
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ["statistics-overview"],
    queryFn: async () => {
      const response = await api.get("/statistics/overview");
      return response.data;
    },
  });

  // Temų statistika
  const { data: topics = [], isLoading: topicsLoading } = useQuery({
    queryKey: ["statistics-topics"],
    queryFn: async () => {
      const response = await api.get("/statistics/topics");
      return response.data;
    },
  });

  // Klaidų šablonai
  const { data: errors = [], isLoading: errorsLoading } = useQuery({
    queryKey: ["statistics-errors"],
    queryFn: async () => {
      const response = await api.get("/statistics/errors");
      return response.data;
    },
  });

  // Tendencijų duomenys - tuščia kai nėra realiu duomenų
  const trendData: { month: string; average: number }[] = [];

  // Pažymių pasiskirstymas - tuščias kai nėra realiu duomenų
  const gradeDistribution: Record<string, number> = {};

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <PageHeader
          title="Statistika"
          description="Klasės ir mokinių pažangos analizė"
        />

        <div className="flex items-center gap-2">
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="h-10 px-3 py-2 rounded-md border bg-background text-sm w-40"
          >
            <option value="all">Visos klasės</option>
            <option value="5a">5a</option>
            <option value="5b">5b</option>
            <option value="6a">6a</option>
            <option value="6b">6b</option>
          </select>

          <Button variant="outline" size="icon">
            <RefreshCw className="h-4 w-4" />
          </Button>

          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Eksportuoti
          </Button>
        </div>
      </div>

      {/* Statistikos kortelės */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Mokiniai</p>
                <p className="text-2xl font-bold">
                  {overview?.students_count || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Vidurkis</p>
                <div className="flex items-center gap-1">
                  <p className="text-2xl font-bold">
                    {overview?.average_grade?.toFixed(1) || "—"}
                  </p>
                  <TrendingUp className="h-4 w-4 text-green-500" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Kontroliniai</p>
                <p className="text-2xl font-bold">
                  {overview?.tests_count || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-amber-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">
                  Laukia tikrinimo
                </p>
                <p className="text-2xl font-bold">
                  {overview?.pending_count || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Apžvalga</TabsTrigger>
          <TabsTrigger value="topics">Temos</TabsTrigger>
          <TabsTrigger value="errors">Klaidos</TabsTrigger>
          <TabsTrigger value="students">Mokiniai</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Pažymių tendencija */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Pažymių tendencija
                </CardTitle>
                <CardDescription>
                  Vidutinis pažymys per paskutinius mėnesius
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ProgressChart data={trendData} />
              </CardContent>
            </Card>

            {/* Pažymių pasiskirstymas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Pažymių pasiskirstymas
                </CardTitle>
                <CardDescription>
                  Kiek mokinių gavo kiekvieną pažymį
                </CardDescription>
              </CardHeader>
              <CardContent>
                <GradeDistribution distribution={gradeDistribution} />
              </CardContent>
            </Card>
          </div>

          {/* Top mokiniai */}
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-600">
                  <Award className="h-5 w-5" />
                  Geriausi mokiniai
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-6 text-muted-foreground">
                  <p>Įkelkite ir patikrinkite darbus,</p>
                  <p className="text-sm">
                    kad pamatytumėte geriausius mokinius
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-amber-600">
                  <TrendingDown className="h-5 w-5" />
                  Reikia pagalbos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-6 text-muted-foreground">
                  <p>Įkelkite ir patikrinkite darbus,</p>
                  <p className="text-sm">
                    kad pamatytumėte kas reikia pagalbos
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="topics">
          <Card>
            <CardHeader>
              <CardTitle>Temų analizė</CardTitle>
              <CardDescription>
                Kaip mokiniams sekasi su skirtingomis temomis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {topicsLoading ? (
                <p className="text-center text-muted-foreground py-8">
                  Kraunama...
                </p>
              ) : topics.length > 0 ? (
                <TopicAnalysis topics={topics} />
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>Dar nėra temų statistikos</p>
                  <p className="text-sm mt-1">
                    Įkelkite ir patikrinkite darbus, kad pamatytumėte temų
                    analizę
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors">
          <Card>
            <CardHeader>
              <CardTitle>Dažniausios klaidos</CardTitle>
              <CardDescription>
                Užduotys, kuriose mokiniai dažniausiai klysta
              </CardDescription>
            </CardHeader>
            <CardContent>
              {errorsLoading ? (
                <p className="text-center text-muted-foreground py-8">
                  Kraunama...
                </p>
              ) : errors.length > 0 ? (
                <ErrorPatterns errors={errors} />
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>Dar nėra klaidų statistikos</p>
                  <p className="text-sm mt-1">
                    Įkelkite ir patikrinkite darbus, kad pamatytumėte
                    dažniausias klaidas
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="students">
          <Card>
            <CardHeader>
              <CardTitle>Mokinių statistika</CardTitle>
              <CardDescription>
                Individualūs rezultatai ir pažanga
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-center text-muted-foreground py-8">
                Pasirinkite mokinį iš mokinių sąrašo, kad pamatytumėte jo
                statistiką
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
