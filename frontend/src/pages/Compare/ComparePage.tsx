/**
 * ComparePage - OCR rezultatų palyginimas su originalu
 * Split view: kairėje originalus vaizdas, dešinėje OCR rezultatai
 */

import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/page-header";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ImageViewer } from "@/components/ui/ImageViewer";
import { MathRenderer, MathText } from "@/components/ui/MathRenderer";
import {
  ArrowLeft,
  Check,
  X,
  Edit3,
  RotateCcw,
  Save,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Move,
  Maximize2,
} from "lucide-react";

// Tipai
interface OcrResult {
  id: number;
  taskNumber: string;
  originalImage: string;
  recognizedText: string;
  recognizedLatex: string;
  confidence: number;
  status: "pending" | "verified" | "corrected" | "error";
}

interface SubmissionData {
  id: number;
  studentName: string;
  studentCode: string;
  testTitle: string;
  className: string;
  variantName: string;
  submittedAt: string;
  ocrResults: OcrResult[];
}

// Demo duomenys
const demoSubmission: SubmissionData = {
  id: 1,
  studentName: "Jonas Jonaitis",
  studentCode: "M2026001",
  testTitle: "Trupmenų sudėtis ir atimtis",
  className: "5a",
  variantName: "I variantas",
  submittedAt: "2026-01-10T14:30:00",
  ocrResults: [
    {
      id: 1,
      taskNumber: "1",
      originalImage: "/uploads/demo/task1.jpg",
      recognizedText: "2/5 + 1/3 = 6/15 + 5/15 = 11/15",
      recognizedLatex:
        "\\frac{2}{5} + \\frac{1}{3} = \\frac{6}{15} + \\frac{5}{15} = \\frac{11}{15}",
      confidence: 0.95,
      status: "verified",
    },
    {
      id: 2,
      taskNumber: "2",
      originalImage: "/uploads/demo/task2.jpg",
      recognizedText: "5/6 - 1/4 = 10/12 - 3/12 = 7/12",
      recognizedLatex:
        "\\frac{5}{6} - \\frac{1}{4} = \\frac{10}{12} - \\frac{3}{12} = \\frac{7}{12}",
      confidence: 0.88,
      status: "pending",
    },
    {
      id: 3,
      taskNumber: "3",
      originalImage: "/uploads/demo/task3.jpg",
      recognizedText: "12/18 = 6/9 = 2/3",
      recognizedLatex: "\\frac{12}{18} = \\frac{6}{9} = \\frac{2}{3}",
      confidence: 0.72,
      status: "pending",
    },
    {
      id: 4,
      taskNumber: "4",
      originalImage: "/uploads/demo/task4.jpg",
      recognizedText:
        "2 1/4 + 1 2/3 = 9/4 + 5/3 = 27/12 + 20/12 = 47/12 = 3 11/12",
      recognizedLatex:
        "2\\frac{1}{4} + 1\\frac{2}{3} = \\frac{9}{4} + \\frac{5}{3} = \\frac{27}{12} + \\frac{20}{12} = \\frac{47}{12} = 3\\frac{11}{12}",
      confidence: 0.65,
      status: "error",
    },
    {
      id: 5,
      taskNumber: "5",
      originalImage: "/uploads/demo/task5.jpg",
      recognizedText: "1 - 1/4 - 1/3 = 12/12 - 3/12 - 4/12 = 5/12",
      recognizedLatex:
        "1 - \\frac{1}{4} - \\frac{1}{3} = \\frac{12}{12} - \\frac{3}{12} - \\frac{4}{12} = \\frac{5}{12}",
      confidence: 0.91,
      status: "corrected",
    },
  ],
};

export function ComparePage() {
  const { submissionId } = useParams<{ submissionId: string }>();
  const navigate = useNavigate();

  const [submission, setSubmission] = useState<SubmissionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editedLatex, setEditedLatex] = useState("");
  const [splitRatio, setSplitRatio] = useState(50); // procentai kairiam panelui

  useEffect(() => {
    // Simuliuojame API užklausą
    const loadSubmission = async () => {
      setIsLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setSubmission(demoSubmission);
      setIsLoading(false);
    };
    loadSubmission();
  }, [submissionId]);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!submission) {
    return (
      <div className="flex-1 p-6">
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold">Pateikimas nerastas</h2>
          <Button className="mt-4" onClick={() => navigate(-1)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Grįžti atgal
          </Button>
        </div>
      </div>
    );
  }

  const currentTask = submission.ocrResults[currentTaskIndex];
  const totalTasks = submission.ocrResults.length;

  const handlePrevTask = () => {
    if (currentTaskIndex > 0) {
      setCurrentTaskIndex(currentTaskIndex - 1);
      setIsEditing(false);
    }
  };

  const handleNextTask = () => {
    if (currentTaskIndex < totalTasks - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
      setIsEditing(false);
    }
  };

  const handleVerify = () => {
    // TODO: API call to verify
    const updatedResults = [...submission.ocrResults];
    updatedResults[currentTaskIndex] = {
      ...currentTask,
      status: "verified",
    };
    setSubmission({ ...submission, ocrResults: updatedResults });
  };

  const handleStartEdit = () => {
    setEditedLatex(currentTask.recognizedLatex);
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    // TODO: API call to save
    const updatedResults = [...submission.ocrResults];
    updatedResults[currentTaskIndex] = {
      ...currentTask,
      recognizedLatex: editedLatex,
      status: "corrected",
    };
    setSubmission({ ...submission, ocrResults: updatedResults });
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedLatex("");
  };

  const getStatusBadge = (status: OcrResult["status"]) => {
    switch (status) {
      case "verified":
        return <Badge className="bg-green-500">Patvirtinta</Badge>;
      case "corrected":
        return <Badge className="bg-blue-500">Pataisyta</Badge>;
      case "error":
        return <Badge className="bg-red-500">Klaida</Badge>;
      default:
        return <Badge className="bg-yellow-500">Laukia</Badge>;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return "text-green-600";
    if (confidence >= 0.7) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Header */}
      <div className="border-b bg-background p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold">
                {submission.testTitle} - {submission.variantName}
              </h1>
              <p className="text-sm text-muted-foreground">
                {submission.studentName} ({submission.studentCode}) •{" "}
                {submission.className}
              </p>
            </div>
          </div>

          {/* Task navigation */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevTask}
              disabled={currentTaskIndex === 0}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm font-medium px-2">
              Užduotis {currentTaskIndex + 1} / {totalTasks}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextTask}
              disabled={currentTaskIndex === totalTasks - 1}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <>
                <Button variant="outline" size="sm" onClick={handleStartEdit}>
                  <Edit3 className="mr-2 h-4 w-4" />
                  Redaguoti
                </Button>
                <Button
                  size="sm"
                  onClick={handleVerify}
                  disabled={currentTask.status === "verified"}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Check className="mr-2 h-4 w-4" />
                  Patvirtinti
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" size="sm" onClick={handleCancelEdit}>
                  <X className="mr-2 h-4 w-4" />
                  Atšaukti
                </Button>
                <Button size="sm" onClick={handleSaveEdit}>
                  <Save className="mr-2 h-4 w-4" />
                  Išsaugoti
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Task tabs */}
      <div className="border-b bg-muted/30 px-4 py-2 flex gap-1 overflow-x-auto">
        {submission.ocrResults.map((result, index) => (
          <button
            key={result.id}
            onClick={() => {
              setCurrentTaskIndex(index);
              setIsEditing(false);
            }}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              index === currentTaskIndex
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            }`}
          >
            <span>{result.taskNumber}</span>
            {result.status === "verified" && (
              <Check className="h-3 w-3 text-green-400" />
            )}
            {result.status === "error" && (
              <X className="h-3 w-3 text-red-400" />
            )}
          </button>
        ))}
      </div>

      {/* Split view */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - Original image */}
        <div
          className="border-r bg-muted/20 flex flex-col"
          style={{ width: `${splitRatio}%` }}
        >
          <div className="p-2 border-b bg-background flex items-center justify-between">
            <span className="text-sm font-medium">Originalus vaizdas</span>
            <div className="flex items-center gap-1">
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="flex-1 overflow-auto p-4 flex items-center justify-center bg-slate-100">
            {/* Placeholder for image - in production use ImageViewer */}
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="w-64 h-48 bg-slate-200 rounded flex items-center justify-center mb-4">
                <span className="text-slate-500">
                  Užduotis {currentTask.taskNumber}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                Originalus mokinio atsakymas
              </p>
            </div>
          </div>
        </div>

        {/* Resize handle */}
        <div
          className="w-1 bg-border hover:bg-primary cursor-col-resize"
          onMouseDown={(e) => {
            const startX = e.clientX;
            const startRatio = splitRatio;

            const handleMouseMove = (e: MouseEvent) => {
              const container = (e.target as HTMLElement).parentElement;
              if (container) {
                const containerWidth = container.offsetWidth;
                const delta = e.clientX - startX;
                const newRatio = startRatio + (delta / containerWidth) * 100;
                setSplitRatio(Math.min(80, Math.max(20, newRatio)));
              }
            };

            const handleMouseUp = () => {
              document.removeEventListener("mousemove", handleMouseMove);
              document.removeEventListener("mouseup", handleMouseUp);
            };

            document.addEventListener("mousemove", handleMouseMove);
            document.addEventListener("mouseup", handleMouseUp);
          }}
        />

        {/* Right panel - OCR results */}
        <div className="flex-1 flex flex-col bg-background">
          <div className="p-2 border-b flex items-center justify-between">
            <span className="text-sm font-medium">OCR rezultatas</span>
            <div className="flex items-center gap-2">
              {getStatusBadge(currentTask.status)}
              <span
                className={`text-sm ${getConfidenceColor(
                  currentTask.confidence
                )}`}
              >
                {Math.round(currentTask.confidence * 100)}% tikslumas
              </span>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-6">
            {/* Recognized text */}
            <Card className="mb-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Atpažintas tekstas</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  {currentTask.recognizedText}
                </p>
              </CardContent>
            </Card>

            {/* LaTeX result */}
            <Card className="mb-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Matematinė formulė</CardTitle>
              </CardHeader>
              <CardContent>
                {isEditing ? (
                  <div className="space-y-4">
                    <textarea
                      value={editedLatex}
                      onChange={(e) => setEditedLatex(e.target.value)}
                      className="w-full h-32 p-3 border rounded-md font-mono text-sm"
                      placeholder="LaTeX formulė..."
                    />
                    <div className="p-4 bg-muted rounded-md">
                      <p className="text-xs text-muted-foreground mb-2">
                        Peržiūra:
                      </p>
                      <div className="text-xl">
                        <MathRenderer math={editedLatex} block />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-2xl py-4">
                    <MathRenderer math={currentTask.recognizedLatex} block />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Raw LaTeX */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">LaTeX kodas</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="p-3 bg-muted rounded-md text-sm font-mono overflow-x-auto">
                  {isEditing ? editedLatex : currentTask.recognizedLatex}
                </pre>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComparePage;
