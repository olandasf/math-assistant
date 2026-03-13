/**
 * CheckResultsModal - Tikrinimo rezultatų modalas
 * Rodo detalų tikrinimo rezultatų suvestinę su AI paaiškinimais
 */

import { useState } from "react";
import {
  X,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Save,
  Loader2,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Award,
  TrendingUp,
  FileText,
} from "lucide-react";
import { Button } from "./button";
import { Badge } from "./badge";
import { cn } from "@/lib/utils";
import { MathRenderer, MixedMathText } from "./MathRenderer";

// Tipai rezultatams
export interface TaskError {
  type:
    | "calculation"
    | "sign"
    | "incomplete"
    | "concept"
    | "notation"
    | "order"
    | "method";
  description: string;
  explanation?: string;
  correctApproach?: string;
}

export interface TaskResult {
  taskNumber: number;
  taskId?: string;
  studentAnswer: string;
  studentLatex: string;
  isCorrect: boolean;
  correctAnswer?: string;
  correctLatex?: string;
  points: number;
  maxPoints: number;
  errors?: TaskError[];
  suggestion?: string;
  confidence?: number;
  errorAnalysis?: {
    error_type?: string;
    error_location?: string;
    what_went_wrong?: string;
    why_wrong?: string;
    how_to_fix?: string;
  };
  solutionMethods?: Array<{
    method_name: string;
    steps: Array<{
      step_number: number;
      description: string;
      expression: string;
      result: string;
    }>;
    final_answer: string;
  }>;
}

interface CheckResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave?: (overrideGrade?: number, teacherNotes?: string) => void;
  isSaving?: boolean;
  studentName: string;
  testTitle: string;
  results: TaskResult[];
  totalPoints: number;
  maxPoints: number;
  grade: number;
  aiExplanation?: string;
}

// Demo duomenys testavimui
export const DEMO_CHECK_RESULTS: TaskResult[] = [
  {
    taskNumber: 1,
    taskId: "1a",
    studentAnswer: "54",
    studentLatex: "54",
    isCorrect: true,
    points: 2,
    maxPoints: 2,
  },
  {
    taskNumber: 2,
    taskId: "1b",
    studentAnswer: "18",
    studentLatex: "18",
    isCorrect: false,
    correctAnswer: "17",
    correctLatex: "17",
    points: 0,
    maxPoints: 2,
    errors: [
      {
        type: "calculation",
        description: "Skaičiavimo klaida",
        explanation: "Mokinys suklydo sudedant: 8 + 9 = 17, ne 18",
      },
    ],
  },
  {
    taskNumber: 3,
    taskId: "1c",
    studentAnswer: "300",
    studentLatex: "300",
    isCorrect: true,
    points: 2,
    maxPoints: 2,
  },
  {
    taskNumber: 4,
    taskId: "2a",
    studentAnswer: "-210",
    studentLatex: "-210",
    isCorrect: false,
    correctAnswer: "210",
    correctLatex: "210",
    points: 1,
    maxPoints: 2,
    errors: [
      {
        type: "sign",
        description: "Ženklo klaida",
        explanation: "Dviejų neigiamų skaičių sandauga yra teigiamas skaičius",
      },
    ],
  },
  {
    taskNumber: 5,
    taskId: "2b",
    studentAnswer: "",
    studentLatex: "",
    isCorrect: false,
    correctAnswer: "340",
    correctLatex: "340",
    points: 0,
    maxPoints: 2,
    errors: [
      {
        type: "incomplete",
        description: "Atsakymas nerastas",
        explanation: "Mokinys nepateikė atsakymo šiai užduočiai",
      },
    ],
  },
];

export function CheckResultsModal({
  isOpen,
  onClose,
  onSave,
  isSaving = false,
  studentName,
  testTitle,
  results,
  totalPoints,
  maxPoints,
  grade,
  aiExplanation,
}: CheckResultsModalProps) {
  const [expandedTasks, setExpandedTasks] = useState<Set<number>>(new Set());
  const [showAllDetails, setShowAllDetails] = useState(false);

  if (!isOpen) return null;

  const toggleTask = (taskNumber: number) => {
    const newExpanded = new Set(expandedTasks);
    if (newExpanded.has(taskNumber)) {
      newExpanded.delete(taskNumber);
    } else {
      newExpanded.add(taskNumber);
    }
    setExpandedTasks(newExpanded);
  };

  const toggleAllDetails = () => {
    if (showAllDetails) {
      setExpandedTasks(new Set());
    } else {
      setExpandedTasks(new Set(results.map((r) => r.taskNumber)));
    }
    setShowAllDetails(!showAllDetails);
  };

  const percentage =
    maxPoints > 0 ? Math.round((totalPoints / maxPoints) * 100) : 0;
  const correctCount = results.filter((r) => r.isCorrect).length;
  const incorrectCount = results.filter((r) => !r.isCorrect).length;

  // Pažymio spalva
  const gradeColor =
    grade >= 9
      ? "text-green-600 bg-green-100"
      : grade >= 7
        ? "text-blue-600 bg-blue-100"
        : grade >= 5
          ? "text-amber-600 bg-amber-100"
          : "text-red-600 bg-red-100";

  // Klaidos tipo ikona
  const getErrorIcon = (type: TaskError["type"]) => {
    switch (type) {
      case "calculation":
        return "🔢";
      case "sign":
        return "±";
      case "incomplete":
        return "⏳";
      case "concept":
        return "💡";
      case "notation":
        return "✏️";
      case "order":
        return "📊";
      default:
        return "❓";
    }
  };

  const handleSave = () => {
    if (onSave) {
      onSave(grade);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Tikrinimo rezultatai
            </h2>
            <p className="text-sm text-gray-600">
              {studentName} • {testTitle}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
          {/* Pažymys */}
          <div className="bg-white rounded-lg p-4 shadow-sm border text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Award className="h-5 w-5 text-amber-500" />
              <span className="text-sm text-gray-600">Pažymys</span>
            </div>
            <div
              className={cn("text-4xl font-bold rounded-lg py-2", gradeColor)}
            >
              {grade}
            </div>
          </div>

          {/* Taškai */}
          <div className="bg-white rounded-lg p-4 shadow-sm border text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <TrendingUp className="h-5 w-5 text-blue-500" />
              <span className="text-sm text-gray-600">Taškai</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {totalPoints} / {maxPoints}
            </div>
            <div className="text-sm text-gray-500">{percentage}%</div>
          </div>

          {/* Teisingi */}
          <div className="bg-white rounded-lg p-4 shadow-sm border text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-600">Teisingi</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {correctCount}
            </div>
            <div className="text-sm text-gray-500">iš {results.length}</div>
          </div>

          {/* Neteisingi */}
          <div className="bg-white rounded-lg p-4 shadow-sm border text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <XCircle className="h-5 w-5 text-red-500" />
              <span className="text-sm text-gray-600">Klaidos</span>
            </div>
            <div className="text-2xl font-bold text-red-600">
              {incorrectCount}
            </div>
            <div className="text-sm text-gray-500">užduotyse</div>
          </div>
        </div>

        {/* Results list */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Toggle all button */}
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-900">Užduočių rezultatai</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleAllDetails}
              className="text-sm"
            >
              {showAllDetails ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" />
                  Sutraukti visas
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" />
                  Išskleisti visas
                </>
              )}
            </Button>
          </div>

          {/* Task results */}
          <div className="space-y-3">
            {results.map((result) => (
              <div
                key={result.taskNumber}
                className={cn(
                  "border rounded-lg overflow-hidden transition-all",
                  result.isCorrect
                    ? "border-green-200 bg-green-50/50"
                    : "border-red-200 bg-red-50/50",
                )}
              >
                {/* Task header */}
                <button
                  onClick={() => toggleTask(result.taskNumber)}
                  className="w-full flex items-center justify-between p-4 hover:bg-white/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    {result.isCorrect ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                    <span className="font-medium">
                      {result.taskId || result.taskNumber} užduotis
                    </span>
                    {!result.isCorrect && result.errors && (
                      <Badge variant="secondary" className="ml-2">
                        {result.errors[0]?.type === "calculation" &&
                          "Skaičiavimo klaida"}
                        {result.errors[0]?.type === "sign" && "Ženklo klaida"}
                        {result.errors[0]?.type === "incomplete" &&
                          "Neatsakyta"}
                        {result.errors[0]?.type === "concept" &&
                          "Koncepcijos klaida"}
                        {result.errors[0]?.type === "notation" &&
                          "Užrašymo klaida"}
                        {result.errors[0]?.type === "order" && "Tvarkos klaida"}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">
                      {result.points} / {result.maxPoints} tšk.
                    </span>
                    {expandedTasks.has(result.taskNumber) ? (
                      <ChevronUp className="h-4 w-4 text-gray-500" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    )}
                  </div>
                </button>

                {/* Task details */}
                {expandedTasks.has(result.taskNumber) && (
                  <div className="px-4 pb-4 pt-2 border-t border-gray-100 bg-white/80">
                    <div className="grid grid-cols-2 gap-4 mb-3">
                      <div>
                        <div className="text-xs text-gray-500 mb-1">
                          Mokinio atsakymas
                        </div>
                        <div className="p-2 bg-gray-100 rounded font-mono text-sm">
                          {result.studentLatex ? (
                            <MathRenderer math={result.studentLatex} />
                          ) : (
                            <span className="text-gray-400 italic">
                              (nėra atsakymo)
                            </span>
                          )}
                        </div>
                      </div>
                      {!result.isCorrect && result.correctLatex && (
                        <div>
                          <div className="text-xs text-gray-500 mb-1">
                            Teisingas atsakymas
                          </div>
                          <div className="p-2 bg-green-100 rounded font-mono text-sm">
                            <MathRenderer math={result.correctLatex} />
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Errors */}
                    {result.errors && result.errors.length > 0 && (
                      <div className="space-y-2">
                        {result.errors.map((error, i) => (
                          <div
                            key={i}
                            className="p-3 bg-amber-50 border border-amber-200 rounded-lg"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <span>{getErrorIcon(error.type)}</span>
                              <span className="font-medium text-amber-800">
                                <MixedMathText text={error.description} />
                              </span>
                            </div>
                            {error.explanation && (
                              <div className="text-sm text-amber-700 ml-6">
                                <MixedMathText text={error.explanation} />
                              </div>
                            )}
                            {error.correctApproach && (
                              <div className="text-sm text-green-700 ml-6 mt-1">
                                💡{" "}
                                <MixedMathText text={error.correctApproach} />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Suggestion */}
                    {result.suggestion && (
                      <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center gap-2 mb-1">
                          <Sparkles className="h-4 w-4 text-blue-600" />
                          <span className="font-medium text-blue-800">
                            AI patarimas
                          </span>
                        </div>
                        <div className="text-sm text-blue-700 ml-6">
                          <MixedMathText text={result.suggestion} />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* AI Explanation */}
          {aiExplanation && (
            <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="h-5 w-5 text-purple-600" />
                <h4 className="font-semibold text-purple-900">
                  AI mokytojo komentaras
                </h4>
              </div>
              <div className="text-sm text-purple-800 whitespace-pre-wrap">
                {aiExplanation}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t bg-gray-50">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <FileText className="h-4 w-4" />
            <span>
              {results.length} užduotys • {totalPoints}/{maxPoints} taškų
            </span>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose}>
              Uždaryti
            </Button>
            {onSave && (
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saugoma...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Išsaugoti rezultatus
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CheckResultsModal;
