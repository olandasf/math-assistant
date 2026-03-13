/**
 * Results Page - Tikrinimo rezultatų peržiūra ir redagavimas
 *
 * Čia mokytoja mato:
 * - Mokinio atsakymų tikrinimo rezultatus
 * - Klaidas su AI paaiškinimais
 * - Galimybę keisti pažymį
 * - PDF eksportą
 */

import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui";
import { Separator } from "@/components/ui";
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Lightbulb,
  FileDown,
  ChevronLeft,
  ChevronRight,
  Edit3,
  Save,
  Sparkles,
  Loader2,
  Calculator,
  BookOpen,
  MessageSquare,
  ArrowLeft,
  AlertTriangle,
  ChevronDown,
} from "lucide-react";
import { MathText } from "@/components/ui/MathRenderer";
import { useMutation } from "@tanstack/react-query";
import api from "@/api/client";

// === Šablonų tipai ===
interface ErrorTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: "minor" | "moderate" | "major";
  pointsDeduction: number;
  explanation: string;
}

interface CommentTemplate {
  id: string;
  name: string;
  text: string;
  category: string;
  tone: "positive" | "neutral" | "constructive";
}

// Gauti šablonus iš localStorage
const getErrorTemplates = (): ErrorTemplate[] => {
  const saved = localStorage.getItem("errorTemplates");
  return saved ? JSON.parse(saved) : [];
};

const getCommentTemplates = (): CommentTemplate[] => {
  const saved = localStorage.getItem("commentTemplates");
  return saved ? JSON.parse(saved) : [];
};

// === Tipos ===
interface TaskResult {
  id: number;
  number: number;
  question: string;
  studentAnswer: string;
  correctAnswer: string;
  isCorrect: boolean;
  points: number;
  maxPoints: number;
  explanation?: string;
  suggestions?: string[];
}

interface SubmissionResult {
  id: number;
  studentName: string;
  studentCode: string;
  className: string;
  testTitle: string;
  testDate: string;
  variant: string;
  grade: number;
  totalPoints: number;
  maxPoints: number;
  tasks: TaskResult[];
  teacherComments?: string;
}

// === Sub-components ===

interface ErrorMarkerProps {
  isCorrect: boolean;
  points: number;
  maxPoints: number;
}

function ErrorMarker({ isCorrect, points, maxPoints }: ErrorMarkerProps) {
  if (isCorrect) {
    return (
      <div className="flex items-center gap-2 text-green-600">
        <CheckCircle2 className="h-5 w-5" />
        <span className="font-medium">
          {points}/{maxPoints} tšk.
        </span>
      </div>
    );
  }

  if (points > 0) {
    return (
      <div className="flex items-center gap-2 text-amber-600">
        <AlertCircle className="h-5 w-5" />
        <span className="font-medium">
          {points}/{maxPoints} tšk.
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-red-600">
      <XCircle className="h-5 w-5" />
      <span className="font-medium">0/{maxPoints} tšk.</span>
    </div>
  );
}

interface SolutionDisplayProps {
  task: TaskResult;
  onEdit: (taskId: number, newAnswer: string) => void;
  onApplyErrorTemplate: (taskId: number, template: ErrorTemplate) => void;
}

function SolutionDisplay({
  task,
  onEdit,
  onApplyErrorTemplate,
}: SolutionDisplayProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedAnswer, setEditedAnswer] = useState(task.studentAnswer);
  const [showErrorTemplates, setShowErrorTemplates] = useState(false);
  const errorTemplates = getErrorTemplates();

  const handleSave = () => {
    onEdit(task.id, editedAnswer);
    setIsEditing(false);
  };

  return (
    <Card
      className={`border-l-4 ${
        task.isCorrect
          ? "border-l-green-500 bg-green-50/50"
          : task.points > 0
          ? "border-l-amber-500 bg-amber-50/50"
          : "border-l-red-500 bg-red-50/50"
      }`}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="text-base px-3 py-1">
              {task.number}
            </Badge>
            <CardTitle className="text-base font-medium">
              <MathText text={task.question} />
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <ErrorMarker
              isCorrect={task.isCorrect}
              points={task.points}
              maxPoints={task.maxPoints}
            />
            {/* Klaidos šablono pasirinkimas */}
            {!task.isCorrect && errorTemplates.length > 0 && (
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowErrorTemplates(!showErrorTemplates)}
                  className="text-amber-600 hover:text-amber-700"
                >
                  <AlertTriangle className="h-4 w-4 mr-1" />
                  Šablonas
                  <ChevronDown className="h-3 w-3 ml-1" />
                </Button>

                {showErrorTemplates && (
                  <div className="absolute right-0 top-full mt-1 z-10 w-64 bg-white border rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
                    {errorTemplates.map((template) => (
                      <button
                        key={template.id}
                        className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex flex-col gap-0.5"
                        onClick={() => {
                          onApplyErrorTemplate(task.id, template);
                          setShowErrorTemplates(false);
                        }}
                      >
                        <span className="font-medium">{template.name}</span>
                        <span className="text-xs text-muted-foreground">
                          {template.description}
                        </span>
                        <span className="text-xs text-amber-600">
                          -{template.pointsDeduction} tšk.
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Mokinio atsakymas */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-sm text-muted-foreground flex items-center gap-1">
              <Edit3 className="h-3 w-3" />
              Mokinio atsakymas
            </Label>
            {isEditing ? (
              <div className="flex gap-2 mt-1">
                <Input
                  value={editedAnswer}
                  onChange={(e) => setEditedAnswer(e.target.value)}
                  className="font-mono"
                />
                <Button size="sm" onClick={handleSave}>
                  <Save className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <div
                className="mt-1 p-2 bg-white rounded border cursor-pointer hover:bg-gray-50"
                onClick={() => setIsEditing(true)}
              >
                <MathText
                  text={task.studentAnswer || "—"}
                  className={!task.isCorrect ? "text-red-600" : ""}
                />
              </div>
            )}
          </div>

          <div>
            <Label className="text-sm text-muted-foreground flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3" />
              Teisingas atsakymas
            </Label>
            <div className="mt-1 p-2 bg-green-50 rounded border border-green-200">
              <MathText text={task.correctAnswer} className="text-green-700" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface ExplanationBoxProps {
  task: TaskResult;
  onRequestExplanation: (taskId: number) => void;
  isLoading?: boolean;
}

function ExplanationBox({
  task,
  onRequestExplanation,
  isLoading,
}: ExplanationBoxProps) {
  if (task.isCorrect) return null;

  return (
    <Card className="bg-blue-50/50 border-blue-200">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2 text-blue-700">
          <Lightbulb className="h-4 w-4" />
          AI paaiškinimas - Užduotis {task.number}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {task.explanation ? (
          <div className="space-y-3">
            <p className="text-sm text-gray-700">{task.explanation}</p>

            {task.suggestions && task.suggestions.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-blue-600 mb-2">
                  Patarimai:
                </p>
                <ul className="space-y-1">
                  {task.suggestions.map((suggestion, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-gray-600 flex items-start gap-2"
                    >
                      <span className="text-blue-500">•</span>
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onRequestExplanation(task.id)}
            disabled={isLoading}
            className="text-blue-600 border-blue-300 hover:bg-blue-100"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4 mr-2" />
            )}
            Gauti AI paaiškinimą
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

interface GradeEditorProps {
  grade: number;
  totalPoints: number;
  maxPoints: number;
  onGradeChange: (grade: number) => void;
}

function GradeEditor({
  grade,
  totalPoints,
  maxPoints,
  onGradeChange,
}: GradeEditorProps) {
  const percentage =
    maxPoints > 0 ? Math.round((totalPoints / maxPoints) * 100) : 0;

  const getGradeColor = (g: number) => {
    if (g >= 9) return "text-green-600 bg-green-100 border-green-300";
    if (g >= 7) return "text-blue-600 bg-blue-100 border-blue-300";
    if (g >= 5) return "text-amber-600 bg-amber-100 border-amber-300";
    return "text-red-600 bg-red-100 border-red-300";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Calculator className="h-5 w-5" />
          Vertinimas
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Taškai */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <span className="text-sm text-muted-foreground">Taškai</span>
          <span className="text-lg font-semibold">
            {totalPoints} / {maxPoints}
            <span className="text-sm text-muted-foreground ml-2">
              ({percentage}%)
            </span>
          </span>
        </div>

        {/* Pažymys */}
        <div className="space-y-2">
          <Label>Pažymys</Label>
          <div className="flex items-center gap-2">
            <Input
              type="number"
              min={1}
              max={10}
              value={grade}
              onChange={(e) => onGradeChange(Number(e.target.value))}
              className={`w-20 text-center text-2xl font-bold ${getGradeColor(
                grade
              )}`}
            />
            <span className="text-muted-foreground">/ 10</span>
          </div>
        </div>

        {/* Greitieji pažymiai */}
        <div className="flex flex-wrap gap-1">
          {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((g) => (
            <Button
              key={g}
              variant={grade === g ? "default" : "outline"}
              size="sm"
              onClick={() => onGradeChange(g)}
              className="w-9 h-9"
            >
              {g}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// === Main Component ===

export function ResultsPage() {
  const { submissionId } = useParams<{ submissionId: string }>();
  const navigate = useNavigate();

  // Demo duomenys (realiai būtų iš API)
  const [result, setResult] = useState<SubmissionResult>({
    id: 1,
    studentName: "Jonas Jonaitis",
    studentCode: "M2026001",
    className: "5a",
    testTitle: "Trupmenų sudėtis ir atimtis",
    testDate: "2026-01-10",
    variant: "I variantas",
    grade: 8,
    totalPoints: 16,
    maxPoints: 20,
    teacherComments: "",
    tasks: [
      {
        id: 1,
        number: 1,
        question: "Apskaičiuokite: $\\frac{2}{5} + \\frac{1}{3}$",
        studentAnswer: "\\frac{11}{15}",
        correctAnswer: "\\frac{11}{15}",
        isCorrect: true,
        points: 2,
        maxPoints: 2,
      },
      {
        id: 2,
        number: 2,
        question: "Apskaičiuokite: $\\frac{5}{6} - \\frac{1}{4}$",
        studentAnswer: "\\frac{7}{12}",
        correctAnswer: "\\frac{7}{12}",
        isCorrect: true,
        points: 2,
        maxPoints: 2,
      },
      {
        id: 3,
        number: 3,
        question: "Suprastinkite trupmeną: $\\frac{12}{18}$",
        studentAnswer: "\\frac{6}{9}",
        correctAnswer: "\\frac{2}{3}",
        isCorrect: false,
        points: 1,
        maxPoints: 2,
        explanation:
          "Mokinys pradėjo suprastinti trupmeną teisingai (padalino iš 2), bet nesuprastino iki galo. Trupmena 6/9 dar gali būti suprastinta padalinus skaitiklį ir vardiklį iš 3.",
        suggestions: [
          "Visada tikrink ar trupmeną dar galima suprastinti",
          "Ieškok didžiausio bendro daliklio (DBD)",
          "6 ir 9 abu dalijasi iš 3",
        ],
      },
      {
        id: 4,
        number: 4,
        question: "Išspręskite lygtį: $x + \\frac{1}{2} = \\frac{3}{4}$",
        studentAnswer: "\\frac{1}{4}",
        correctAnswer: "\\frac{1}{4}",
        isCorrect: true,
        points: 3,
        maxPoints: 3,
      },
      {
        id: 5,
        number: 5,
        question: "Apskaičiuokite: $2\\frac{1}{3} + 1\\frac{1}{2}$",
        studentAnswer: "3\\frac{2}{5}",
        correctAnswer: "3\\frac{5}{6}",
        isCorrect: false,
        points: 0,
        maxPoints: 3,
      },
    ],
  });

  const [comments, setComments] = useState(result.teacherComments || "");
  const [loadingExplanation, setLoadingExplanation] = useState<number | null>(
    null
  );
  const [showCommentTemplates, setShowCommentTemplates] = useState(false);
  const commentTemplates = getCommentTemplates();

  // Pritaikyti klaidos šabloną
  const handleApplyErrorTemplate = (
    taskId: number,
    template: ErrorTemplate
  ) => {
    setResult((prev) => ({
      ...prev,
      tasks: prev.tasks.map((t) =>
        t.id === taskId
          ? {
              ...t,
              explanation: template.explanation,
              points: Math.max(0, t.maxPoints - template.pointsDeduction),
            }
          : t
      ),
    }));
    // Perskaičiuoti bendrus taškus
    setResult((prev) => ({
      ...prev,
      totalPoints: prev.tasks.reduce((sum, t) => sum + t.points, 0),
    }));
  };

  // AI paaiškinimo užklausa
  const explainMutation = useMutation({
    mutationFn: async (taskId: number) => {
      const task = result.tasks.find((t) => t.id === taskId);
      if (!task) throw new Error("Užduotis nerasta");

      const response = await api.post("/math/explain-error", {
        task_text: task.question,
        student_answer: task.studentAnswer,
        correct_answer: task.correctAnswer,
        grade_level: 5,
      });
      return { taskId, data: response.data };
    },
    onSuccess: ({ taskId, data }) => {
      setResult((prev) => ({
        ...prev,
        tasks: prev.tasks.map((t) =>
          t.id === taskId
            ? {
                ...t,
                explanation: data.explanation,
                suggestions: data.suggestions,
              }
            : t
        ),
      }));
    },
  });

  const handleRequestExplanation = (taskId: number) => {
    setLoadingExplanation(taskId);
    explainMutation.mutate(taskId, {
      onSettled: () => setLoadingExplanation(null),
    });
  };

  const handleEditAnswer = (taskId: number, newAnswer: string) => {
    setResult((prev) => ({
      ...prev,
      tasks: prev.tasks.map((t) =>
        t.id === taskId ? { ...t, studentAnswer: newAnswer } : t
      ),
    }));
  };

  const handleGradeChange = (newGrade: number) => {
    setResult((prev) => ({
      ...prev,
      grade: Math.min(10, Math.max(1, newGrade)),
    }));
  };

  const handleExportPDF = async () => {
    try {
      const response = await api.post("/exports/student-report", {
        submission_id: Number(submissionId) || 1,
        include_explanations: true,
        teacher_comments: comments,
      });

      if (response.data.download_url) {
        window.open(
          `http://localhost:8000${response.data.download_url}`,
          "_blank"
        );
      }
    } catch (error) {
      console.error("PDF export failed:", error);
    }
  };

  const correctCount = result.tasks.filter((t) => t.isCorrect).length;
  const incorrectCount = result.tasks.length - correctCount;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{result.studentName}</h1>
            <p className="text-muted-foreground">
              {result.className} • {result.testTitle} • {result.variant}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleExportPDF}>
            <FileDown className="h-4 w-4 mr-2" />
            Eksportuoti PDF
          </Button>
          <Button>
            <Save className="h-4 w-4 mr-2" />
            Išsaugoti
          </Button>
        </div>
      </div>

      {/* Statistika */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {correctCount}
              </div>
              <div className="text-sm text-green-700">Teisingai</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">
                {incorrectCount}
              </div>
              <div className="text-sm text-red-700">Klaidų</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {result.totalPoints}/{result.maxPoints}
              </div>
              <div className="text-sm text-blue-700">Taškai</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {result.grade}
              </div>
              <div className="text-sm text-purple-700">Pažymys</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Užduotys */}
        <div className="col-span-2 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Užduotys ({result.tasks.length})
          </h2>

          {result.tasks.map((task) => (
            <div key={task.id} className="space-y-2">
              <SolutionDisplay
                task={task}
                onEdit={handleEditAnswer}
                onApplyErrorTemplate={handleApplyErrorTemplate}
              />
              <ExplanationBox
                task={task}
                onRequestExplanation={handleRequestExplanation}
                isLoading={loadingExplanation === task.id}
              />
            </div>
          ))}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <GradeEditor
            grade={result.grade}
            totalPoints={result.totalPoints}
            maxPoints={result.maxPoints}
            onGradeChange={handleGradeChange}
          />

          {/* Mokytojo komentarai */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Mokytojo komentarai
                </CardTitle>
                {/* Komentarų šablonai */}
                {commentTemplates.length > 0 && (
                  <div className="relative">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setShowCommentTemplates(!showCommentTemplates)
                      }
                    >
                      Šablonai
                      <ChevronDown className="h-3 w-3 ml-1" />
                    </Button>

                    {showCommentTemplates && (
                      <div className="absolute right-0 top-full mt-1 z-10 w-64 bg-white border rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
                        {commentTemplates.map((template) => (
                          <button
                            key={template.id}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex flex-col gap-0.5"
                            onClick={() => {
                              setComments((prev) =>
                                prev
                                  ? `${prev}\n\n${template.text}`
                                  : template.text
                              );
                              setShowCommentTemplates(false);
                            }}
                          >
                            <span className="font-medium">{template.name}</span>
                            <span className="text-xs text-muted-foreground line-clamp-2">
                              {template.text}
                            </span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Pridėkite komentarą mokiniui..."
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={4}
              />
            </CardContent>
          </Card>

          {/* Navigacija */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex justify-between">
                <Button variant="outline" size="sm">
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Ankstesnis
                </Button>
                <Button variant="outline" size="sm">
                  Kitas
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
