/**
 * ProcessingStatus - OCR apdorojimo būsenos komponentas
 * Rodo realų laiką progresą, žingsnius ir rezultatus
 */

import { useEffect, useState } from "react";
import {
  CheckCircle,
  AlertCircle,
  Loader2,
  Image as ImageIcon,
  FileText,
  Cpu,
  Sparkles,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui";

// Apdorojimo žingsniai
type ProcessingStep =
  | "upload"
  | "preprocess"
  | "ocr"
  | "math_check"
  | "complete";

interface StepInfo {
  id: ProcessingStep;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const PROCESSING_STEPS: StepInfo[] = [
  {
    id: "upload",
    label: "Įkėlimas",
    icon: <ImageIcon className="w-4 h-4" />,
    description: "Failas įkeliamas į sistemą",
  },
  {
    id: "preprocess",
    label: "Paruošimas",
    icon: <FileText className="w-4 h-4" />,
    description: "Vaizdo kokybės gerinimas",
  },
  {
    id: "ocr",
    label: "OCR",
    icon: <Cpu className="w-4 h-4" />,
    description: "Teksto ir formulių atpažinimas",
  },
  {
    id: "math_check",
    label: "Tikrinimas",
    icon: <Sparkles className="w-4 h-4" />,
    description: "Matematinis sprendimo tikrinimas",
  },
  {
    id: "complete",
    label: "Baigta",
    icon: <CheckCircle className="w-4 h-4" />,
    description: "Apdorojimas baigtas",
  },
];

interface ProcessingStatusProps {
  /** Dabartinis žingsnis */
  currentStep: ProcessingStep;
  /** Bendras progresas (0-100) */
  progress: number;
  /** Ar vyksta apdorojimas */
  isProcessing: boolean;
  /** Ar įvyko klaida */
  hasError?: boolean;
  /** Klaidos pranešimas */
  errorMessage?: string;
  /** Apdorojimo pradžios laikas */
  startTime?: Date;
  /** Papildoma informacija */
  details?: string;
  /** Papildoma CSS klasė */
  className?: string;
  /** Kompaktiškas režimas */
  compact?: boolean;
}

export function ProcessingStatus({
  currentStep,
  progress,
  isProcessing,
  hasError = false,
  errorMessage,
  startTime,
  details,
  className,
  compact = false,
}: ProcessingStatusProps) {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Atnaujinti praėjusį laiką
  useEffect(() => {
    if (!isProcessing || !startTime) {
      return;
    }

    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [isProcessing, startTime]);

  // Formatuoti laiką
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  // Gauti žingsnio statusą
  const getStepStatus = (stepId: ProcessingStep) => {
    const stepIndex = PROCESSING_STEPS.findIndex((s) => s.id === stepId);
    const currentIndex = PROCESSING_STEPS.findIndex(
      (s) => s.id === currentStep
    );

    if (hasError && stepId === currentStep) {
      return "error";
    }
    if (stepIndex < currentIndex) {
      return "completed";
    }
    if (stepIndex === currentIndex) {
      return isProcessing ? "active" : "completed";
    }
    return "pending";
  };

  // Kompaktiškas režimas
  if (compact) {
    return (
      <div className={cn("flex items-center gap-3", className)}>
        {hasError ? (
          <AlertCircle className="w-5 h-5 text-red-500" />
        ) : isProcessing ? (
          <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
        ) : (
          <CheckCircle className="w-5 h-5 text-green-500" />
        )}

        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">
            {hasError
              ? "Klaida"
              : PROCESSING_STEPS.find((s) => s.id === currentStep)?.label}
          </div>
          {isProcessing && <Progress value={progress} className="h-1 mt-1" />}
        </div>

        <div className="text-xs text-slate-500">
          {progress}%
          {startTime && isProcessing && (
            <span className="ml-2">
              <Clock className="w-3 h-3 inline mr-1" />
              {formatTime(elapsedTime)}
            </span>
          )}
        </div>
      </div>
    );
  }

  // Pilnas režimas
  return (
    <div
      className={cn(
        "p-4 border border-slate-200 rounded-lg bg-white",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-slate-900">
          {hasError ? (
            <span className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              Apdorojimo klaida
            </span>
          ) : isProcessing ? (
            <span className="flex items-center gap-2 text-blue-600">
              <Loader2 className="w-5 h-5 animate-spin" />
              Apdorojama...
            </span>
          ) : (
            <span className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              Apdorojimas baigtas
            </span>
          )}
        </h3>

        {startTime && (
          <div className="flex items-center gap-1 text-sm text-slate-500">
            <Clock className="w-4 h-4" />
            {formatTime(elapsedTime)}
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-slate-500 mb-1">
          <span>Progresas</span>
          <span>{progress}%</span>
        </div>
        <Progress
          value={progress}
          className={cn("h-2", hasError && "bg-red-100 [&>div]:bg-red-500")}
        />
      </div>

      {/* Žingsniai */}
      <div className="space-y-2">
        {PROCESSING_STEPS.map((step, index) => {
          const status = getStepStatus(step.id);

          return (
            <div
              key={step.id}
              className={cn(
                "flex items-center gap-3 p-2 rounded-lg transition-colors",
                status === "active" && "bg-blue-50",
                status === "error" && "bg-red-50",
                status === "completed" && "bg-green-50/50"
              )}
            >
              {/* Ikona */}
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center",
                  status === "pending" && "bg-slate-100 text-slate-400",
                  status === "active" && "bg-blue-500 text-white",
                  status === "completed" && "bg-green-500 text-white",
                  status === "error" && "bg-red-500 text-white"
                )}
              >
                {status === "active" && isProcessing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : status === "completed" ? (
                  <CheckCircle className="w-4 h-4" />
                ) : status === "error" ? (
                  <AlertCircle className="w-4 h-4" />
                ) : (
                  step.icon
                )}
              </div>

              {/* Tekstas */}
              <div className="flex-1">
                <div
                  className={cn(
                    "text-sm font-medium",
                    status === "pending" && "text-slate-400",
                    status === "active" && "text-blue-700",
                    status === "completed" && "text-green-700",
                    status === "error" && "text-red-700"
                  )}
                >
                  {step.label}
                </div>
                <div className="text-xs text-slate-500">{step.description}</div>
              </div>

              {/* Status badge */}
              <div
                className={cn(
                  "text-xs px-2 py-0.5 rounded-full",
                  status === "pending" && "bg-slate-100 text-slate-500",
                  status === "active" && "bg-blue-100 text-blue-700",
                  status === "completed" && "bg-green-100 text-green-700",
                  status === "error" && "bg-red-100 text-red-700"
                )}
              >
                {status === "pending" && "Laukia"}
                {status === "active" && "Vykdoma"}
                {status === "completed" && "Atlikta"}
                {status === "error" && "Klaida"}
              </div>
            </div>
          );
        })}
      </div>

      {/* Klaidos pranešimas */}
      {hasError && errorMessage && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {errorMessage}
        </div>
      )}

      {/* Papildoma informacija */}
      {details && (
        <div className="mt-4 p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-600">
          {details}
        </div>
      )}
    </div>
  );
}

/**
 * Batch apdorojimo būsena keliems failams
 */
interface BatchProcessingStatusProps {
  files: Array<{
    id: string;
    name: string;
    currentStep: ProcessingStep;
    progress: number;
    hasError?: boolean;
  }>;
  className?: string;
}

export function BatchProcessingStatus({
  files,
  className,
}: BatchProcessingStatusProps) {
  const totalProgress =
    files.length > 0
      ? Math.round(files.reduce((acc, f) => acc + f.progress, 0) / files.length)
      : 0;

  const completed = files.filter(
    (f) => f.currentStep === "complete" && !f.hasError
  ).length;
  const errors = files.filter((f) => f.hasError).length;
  const processing = files.filter(
    (f) => f.currentStep !== "complete" && !f.hasError
  ).length;

  return (
    <div
      className={cn(
        "p-4 border border-slate-200 rounded-lg bg-white",
        className
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-slate-900">Batch apdorojimas</h3>
        <div className="text-sm text-slate-500">
          {completed}/{files.length} baigta
        </div>
      </div>

      <Progress value={totalProgress} className="h-2 mb-3" />

      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-1">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span className="text-green-700">{completed} baigta</span>
        </div>
        {processing > 0 && (
          <div className="flex items-center gap-1">
            <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
            <span className="text-blue-700">{processing} vykdoma</span>
          </div>
        )}
        {errors > 0 && (
          <div className="flex items-center gap-1">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span className="text-red-700">{errors} klaidos</span>
          </div>
        )}
      </div>

      {/* Failų sąrašas */}
      <div className="mt-3 space-y-1 max-h-40 overflow-y-auto">
        {files.map((file) => (
          <div
            key={file.id}
            className="flex items-center gap-2 text-sm p-1.5 rounded hover:bg-slate-50"
          >
            {file.hasError ? (
              <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
            ) : file.currentStep === "complete" ? (
              <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
            ) : (
              <Loader2 className="w-4 h-4 text-blue-500 animate-spin shrink-0" />
            )}
            <span className="truncate flex-1">{file.name}</span>
            <span className="text-slate-400">{file.progress}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProcessingStatus;
