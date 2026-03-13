/**
 * WorkReviewPage - Konkretaus įkelto darbo peržiūra ir redagavimas
 * Kairėje: originalus vaizdas su zoom/rotate/pan
 * Dešinėje: LaTeX redaktorius su atpažintu tekstu
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  Save,
  Check,
  X,
  Edit3,
  ChevronLeft,
  ChevronRight,
  Undo2,
  Redo2,
  Eye,
  EyeOff,
  Type,
  ZoomIn,
  ZoomOut,
  RotateCw,
  RotateCcw,
  Maximize2,
  RefreshCw,
  Send,
  Loader2,
  CheckCircle,
} from "lucide-react";
import { Button, Badge, PageHeader } from "@/components/ui";
import { ImageViewer } from "@/components/ui/ImageViewer";
import { MathRenderer } from "@/components/ui/MathRenderer";
import { MathEditor } from "@/components/ui/MathEditor";
import {
  CheckResultsModal,
  DEMO_CHECK_RESULTS,
} from "@/components/ui/CheckResultsModal";
import { useUploadStore } from "@/stores";
import {
  useCheckFullWork,
  useAutoCheck,
  useTasks,
  useVariants,
  useSaveCheckResults,
} from "@/api/hooks";
import type {
  TaskDefinition,
  AnswerCreate,
  AutoCheckResponse,
} from "@/api/hooks";
import { cn } from "@/lib/utils";

// Demo vaizdas - placeholder (naudojamas tik kai nėra realaus vaizdo)
const DEMO_IMAGE =
  "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjgwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PGxpbmUgeDE9IjAiIHkxPSIwIiB4Mj0iNjAwIiB5Mj0iMCIgc3Ryb2tlPSIjZTBlMGUwIiBzdHJva2Utd2lkdGg9IjEiLz48dGV4dCB4PSIzMDAiIHk9IjQwMCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjI0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5Nb2tpbmlvIGRhcmJhczwvdGV4dD48L3N2Zz4=";

// Helper funkcija dublikatų pašalinimui iš LaTeX
function removeDuplicateLatexLines(latex: string): string {
  if (!latex) return latex;

  // Jei yra §§§ separatorius - naudojame jį
  if (latex.includes("§§§")) {
    const lines = latex.split("§§§").filter((line) => line.trim() !== "");
    const seenIds = new Set<string>();
    const uniqueLines: string[] = [];

    for (const line of lines) {
      const trimmed = line.trim();
      // Ištraukiame task ID (pvz. "1a", "1b", "2a")
      const match = trimmed.match(/^(\d+[a-z]?)\)/i);
      if (match) {
        const taskId = match[1].toLowerCase();
        if (!seenIds.has(taskId)) {
          seenIds.add(taskId);
          uniqueLines.push(trimmed);
        } else {
          console.log(`[LaTeX] Pašalintas dublikatas: ${taskId}`);
        }
      } else {
        uniqueLines.push(trimmed);
      }
    }

    console.log(
      `[LaTeX] §§§ dublikatai: ${lines.length} -> ${uniqueLines.length}`,
    );
    return uniqueLines.join("§§§");
  }

  // Jei nėra separatoriaus - bandome pašalinti inline dublikatus
  // Ieškome pattern: "1a)...1a)..." ir pašaliname antrą
  let result = latex;
  const taskPattern = /(\d+[a-z]?)\)/gi;
  const matches = [...latex.matchAll(taskPattern)];

  // Grupuojame pagal task ID
  const taskGroups = new Map<string, number[]>();
  for (const match of matches) {
    const taskId = match[1].toLowerCase();
    if (!taskGroups.has(taskId)) {
      taskGroups.set(taskId, []);
    }
    taskGroups.get(taskId)!.push(match.index!);
  }

  // Randame dublikatus ir pašaliname
  const toRemove: { start: number; end: number }[] = [];

  for (const [taskId, positions] of taskGroups) {
    if (positions.length > 1) {
      console.log(
        `[LaTeX] Inline dublikatas: ${taskId}) (${positions.length}x)`,
      );

      // Pašaliname visus išskyrus pirmą
      for (let i = 1; i < positions.length; i++) {
        const start = positions[i];
        // Pabaiga - kitas uždavinys arba string pabaiga
        let end = latex.length;

        // Ieškome kito uždavinio
        for (const [otherId, otherPositions] of taskGroups) {
          for (const pos of otherPositions) {
            if (pos > start && pos < end) {
              end = pos;
            }
          }
        }

        toRemove.push({ start, end });
      }
    }
  }

  // Pašaliname nuo galo
  toRemove.sort((a, b) => b.start - a.start);
  for (const { start, end } of toRemove) {
    result = result.slice(0, start) + result.slice(end);
  }

  if (toRemove.length > 0) {
    console.log(`[LaTeX] Pašalinta ${toRemove.length} inline dublikatų`);
  }

  return result;
}

export default function WorkReviewPage() {
  const { fileId } = useParams<{ fileId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Store
  const { files: storeFiles } = useUploadStore();

  // Ref to track if OCR has been called (prevents double calls)
  const ocrCalledRef = useRef<string | null>(null);

  // Find current file in store
  const currentFile = storeFiles.find(
    (f) => f.fileId === fileId || f.id === fileId,
  );

  // API hooks for real checking
  const checkFullWork = useCheckFullWork();
  const autoCheck = useAutoCheck();
  const saveCheckResults = useSaveCheckResults();
  const { data: variants } = useVariants(currentFile?.testId || 0);
  // Get first variant's tasks (for now - TODO: let user select variant)
  const firstVariantId = variants?.[0]?.id || 0;
  const { data: tasks } = useTasks(currentFile?.testId || 0, firstVariantId);

  // State
  const [status, setStatus] = useState<
    "pending" | "processing" | "completed" | "verified" | "checking"
  >("completed");
  const [currentTask, setCurrentTask] = useState(1);
  const [totalTasks, setTotalTasks] = useState(5);
  const [isEditing, setIsEditing] = useState(false);
  const [showPreview, setShowPreview] = useState(true);
  const [showLatexCode, setShowLatexCode] = useState(false);

  // Check results state
  const [isChecking, setIsChecking] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [checkResults, setCheckResults] = useState<typeof DEMO_CHECK_RESULTS>(
    [],
  );
  const [isSaving, setIsSaving] = useState(false);
  const [apiCheckResults, setApiCheckResults] = useState<
    typeof checkFullWork.data | null
  >(null);

  // Image state
  const [imageUrl, setImageUrl] = useState<string>(DEMO_IMAGE);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // OCR content - pradžioje tušti, užpildomi iš OCR
  const [recognizedText, setRecognizedText] = useState("");
  const [latexContent, setLatexContent] = useState("");
  const [editedLatex, setEditedLatex] = useState("");
  const [confidence, setConfidence] = useState(0);

  // Undo/Redo history
  const [history, setHistory] = useState<string[]>([""]);
  const [historyIndex, setHistoryIndex] = useState(0);

  // Split ratio
  const [splitRatio, setSplitRatio] = useState(50);

  // Update image when page changes
  useEffect(() => {
    if (currentFile?.fileId) {
      const imgUrl = `/api/v1/upload/${currentFile.fileId}/page/${currentPage}`;
      setImageUrl(imgUrl);
    }
  }, [currentPage, currentFile?.fileId]);

  // Page navigation handlers
  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // Load file data and perform OCR if needed
  useEffect(() => {
    // Naudojame ref kad išvengtume dvigubo OCR kvietimo
    let isCancelled = false;

    const loadFileData = async () => {
      if (!fileId) return;

      // Find file in store
      const storeFile = storeFiles.find(
        (f) => f.fileId === fileId || f.id === fileId,
      );

      console.log("[DEBUG] WorkReviewPage loadFileData:", {
        fileId,
        storeFile,
        storeFilesCount: storeFiles.length,
        allFileIds: storeFiles.map((f) => ({ id: f.id, fileId: f.fileId })),
      });

      if (storeFile) {
        // Use real file data - pirma gauname failo info kad žinotume puslapių skaičių
        if (storeFile.fileId) {
          // Gauname failo informaciją
          try {
            const fileInfoResponse = await fetch(
              `/api/v1/upload/${storeFile.fileId}`,
            );
            if (fileInfoResponse.ok) {
              const fileInfo = await fileInfoResponse.json();
              if (!isCancelled) {
                setTotalPages(fileInfo.pages || 1);
              }
              console.log(
                "[DEBUG] File info:",
                fileInfo,
                "pages:",
                fileInfo.pages,
              );
            }
          } catch (e) {
            console.error("[ERROR] Failed to get file info:", e);
          }

          if (!isCancelled) {
            const imgUrl = `/api/v1/upload/${storeFile.fileId}/page/${currentPage}`;
            console.log("[DEBUG] Setting imageUrl:", imgUrl);
            setImageUrl(imgUrl);
          }
        }

        // Tikriname ar cache turi pakankamai užduočių (jei failas turi >1 puslapį)
        const cachedSeparatorCount =
          (storeFile.ocrResult?.latex?.split("§§§").length ?? 1) - 1;
        const filePages = totalPages || storeFile.pages || 1;
        const expectedMinTasks = filePages > 1 ? 15 : 5; // 2 puslapiai = bent 15 užduočių
        const cacheHasEnoughTasks =
          cachedSeparatorCount >= expectedMinTasks - 1;

        console.log("[DEBUG] Cache check:", {
          cachedTasks: cachedSeparatorCount + 1,
          expectedMinTasks,
          filePages,
          cacheHasEnoughTasks,
          ocrCalledRef: ocrCalledRef.current,
        });

        // VISADA paleidžiame OCR all-pages kai:
        // 1. Dar nekviečiame šiam failui, ARBA
        // 2. Cache neturi pakankamai užduočių (multi-page failas)
        const shouldCallOCR =
          storeFile.fileId &&
          (ocrCalledRef.current !== storeFile.fileId || !cacheHasEnoughTasks);

        if (shouldCallOCR) {
          ocrCalledRef.current = storeFile.fileId ?? null; // Mark as called
          if (!isCancelled) {
            setStatus("processing");
          }
          try {
            console.log(
              "[DEBUG] Calling OCR all-pages for:",
              storeFile.fileId,
              {
                reason:
                  ocrCalledRef.current !== storeFile.fileId
                    ? "first call"
                    : "cache insufficient",
              },
            );
            const response = await fetch(`/api/v1/upload/ocr/all-pages`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                file_id: storeFile.fileId,
                detect_math: true,
              }),
            });

            if (isCancelled) return;

            if (response.ok) {
              const ocrData = await response.json();
              console.log("[DEBUG] OCR response:", {
                hasLatex: !!ocrData.latex,
                latexLength: ocrData.latex?.length,
                hasSeparator: ocrData.latex?.includes("§§§"),
                separatorCount: ocrData.latex?.split("§§§").length - 1,
              });
              setRecognizedText(ocrData.text || "");
              // Jei nėra LaTeX, naudojame paprastą tekstą
              const latexOrText = ocrData.latex || ocrData.text || "";
              // Pašaliname dublikatus
              const cleanLatex = removeDuplicateLatexLines(latexOrText);
              console.log("[DEBUG] Clean LaTeX:", {
                originalLength: latexOrText.length,
                cleanLength: cleanLatex.length,
                separatorCount: cleanLatex.split("§§§").length - 1,
                first200: cleanLatex.substring(0, 200),
              });
              setLatexContent(cleanLatex);
              setEditedLatex(cleanLatex);
              setConfidence(ocrData.confidence || 0);
              setHistory([cleanLatex]);
              setHistoryIndex(0);
              setStatus("completed");
              console.log(
                "[INFO] OCR atliktas WorkReviewPage (visi puslapiai):",
                storeFile.fileId,
                {
                  hasLatex: !!ocrData.latex,
                  textLength: ocrData.text?.length,
                  pages: ocrData.pages,
                  separatorCount: cleanLatex.split("§§§").length - 1,
                },
              );
            } else {
              console.error("[ERROR] OCR nepavyko:", response.status);
              // Fallback į cache jei OCR nepavyko
              if (storeFile.ocrResult) {
                setRecognizedText(storeFile.ocrResult.text);
                const latexOrText =
                  storeFile.ocrResult.latex || storeFile.ocrResult.text || "";
                const cleanLatex = removeDuplicateLatexLines(latexOrText);
                setLatexContent(cleanLatex);
                setEditedLatex(cleanLatex);
                setConfidence(storeFile.ocrResult.confidence);
              }
              setStatus("completed");
            }
          } catch (error) {
            if (isCancelled) return;
            console.error("[ERROR] OCR klaida:", error);
            // Fallback į cache jei OCR nepavyko
            if (storeFile.ocrResult) {
              setRecognizedText(storeFile.ocrResult.text);
              const latexOrText =
                storeFile.ocrResult.latex || storeFile.ocrResult.text || "";
              const cleanLatex = removeDuplicateLatexLines(latexOrText);
              setLatexContent(cleanLatex);
              setEditedLatex(cleanLatex);
              setConfidence(storeFile.ocrResult.confidence);
            }
            setStatus("completed");
          }
        } else if (storeFile.ocrResult && cacheHasEnoughTasks) {
          // Cache turi pakankamai užduočių - naudojame jį
          console.log(
            "[DEBUG] Using cached ocrResult (has enough tasks):",
            cachedSeparatorCount + 1,
          );
          setRecognizedText(storeFile.ocrResult.text);
          const latexOrText =
            storeFile.ocrResult.latex || storeFile.ocrResult.text || "";
          const cleanLatex = removeDuplicateLatexLines(latexOrText);
          setLatexContent(cleanLatex);
          setEditedLatex(cleanLatex);
          setConfidence(storeFile.ocrResult.confidence);
          setStatus("completed");
        } else {
          console.log("[WARN] No fileId and no sufficient ocrResult");
          setStatus("completed");
        }
      } else {
        // Failas nerastas store - gal tiesioginis URL?
        console.log("[WARN] Failas nerastas store:", fileId);
      }
    };

    loadFileData();

    // Cleanup funkcija - atšaukia OCR jei komponentas unmount'inamas
    return () => {
      isCancelled = true;
    };
  }, [fileId]); // Pašalinome storeFiles iš priklausomybių kad išvengtume dvigubo OCR

  // Handle zoom
  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 25, 400));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 25, 25));
  const handleRotateCW = () => setRotation((prev) => (prev + 90) % 360);
  const handleRotateCCW = () => setRotation((prev) => (prev - 90 + 360) % 360);
  const handleReset = () => {
    setZoom(100);
    setRotation(0);
  };

  // Edit handlers
  const handleStartEdit = () => {
    setEditedLatex(latexContent);
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    // Save to history
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(editedLatex);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);

    setLatexContent(editedLatex);
    setIsEditing(false);
    setStatus("verified");
  };

  const handleCancelEdit = () => {
    setEditedLatex(latexContent);
    setIsEditing(false);
  };

  // Submit for checking - NAUDOJA PATAISYTĄ latexContent!
  const handleSubmitForCheck = async () => {
    // Apsauga: neleisti tikrinti kol OCR vyksta
    if (status === "processing") {
      alert("Palaukite kol OCR baigs apdoroti visus puslapius.");
      return;
    }

    // Apsauga: patikrinti ar LaTeX turi pakankamai uždavinių (jei PDF turi >1 puslapį)
    const currentLatex = latexContent || recognizedText;
    const separatorCount = currentLatex
      ? currentLatex.split("§§§").length - 1
      : 0;

    // Jei PDF turi 2 puslapius, tikimės bent 15+ uždavinių (separator_count >= 14)
    // Jei matome tik ~12, vadinasi antras puslapis dar nebuvo apdorotas
    if (totalPages > 1 && separatorCount < 14) {
      alert(
        `⚠️ OCR dar nebaigė apdoroti visų puslapių!\n\n` +
          `Aptikta tik ${
            separatorCount + 1
          } uždavinių, bet PDF turi ${totalPages} puslapius.\n\n` +
          `Palaukite kol statusas pasikeis į "Apdorota" ir bandykite dar kartą.`,
      );
      return; // Neleidžiame tęsti
    }

    setIsChecking(true);
    setStatus("checking");

    try {
      if (!currentLatex || currentLatex.trim().length === 0) {
        alert(
          "Nėra teksto tikrinimui. Pirmiausia įkelkite ir atpažinkite darbą.",
        );
        setIsChecking(false);
        setStatus("completed");
        return;
      }

      // DEBUG: Išsamūs logai
      console.log("[DEBUG] handleSubmitForCheck - LaTeX info:", {
        length: currentLatex.length,
        separatorCount: separatorCount,
        expectedTasks: separatorCount + 1,
        first200: currentLatex.substring(0, 200),
        last200: currentLatex.substring(currentLatex.length - 200),
      });

      console.log(
        "[DEBUG] Siunčiamas tikrinimui LaTeX:",
        currentLatex.substring(0, 200) + "...",
      );

      // Jei turime realias užduotis iš DB - naudojame API
      if (tasks && tasks.length > 0) {
        console.log(
          "[INFO] Naudojamas realus API tikrinimas su",
          tasks.length,
          "užduotimis",
        );

        const taskDefinitions: TaskDefinition[] = tasks.map((t) => ({
          task_number: t.number,
          expected_answer: t.correct_answer,
          max_points: t.points,
          task_type: "arithmetic",
        }));

        const response = await checkFullWork.mutateAsync({
          latex_content: currentLatex,
          tasks: taskDefinitions,
          grade_level: 6,
        });

        // Konvertuojame backend rezultatus į frontend formatą
        const convertedResults = response.task_results.map((r, idx) => {
          // Mapuojame backend error types į frontend types
          const mapErrorType = (
            backendType?: string,
          ): "calculation" | "method" | "notation" | "incomplete" => {
            switch (backendType) {
              case "missing":
                return "incomplete";
              case "calculation":
                return "calculation";
              case "method":
                return "method";
              case "format":
                return "notation";
              case "decimal":
                return "calculation";
              case "digit_swap":
                return "calculation";
              case "system":
                return "calculation";
              default:
                return "calculation";
            }
          };

          return {
            taskNumber: idx + 1,
            studentAnswer: r.student_answer || "",
            studentLatex: r.student_answer || "",
            isCorrect: r.is_correct,
            correctAnswer: r.is_correct ? undefined : r.expected_answer,
            correctLatex: r.is_correct ? undefined : r.expected_answer,
            points: r.points_earned,
            maxPoints: r.max_points,
            errors: r.is_correct
              ? undefined
              : [
                  {
                    type: mapErrorType(r.error_type),
                    description: r.error_description || "Klaida",
                    explanation: r.suggestion || "",
                  },
                ],
          };
        });

        setCheckResults(convertedResults);
        setApiCheckResults(response);
        setShowResults(true);
        setStatus("verified");
        return;
      }

      // Jei nėra užduočių DB - naudojame AUTOMATINĮ tikrinimą (AI/SymPy)
      console.log(
        "[INFO] Nėra užduočių DB - naudojamas automatinis AI tikrinimas",
      );

      const autoResponse = await autoCheck.mutateAsync({
        latex_content: currentLatex,
        grade_level: 6,
        check_calculations: true,
      });

      console.log("[DEBUG] Auto check response:", autoResponse);
      // DEBUG: Log confidence values
      console.log(
        "[DEBUG] Confidence values:",
        autoResponse.task_results.map((r) => ({
          task_id: r.task_id,
          confidence: r.confidence,
        })),
      );

      // Konvertuojame auto check rezultatus į frontend formatą
      const autoResults = autoResponse.task_results.map((r, idx) => {
        // Konvertuojame error_analysis
        const errorAnalysis = r.error_analysis
          ? {
              error_type: r.error_analysis.error_type,
              error_location: r.error_analysis.error_location,
              what_went_wrong: r.error_analysis.what_went_wrong,
              why_wrong: r.error_analysis.why_wrong,
              how_to_fix: r.error_analysis.how_to_fix,
            }
          : undefined;

        // Konvertuojame solution_methods - VISADA (ir teisingų, ir neteisingų atsakymų atveju)
        const solutionMethods =
          r.solution_methods?.map((method) => ({
            method_name: method.method_name,
            steps: method.steps.map((step) => ({
              step_number: step.step_number,
              description: step.description,
              expression: step.expression,
              result: step.result ?? "",
            })),
            final_answer: method.final_answer,
          })) || [];

        // Skaičiuojame taškus - 2 taškai už teisingą, 0 už neteisingą
        const maxPts = 2;
        const earnedPts = r.is_correct === true ? maxPts : 0;

        return {
          taskNumber: idx + 1,
          taskId: r.task_id || `${idx + 1}`,
          studentAnswer: r.student_answer || "",
          studentLatex: r.student_solution || "",
          isCorrect: r.is_correct ?? false,
          correctAnswer: r.calculated_answer || undefined,
          correctLatex: r.calculated_answer || undefined,
          points: earnedPts,
          maxPoints: maxPts,
          confidence: r.confidence, // OCR pasitikėjimo lygis
          suggestion: r.suggestion || undefined, // AI paaiškinimas
          errors:
            r.is_correct === false
              ? [
                  {
                    type: "calculation" as const,
                    description: r.error_description || "Skaičiavimo klaida",
                    explanation: r.suggestion || "",
                  },
                ]
              : r.is_correct === null
                ? [
                    {
                      type: "incomplete" as const,
                      description: "Nepavyko patikrinti",
                      explanation:
                        r.suggestion ||
                        "Sistema negalėjo automatiškai patikrinti šio atsakymo",
                    },
                  ]
                : undefined,
          // Nauji laukai - VISADA pridedame sprendimo būdus
          errorAnalysis,
          solutionMethods,
        };
      });

      setCheckResults(autoResults);
      setShowResults(true);
      setStatus("verified");
      return;
    } catch (error) {
      console.error("Tikrinimo klaida:", error);
      alert("Tikrinimo klaida. Bandykite dar kartą.");
    } finally {
      setIsChecking(false);
    }
  };

  // Save check results to database
  const handleSaveResults = async (
    overrideGrade?: number,
    teacherNotes?: string,
  ) => {
    if (!currentFile?.studentId || !currentFile?.testId) {
      console.error(
        "[ERROR] Nėra student_id arba test_id - negalima išsaugoti",
      );
      alert("Pasirinkite mokinį ir kontrolinį prieš saugant rezultatus");
      return;
    }

    if (!tasks || tasks.length === 0) {
      console.log("[INFO] Nėra užduočių DB - demo režimas, saugoma nebus");
      setShowResults(false);
      navigate("/upload");
      return;
    }

    setIsSaving(true);

    try {
      // Sukuriame answers masyv from checkResults ir tasks
      const answers: AnswerCreate[] = checkResults
        .map((result, idx) => {
          const task = tasks[idx];
          return {
            task_id: task?.id || 0,
            recognized_text: result.studentAnswer,
            recognized_latex: result.studentLatex,
            is_correct: result.isCorrect,
            earned_points: result.points,
            max_points: result.maxPoints,
            ai_explanation: result.errors?.[0]?.explanation,
          };
        })
        .filter((a) => a.task_id > 0);

      const response = await saveCheckResults.mutateAsync({
        student_id: currentFile.studentId,
        test_id: currentFile.testId,
        variant_id: firstVariantId || undefined,
        file_path: currentFile.fileId || "",
        file_name: currentFile.fileName,
        latex_content: latexContent,
        answers,
        total_points: checkResults.reduce((sum, r) => sum + r.points, 0),
        max_points: checkResults.reduce((sum, r) => sum + r.maxPoints, 0),
      });

      // Jei yra override grade - atnaujiname atskirai
      if (overrideGrade && response?.id) {
        // Import useUpdateGrade arba call API directly
        console.log(
          "[INFO] Override grade:",
          overrideGrade,
          "notes:",
          teacherNotes,
        );
        // TODO: call update grade API if needed
      }

      console.log("[SUCCESS] Rezultatai išsaugoti į duomenų bazę");
      setShowResults(false);
      navigate("/rezultatai");
    } catch (error) {
      console.error("[ERROR] Nepavyko išsaugoti rezultatų:", error);
      alert("Klaida saugant rezultatus. Bandykite dar kartą.");
    } finally {
      setIsSaving(false);
    }
  };

  // Laikina funkcija - parsinamas LaTeX ir generuojami TaskResult[] masyvas
  const parseLatexAndGenerateResults = (
    latex: string,
  ): typeof DEMO_CHECK_RESULTS => {
    // Teisingi atsakymai (iš kontrolinio)
    const correctAnswers: Array<{
      num: number;
      id: string;
      answer: string;
      points: number;
    }> = [
      { num: 1, id: "1a", answer: "54", points: 2 },
      { num: 2, id: "1b", answer: "17", points: 2 },
      { num: 3, id: "1c", answer: "300", points: 2 },
      { num: 4, id: "2a", answer: "210", points: 2 },
      { num: 5, id: "2b", answer: "340", points: 2 },
    ];

    const results: typeof DEMO_CHECK_RESULTS = [];

    for (const task of correctAnswers) {
      // Ieškome mokinio atsakymo LaTeX
      const studentAnswer = extractAnswerFromLatex(latex, task.id);

      if (!studentAnswer) {
        results.push({
          taskNumber: task.num,
          studentAnswer: "",
          studentLatex: "",
          isCorrect: false,
          correctAnswer: task.answer,
          correctLatex: task.answer,
          points: 0,
          maxPoints: task.points,
          errors: [
            {
              type: "incomplete" as const,
              description: "Atsakymas nerastas",
              explanation: "Mokinys nepateikė atsakymo šiai užduočiai.",
            },
          ],
        });
        continue;
      }

      // Tikriname ar atsakymas teisingas
      const isCorrect =
        normalizeNumber(studentAnswer) === normalizeNumber(task.answer);
      const pointsEarned = isCorrect ? task.points : 0;

      const errors = isCorrect
        ? undefined
        : [
            {
              type: "calculation" as const,
              description: `Neteisingai apskaičiuota: ${studentAnswer} ≠ ${task.answer}`,
              explanation: `Teisingas atsakymas yra ${task.answer}, o mokinys parašė ${studentAnswer}.`,
              correctApproach: `Patikrink savo skaičiavimus. Teisingas rezultatas: ${task.answer}.`,
            },
          ];

      results.push({
        taskNumber: task.num,
        studentAnswer: studentAnswer,
        studentLatex: studentAnswer,
        isCorrect,
        correctAnswer: isCorrect ? undefined : task.answer,
        correctLatex: isCorrect ? undefined : task.answer,
        points: pointsEarned,
        maxPoints: task.points,
        errors,
      });
    }

    return results;
  };

  // Išgauti atsakymą iš LaTeX pagal užduoties numerį (pvz. "1a", "2b")
  const extractAnswerFromLatex = (
    latex: string,
    taskId: string,
  ): string | null => {
    // Parsinamas taskId: "1a" -> sectionNum=1, letter="a"
    const match = taskId.match(/^(\d+)([a-z])$/i);
    if (!match) return null;

    const sectionNum = match[1]; // "1" arba "2"
    const letter = match[2].toLowerCase(); // "a", "b", "c"

    console.log(
      `[DEBUG] Parsing ${taskId}: section=${sectionNum}, letter=${letter}`,
    );
    console.log(`[DEBUG] Full LaTeX:`, latex);

    // Skaidome LaTeX į sekcijas pagal "\textbf{1.}", "\textbf{2.}" arba "1.", "2."
    // LaTeX stringe backslash yra escaped kaip \\
    const sections: Record<string, string> = {};

    // Bandome rasti sekcijas su \textbf{N.}
    const textbfPattern =
      /\\textbf\{(\d+)\.\}([\s\S]*?)(?=\\textbf\{\d+\.\}|$)/g;
    let sectionMatch;
    while ((sectionMatch = textbfPattern.exec(latex)) !== null) {
      sections[sectionMatch[1]] = sectionMatch[2];
    }

    // Jei neradome textbf, bandome paprastą "N." formatą
    if (Object.keys(sections).length === 0) {
      const simplePattern =
        /(?:^|\n)\s*(\d+)\.\s*([\s\S]*?)(?=(?:^|\n)\s*\d+\.|$)/gm;
      while ((sectionMatch = simplePattern.exec(latex)) !== null) {
        sections[sectionMatch[1]] = sectionMatch[2];
      }
    }

    console.log(`[DEBUG] Found sections:`, Object.keys(sections));

    // Ieškome teisingoje sekcijoje
    const sectionContent = sections[sectionNum] || latex;

    console.log(
      `[DEBUG] Section ${sectionNum} content:`,
      sectionContent.substring(0, 150),
    );

    // Ieškome atsakymo pagal raidę
    // Formatas: "a)\ 3 \cdot 18 = 54\ (km)" arba "a) 3 · 18 = 54 (km)"
    const answerPatterns = [
      // LaTeX formatas: a)\ ... = 54
      new RegExp(`${letter}\\)\\\\?\\s*[^=]*=\\s*([\\d.,]+)`, "i"),
      // Paprastas formatas: a) ... = 54
      new RegExp(`${letter}\\)\\s*[^=\\n]*=\\s*([\\d.,]+)`, "i"),
      // ats. formatas
      new RegExp(`${letter}\\)[^\\n]*?ats\\.?\\s*([\\d.,]+)`, "i"),
    ];

    for (const pattern of answerPatterns) {
      const answerMatch = sectionContent.match(pattern);
      if (answerMatch) {
        const answer = answerMatch[1].trim();
        console.log(`[DEBUG] ${taskId} found answer: ${answer}`);
        return answer;
      }
    }

    console.log(`[DEBUG] ${taskId} answer NOT FOUND`);
    return null;
  };

  // Normalizuoti skaičių palyginimui
  const normalizeNumber = (s: string): string => {
    return s.replace(/,/g, ".").replace(/\s/g, "").trim();
  };

  const handleUndo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      setEditedLatex(history[historyIndex - 1]);
    }
  };

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1);
      setEditedLatex(history[historyIndex + 1]);
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === "s" && isEditing) {
          e.preventDefault();
          handleSaveEdit();
        }
        if (e.key === "z") {
          e.preventDefault();
          handleUndo();
        }
        if (e.key === "y") {
          e.preventDefault();
          handleRedo();
        }
      }
      if (e.key === "Escape" && isEditing) {
        handleCancelEdit();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isEditing, historyIndex, history]);

  // Get status badge
  const getStatusBadge = () => {
    switch (status) {
      case "verified":
        return <Badge className="bg-green-500 text-white">Patvirtinta</Badge>;
      case "completed":
        return <Badge className="bg-blue-500 text-white">Apdorota</Badge>;
      case "processing":
        return <Badge className="bg-amber-500 text-white">Apdorojama</Badge>;
      default:
        return <Badge className="bg-gray-500 text-white">Laukia</Badge>;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="border-b bg-white px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-lg font-semibold">MatematikoVertintojas</h1>
          </div>
          {getStatusBadge()}
          <span className="text-sm text-muted-foreground">
            Dabartinė užduotis: {currentTask}/{totalTasks}
          </span>
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
                className="bg-green-600 hover:bg-green-700"
                onClick={() => setStatus("verified")}
              >
                <Check className="mr-2 h-4 w-4" />
                Patvirtinti
              </Button>
              <Button
                size="sm"
                onClick={handleSubmitForCheck}
                disabled={isChecking}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isChecking ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Tikrinama...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Pateikti tikrinimui
                  </>
                )}
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

      {/* Main content - Split view */}
      <div className="flex-1 flex min-h-0">
        {/* Left panel - Original image */}
        <div
          className="flex flex-col bg-slate-50 min-h-0"
          style={{ width: `${splitRatio}%` }}
        >
          <div className="p-3 border-b bg-white flex items-center justify-between">
            <h2 className="font-semibold text-gray-800">
              Originalus įkeltas failas
            </h2>
          </div>

          {/* Image controls */}
          <div className="px-3 py-2 border-b bg-white flex items-center gap-2 justify-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomOut}
              className="h-8 w-8 p-0"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>

            <input
              type="range"
              min={25}
              max={400}
              value={zoom}
              onChange={(e) => setZoom(parseInt(e.target.value))}
              className="w-32 h-1 accent-blue-500"
            />

            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomIn}
              className="h-8 w-8 p-0"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>

            <span className="text-sm text-gray-600 w-12 text-center">
              {zoom}%
            </span>

            <div className="w-px h-6 bg-gray-300 mx-2" />

            <Button
              variant="ghost"
              size="sm"
              onClick={handleRotateCCW}
              className="h-8 w-8 p-0"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRotateCW}
              className="h-8 w-8 p-0"
            >
              <RotateCw className="h-4 w-4" />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="h-8 w-8 p-0"
              title="Atstatyti"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>

            {/* Page navigation */}
            {totalPages > 1 && (
              <>
                <div className="w-px h-6 bg-gray-300 mx-2" />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handlePrevPage}
                  disabled={currentPage <= 1}
                  className="h-8 w-8 p-0"
                  title="Ankstesnis puslapis"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm text-gray-600 min-w-[60px] text-center">
                  {currentPage} / {totalPages}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleNextPage}
                  disabled={currentPage >= totalPages}
                  className="h-8 w-8 p-0"
                  title="Kitas puslapis"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </>
            )}
          </div>

          {/* Image container */}
          <div className="flex-1 overflow-auto p-4 bg-slate-100">
            <div
              className="bg-white shadow-lg rounded-lg transition-transform duration-200 mx-auto"
              style={{
                transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                transformOrigin: "top center",
                width: "fit-content",
              }}
            >
              <img
                src={imageUrl}
                alt="Mokinio darbas"
                className="block"
                onError={(e) => {
                  // Fallback to demo image if load fails
                  (e.target as HTMLImageElement).src = DEMO_IMAGE;
                }}
              />
            </div>
          </div>
        </div>

        {/* Resize handle */}
        <div
          className="w-1 bg-gray-200 hover:bg-blue-400 cursor-col-resize transition-colors"
          onMouseDown={(e) => {
            const startX = e.clientX;
            const startRatio = splitRatio;
            const container = e.currentTarget.parentElement;

            const handleMouseMove = (e: MouseEvent) => {
              if (container) {
                const containerWidth = container.offsetWidth;
                const delta = e.clientX - startX;
                const newRatio = startRatio + (delta / containerWidth) * 100;
                setSplitRatio(Math.min(75, Math.max(25, newRatio)));
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

        {/* Right panel - Digital version / LaTeX Editor */}
        <div className="flex-1 flex flex-col bg-white min-w-0">
          <div className="p-3 border-b flex items-center justify-between">
            <h2 className="font-semibold text-gray-800">
              Skaitmeninė versija (redaguojama)
            </h2>
          </div>

          {/* LaTeX Editor toolbar */}
          <div className="px-3 py-2 border-b flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">
              LaTeX Editor
            </span>

            <div className="flex-1" />

            {isEditing && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleUndo}
                  disabled={historyIndex === 0}
                  className="h-8 w-8 p-0"
                  title="Anuliuoti (Ctrl+Z)"
                >
                  <Undo2 className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRedo}
                  disabled={historyIndex >= history.length - 1}
                  className="h-8 w-8 p-0"
                  title="Pakartoti (Ctrl+Y)"
                >
                  <Redo2 className="h-4 w-4" />
                </Button>

                <div className="w-px h-6 bg-gray-300 mx-1" />

                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  title="Įterpti simbolį"
                >
                  <Type className="h-4 w-4" />
                </Button>
              </>
            )}

            <Button
              variant={showPreview ? "default" : "ghost"}
              size="sm"
              onClick={() => setShowPreview(!showPreview)}
              className="h-8 w-8 p-0"
              title={showPreview ? "Slėpti peržiūrą" : "Rodyti peržiūrą"}
            >
              {showPreview ? (
                <Eye className="h-4 w-4" />
              ) : (
                <EyeOff className="h-4 w-4" />
              )}
            </Button>

            <Button
              variant={showLatexCode ? "default" : "ghost"}
              size="sm"
              onClick={() => setShowLatexCode(!showLatexCode)}
              className="h-8 w-8 p-0"
              title="Rodyti LaTeX kodą"
            >
              <span className="text-xs font-mono">{}</span>
            </Button>

            {!isEditing && (
              <Button variant="outline" size="sm" onClick={handleStartEdit}>
                <Edit3 className="mr-1 h-3 w-3" />
                Edit
              </Button>
            )}
          </div>

          {/* Editor content */}
          <div className="flex-1 overflow-auto">
            {isEditing ? (
              <div className="h-full flex flex-col">
                {/* Code editor */}
                <div className="flex-1 p-4">
                  <textarea
                    value={editedLatex}
                    onChange={(e) => setEditedLatex(e.target.value)}
                    className="w-full h-full p-4 font-mono text-sm border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Įveskite LaTeX kodą..."
                    spellCheck={false}
                  />
                </div>

                {/* Preview */}
                {showPreview && (
                  <div className="border-t p-4 bg-slate-50">
                    <p className="text-xs text-muted-foreground mb-2 font-medium">
                      LaTeX Preview
                    </p>
                    <div className="bg-white rounded-lg p-4 border min-h-[100px]">
                      {editedLatex ? (
                        <MathRenderer math={editedLatex} block />
                      ) : (
                        <p className="text-muted-foreground text-sm">
                          No content to preview
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-6">
                {/* Rendered math content */}
                <div className="bg-slate-50 rounded-lg p-6 min-h-[300px]">
                  {showPreview && latexContent ? (
                    <div className="text-lg leading-relaxed">
                      <MathRenderer math={latexContent} block />
                    </div>
                  ) : (
                    <p className="text-muted-foreground">{recognizedText}</p>
                  )}
                </div>

                {/* LaTeX code view */}
                {showLatexCode && (
                  <div className="mt-4">
                    <p className="text-xs text-muted-foreground mb-2 font-medium">
                      LaTeX kodas:
                    </p>
                    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm overflow-x-auto">
                      {latexContent}
                    </pre>
                  </div>
                )}

                {/* Confidence info and Submit button */}
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    OCR tikslumas:{" "}
                    <strong
                      className={cn(
                        confidence >= 0.9
                          ? "text-green-600"
                          : confidence >= 0.7
                            ? "text-amber-600"
                            : "text-red-600",
                      )}
                    >
                      {Math.round(confidence * 100)}%
                    </strong>
                  </span>

                  <Button
                    onClick={handleSubmitForCheck}
                    disabled={isChecking}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isChecking ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Tikrinama...
                      </>
                    ) : (
                      <>
                        <Send className="mr-2 h-4 w-4" />
                        Pateikti tikrinimui
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Check Results Modal */}
      <CheckResultsModal
        isOpen={showResults}
        onClose={() => setShowResults(false)}
        onSave={handleSaveResults}
        isSaving={isSaving}
        studentName={currentFile?.studentId ? "Mokinys" : "Demo mokinys"}
        testTitle={currentFile?.testId ? "Kontrolinis" : "Demo kontrolinis"}
        results={checkResults}
        totalPoints={checkResults.reduce((sum, r) => sum + r.points, 0)}
        maxPoints={checkResults.reduce((sum, r) => sum + r.maxPoints, 0)}
        grade={calculateGrade(
          checkResults.reduce((sum, r) => sum + r.points, 0),
          checkResults.reduce((sum, r) => sum + r.maxPoints, 0),
        )}
        aiExplanation={
          // Surenkame visus AI paaiškinimus iš rezultatų
          checkResults
            .filter((r: any) => r.suggestion)
            .map((r: any) => `**${r.taskId} užduotis:** ${r.suggestion}`)
            .join("\n\n") || generateAIFeedback(checkResults)
        }
      />
    </div>
  );
}

// Apskaičiuoti pažymį pagal Lietuvos sistemą
function calculateGrade(points: number, maxPoints: number): number {
  if (maxPoints === 0) return 1;
  const percentage = (points / maxPoints) * 100;

  if (percentage >= 95) return 10;
  if (percentage >= 85) return 9;
  if (percentage >= 75) return 8;
  if (percentage >= 65) return 7;
  if (percentage >= 55) return 6;
  if (percentage >= 45) return 5;
  if (percentage >= 35) return 4;
  if (percentage >= 25) return 3;
  if (percentage >= 15) return 2;
  return 1;
}

// Generuoti AI feedback pagal tikrinimo rezultatus
function generateAIFeedback(
  results: Array<{
    isCorrect: boolean;
    errors?: Array<{ type: string; description: string }>;
  }>,
): string {
  const correctCount = results.filter((r) => r.isCorrect).length;
  const totalCount = results.length;
  const percentage = totalCount > 0 ? (correctCount / totalCount) * 100 : 0;

  // Jei visi teisingi
  if (correctCount === totalCount) {
    return "Puiku! Visi atsakymai teisingi. Mokinys puikiai suprato temą ir atliko visus skaičiavimus be klaidų.";
  }

  // Jei dauguma teisingi
  if (percentage >= 80) {
    const incorrectCount = totalCount - correctCount;
    return `Labai gerai! ${correctCount} iš ${totalCount} atsakymų teisingi. Tik ${incorrectCount} nedidelė(-s) klaida(-os). Rekomenduojama atidžiau tikrinti atsakymus.`;
  }

  // Jei pusė teisingų
  if (percentage >= 50) {
    return `Vidutiniškai. ${correctCount} iš ${totalCount} atsakymų teisingi. Rekomenduojama pakartoti temą ir daugiau praktikuotis.`;
  }

  // Jei mažuma teisingų
  return `Reikia daugiau praktikos. Tik ${correctCount} iš ${totalCount} atsakymų teisingi. Siūloma pakartoti pagrindines taisykles ir atlikti papildomų pratimų.`;
}
