/**
 * Kontrolinių generavimo puslapis - AI pagalba kuriant kontrolinius
 */

import { useState, useCallback } from "react";
import {
  Sparkles,
  FileText,
  ChevronLeft,
  Copy,
  Download,
  Check,
  RefreshCw,
  BookOpen,
  Edit3,
  Eye,
  Printer,
  AlertTriangle,
  Save,
  FileDown,
  CheckCircle,
} from "lucide-react";
import { Link } from "react-router-dom";
import {
  PageHeader,
  PageLoader,
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
  MathText,
} from "@/components/ui";
import { CurriculumTopicSelector } from "@/components/CurriculumTopicSelector";
import apiClient from "@/api/client";

// === Tipai ===
interface GeneratedTask {
  number: number;
  text: string;
  answer: string; // Backend grąžina "answer", ne "correct_answer"
  answer_latex?: string;
  solution_steps: string[]; // Backend grąžina masyvą
  points: number;
  difficulty: string;
  topic: string;
}

interface GeneratedVariant {
  variant_name: string;
  tasks: GeneratedTask[];
}

interface GeneratedTest {
  title: string;
  topic: string;
  grade_level: number;
  total_points: number;
  variants: GeneratedVariant[];
  generated_at: string;
}

const DIFFICULTY_OPTIONS = [
  {
    value: "easy",
    label: "Lengvas",
    description: "Paprastos užduotys, vienas veiksmas",
  },
  {
    value: "medium",
    label: "Vidutinis",
    description: "Kelių veiksmų užduotys",
  },
  {
    value: "hard",
    label: "Sudėtingas",
    description: "Kompleksinės užduotys su paaiškinimu",
  },
  {
    value: "vbe",
    label: "VBE stilius",
    description: "Brandos egzamino lygio uždaviniai (a, b, c dalys)",
  },
  {
    value: "mixed",
    label: "Mišrus",
    description: "Įvairaus sudėtingumo užduotys",
  },
];

export default function TestGeneratorPage() {
  // Formos būsena
  const [grade, setGrade] = useState<number>(6);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [selectedSubtopics, setSelectedSubtopics] = useState<string[]>([]); // NAUJAS: potemių pasirinkimas
  const [taskCount, setTaskCount] = useState<number>(5);
  const [variantCount, setVariantCount] = useState<number>(2);
  const [difficulty, setDifficulty] = useState<string>("medium");
  const [includeSolutions, setIncludeSolutions] = useState<boolean>(true);
  const [useTemplateGenerator, setUseTemplateGenerator] =
    useState<boolean>(true); // NAUJAS: šabloninis vs AI

  // Generavimo būsena
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedTest, setGeneratedTest] = useState<GeneratedTest | null>(
    null,
  );
  const [activeVariant, setActiveVariant] = useState<number>(0);
  const [showSolutions, setShowSolutions] = useState<boolean>(false);

  // Generuoti kontrolinį
  const handleGenerate = useCallback(async () => {
    if (selectedSubtopics.length === 0) {
      setError("Pasirinkite bent vieną potemę iš programos temų");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedTest(null);

    try {
      // Temos pavadinimas iš pasirinktų topic ID
      const topicString =
        selectedTopics.length === 1
          ? selectedTopics[0]
          : selectedTopics.join(", ");

      const { data } = await apiClient.post<GeneratedTest>("/tests/generate", {
        topic: topicString,
        topics: selectedTopics,
        subtopics: selectedSubtopics,
        use_curriculum: true,
        grade_level: grade,
        task_count: taskCount,
        variant_count: variantCount,
        difficulty,
        include_solutions: includeSolutions,
        save_to_db: false,
        use_template_generator: useTemplateGenerator,
      });

      setGeneratedTest(data);
      setActiveVariant(0);
      setShowSolutions(false);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Nepavyko sugeneruoti kontrolinio";
      setError(message);
    } finally {
      setIsGenerating(false);
    }
  }, [
    selectedTopics,
    selectedSubtopics,
    grade,
    taskCount,
    variantCount,
    difficulty,
    includeSolutions,
    useTemplateGenerator,
  ]);

  // Kopijuoti į clipboard
  const handleCopy = useCallback((text: string) => {
    navigator.clipboard.writeText(text);
  }, []);

  // Eksportuoti kaip tekstą
  const handleExport = useCallback(() => {
    if (!generatedTest) return;

    let content = `${generatedTest.title}\n`;
    content += `Tema: ${generatedTest.topic}\n`;
    content += `Klasė: ${generatedTest.grade_level}\n`;
    content += `Iš viso taškų: ${generatedTest.total_points}\n\n`;

    generatedTest.variants.forEach((variant) => {
      content += `\n=== ${variant.variant_name} ===\n\n`;
      variant.tasks.forEach((task) => {
        content += `${task.number}. (${task.points} tšk.) ${task.text}\n`;
        if (showSolutions) {
          content += `   Atsakymas: ${task.answer}\n`;
          if (task.solution_steps && task.solution_steps.length > 0) {
            content += `   Sprendimas: ${task.solution_steps.join("; ")}\n`;
          }
        }
        content += "\n";
      });
    });

    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${generatedTest.title.replace(/\s+/g, "_")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }, [generatedTest, showSolutions]);

  // === NAUJAS: Išsaugoti į DB ir generuoti PDF ===
  const [isSaving, setIsSaving] = useState(false);
  const [savedExam, setSavedExam] = useState<{
    id: number;
    exam_id: string;
    student_pdf?: string;
    teacher_pdf?: string;
  } | null>(null);

  const handleSaveAndGeneratePDF = useCallback(async () => {
    if (!generatedTest) return;

    setIsSaving(true);
    setError(null);

    try {
      // Konvertuojam sugeneruotą testą į exam formatą
      const examData = {
        class_id: 1, // TODO: pridėti klasės pasirinkimą
        title: generatedTest.title,
        topic: generatedTest.topic || selectedTopics.join(", "),
        grade: grade, // Klasė (5-12)
        task_count: generatedTest.variants[0]?.tasks.length || 5,
        difficulty: difficulty === "easy" ? 1 : difficulty === "hard" ? 3 : 2,
        variants_count: generatedTest.variants.length,
        tasks: generatedTest.variants.flatMap((variant, vIdx) =>
          variant.tasks.map((task, tIdx) => ({
            variant_index: vIdx,
            number: String(task.number),
            text: task.text,
            correct_answer: task.answer,
            points: task.points,
          })),
        ),
      };

      const { data } = await apiClient.post("/exams/from-generated", examData);

      setSavedExam({
        id: data.id,
        exam_id: data.exam_id,
        student_pdf: data.student_pdf,
        teacher_pdf: data.teacher_pdf,
      });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Nepavyko išsaugoti kontrolinio";
      setError(message);
    } finally {
      setIsSaving(false);
    }
  }, [generatedTest, selectedTopics, difficulty]);

  // Parsisiųsti PDF
  const handleDownloadPDF = useCallback(
    (pdfPath: string, isTeacher: boolean) => {
      // PDF yra backend'e, reikia sukurti download URL
      const filename = pdfPath.split(/[/\\]/).pop() || "exam.pdf";
      const downloadUrl = `/api/v1/exams/download/${filename}`;

      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = filename;
      a.click();
    },
    [],
  );

  return (
    <div>
      <PageHeader
        title="Kontrolinio generavimas"
        description={
          useTemplateGenerator
            ? "Šabloninis generatorius (greitas, tikslus)"
            : "AI generatorius (Gemini)"
        }
        actions={
          <Link to="/kontroliniai">
            <Button variant="secondary">
              <ChevronLeft className="h-4 w-4" />
              Grįžti
            </Button>
          </Link>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Kairė pusė - Forma */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
                Generavimo nustatymai
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Generavimo metodas */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Generavimo metodas
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setUseTemplateGenerator(true)}
                    className={`rounded-lg p-3 text-left transition-colors border ${
                      useTemplateGenerator
                        ? "border-green-500 bg-green-50 ring-1 ring-green-500"
                        : "border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <span className="block text-sm font-medium text-gray-900">
                      📐 Šabloninis
                    </span>
                    <span className="block text-xs text-gray-500">
                      Greitas, 100% tikslus
                    </span>
                  </button>
                  <button
                    onClick={() => setUseTemplateGenerator(false)}
                    className={`rounded-lg p-3 text-left transition-colors border ${
                      !useTemplateGenerator
                        ? "border-purple-500 bg-purple-50 ring-1 ring-purple-500"
                        : "border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <span className="block text-sm font-medium text-gray-900">
                      🤖 AI (Gemini)
                    </span>
                    <span className="block text-xs text-gray-500">
                      Kūrybiškas, lėtesnis
                    </span>
                  </button>
                </div>
                {useTemplateGenerator && (
                  <p className="mt-2 text-xs text-green-600">
                    ✓ Rekomenduojama: greitas, tikslūs atsakymai, nemokamas
                  </p>
                )}
              </div>

              {/* Klasė */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Klasė
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {[5, 6, 7, 8, 9, 10, 11, 12].map((g) => (
                    <button
                      key={g}
                      onClick={() => {
                        setGrade(g);
                        setSelectedTopics([]); // Reset temos kai keičiasi klasė
                        setSelectedSubtopics([]); // Reset potemės
                      }}
                      className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                        grade === g
                          ? "bg-blue-600 text-white"
                          : g >= 10
                            ? "bg-purple-100 text-purple-700 hover:bg-purple-200"
                            : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {g} kl.{g >= 10 && " 🎓"}
                    </button>
                  ))}
                </div>
                {grade >= 10 && (
                  <p className="mt-1 text-xs text-purple-600">
                    🎓 VBE lygio temos ir uždaviniai
                  </p>
                )}
              </div>

              {/* Programos temos (iš JSON failų) */}
              <div>
                <CurriculumTopicSelector
                  grade={grade}
                  selectedTopics={selectedTopics}
                  selectedSubtopics={selectedSubtopics}
                  difficulty={difficulty}
                  onTopicsChange={setSelectedTopics}
                  onSubtopicsChange={setSelectedSubtopics}
                />
              </div>

              {/* Sudėtingumas */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Sudėtingumas
                </label>
                <div className="space-y-2">
                  {DIFFICULTY_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setDifficulty(opt.value)}
                      className={`w-full rounded-lg border p-3 text-left transition-colors ${
                        difficulty === opt.value
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:bg-gray-50"
                      }`}
                    >
                      <span className="block text-sm font-medium text-gray-900">
                        {opt.label}
                      </span>
                      <span className="block text-xs text-gray-500">
                        {opt.description}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Uždavinių kiekis */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Uždavinių skaičius: <strong>{taskCount}</strong>
                </label>
                <input
                  type="range"
                  min={2}
                  max={15}
                  value={taskCount}
                  onChange={(e) => setTaskCount(parseInt(e.target.value))}
                  className="w-full accent-blue-600"
                />
                <div className="mt-1 flex justify-between text-xs text-gray-400">
                  <span>2</span>
                  <span>15</span>
                </div>
              </div>

              {/* Variantų kiekis */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Variantų skaičius
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {[1, 2, 3, 4].map((v) => (
                    <button
                      key={v}
                      onClick={() => setVariantCount(v)}
                      className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                        variantCount === v
                          ? "bg-blue-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>

              {/* Įtraukti sprendimus */}
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="includeSolutions"
                  checked={includeSolutions}
                  onChange={(e) => setIncludeSolutions(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label
                  htmlFor="includeSolutions"
                  className="text-sm text-gray-700"
                >
                  Įtraukti sprendimų žingsnius
                </label>
              </div>

              {/* Error */}
              {error && (
                <div className="flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                  <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Generate Button */}
              <Button
                onClick={handleGenerate}
                disabled={isGenerating || selectedSubtopics.length === 0}
                className="w-full"
                size="lg"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Generuojama...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Generuoti kontrolinį
                  </>
                )}
              </Button>

              <p className="text-center text-xs text-gray-500">
                Generavimas gali užtrukti iki 30 sekundžių
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Dešinė pusė - Rezultatas */}
        <div className="lg:col-span-2">
          {isGenerating && (
            <Card>
              <CardContent className="py-16">
                <PageLoader
                  text={
                    useTemplateGenerator
                      ? "Generuojamas kontrolinis..."
                      : "AI generuoja kontrolinį..."
                  }
                />
              </CardContent>
            </Card>
          )}

          {!isGenerating && !generatedTest && (
            <Card>
              <CardContent className="py-16 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
                  <Sparkles className="h-8 w-8 text-purple-500" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-gray-900">
                  Pasirinkite nustatymus ir spauskite "Generuoti"
                </h3>
                <p className="text-gray-500">
                  {useTemplateGenerator
                    ? "Sistema sukurs kontrolinį darbą pagal jūsų pasirinkimus"
                    : "AI sukurs kontrolinį darbą pagal jūsų pasirinkimus"}
                </p>
              </CardContent>
            </Card>
          )}

          {generatedTest && (
            <div className="space-y-4">
              {/* Header su veiksmais */}
              <Card>
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">
                        {generatedTest.title}
                      </h2>
                      <p className="text-sm text-gray-500">
                        {generatedTest.topic} • {generatedTest.grade_level}{" "}
                        klasė • {generatedTest.total_points} taškų
                      </p>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setShowSolutions(!showSolutions)}
                      >
                        {showSolutions ? (
                          <>
                            <Eye className="h-4 w-4" />
                            Slėpti atsakymus
                          </>
                        ) : (
                          <>
                            <BookOpen className="h-4 w-4" />
                            Rodyti atsakymus
                          </>
                        )}
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={handleExport}
                      >
                        <Download className="h-4 w-4" />
                        Eksportuoti TXT
                      </Button>

                      {/* NAUJAS: Išsaugoti ir generuoti PDF */}
                      {!savedExam ? (
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={handleSaveAndGeneratePDF}
                          disabled={isSaving}
                        >
                          {isSaving ? (
                            <>
                              <RefreshCw className="h-4 w-4 animate-spin" />
                              Saugoma...
                            </>
                          ) : (
                            <>
                              <Save className="h-4 w-4" />
                              Išsaugoti ir generuoti PDF
                            </>
                          )}
                        </Button>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="flex items-center gap-1 text-sm text-green-600">
                            <CheckCircle className="h-4 w-4" />
                            Išsaugota (ID: {savedExam.exam_id})
                          </span>
                          {savedExam.student_pdf && (
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() =>
                                window.open(
                                  `/api/v1/exams/pdf/${savedExam.exam_id}`,
                                  "_blank",
                                )
                              }
                            >
                              <FileDown className="h-4 w-4" />
                              PDF (mokinys)
                            </Button>
                          )}
                          {savedExam.teacher_pdf && (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() =>
                                window.open(
                                  `/api/v1/exams/pdf/${savedExam.exam_id}?teacher=true`,
                                  "_blank",
                                )
                              }
                            >
                              <FileDown className="h-4 w-4" />
                              PDF (mokytojas)
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Variantų tabs */}
              <div className="flex gap-2">
                {generatedTest.variants.map((variant, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveVariant(idx)}
                    className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                      activeVariant === idx
                        ? "bg-blue-600 text-white"
                        : "bg-white text-gray-700 hover:bg-gray-50 border"
                    }`}
                  >
                    {variant.variant_name}
                  </button>
                ))}
              </div>

              {/* Aktyvus variantas */}
              <Card>
                <CardHeader className="border-b bg-gray-50">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <FileText className="h-5 w-5" />
                    {generatedTest.variants[activeVariant].variant_name}
                  </CardTitle>
                </CardHeader>
                <CardContent className="divide-y">
                  {generatedTest.variants[activeVariant].tasks.map((task) => (
                    <div key={task.number} className="py-5">
                      <div className="mb-3 flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">
                            {task.number}
                          </span>
                          <Badge
                            variant={
                              task.difficulty === "easy"
                                ? "success"
                                : task.difficulty === "hard"
                                  ? "destructive"
                                  : "secondary"
                            }
                          >
                            {task.points} tšk.
                          </Badge>
                        </div>
                        <button
                          onClick={() => handleCopy(task.text)}
                          className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                          title="Kopijuoti"
                        >
                          <Copy className="h-4 w-4" />
                        </button>
                      </div>

                      <div className="ml-11">
                        <div className="prose prose-sm max-w-none text-gray-800">
                          <MathText text={task.text} />
                        </div>

                        {showSolutions && (
                          <div className="mt-4 rounded-lg bg-green-50 p-4">
                            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-green-800">
                              <Check className="h-4 w-4" />
                              Atsakymas:
                            </div>
                            <div className="mb-3 text-green-900 font-medium text-lg">
                              <MathText
                                text={task.answer_latex || task.answer}
                              />
                            </div>
                            {task.solution_steps &&
                              task.solution_steps.length > 0 && (
                                <div className="border-t border-green-200 pt-3 text-sm text-green-800">
                                  <div className="mb-1 flex items-center gap-2 font-medium">
                                    <Edit3 className="h-4 w-4" />
                                    Sprendimas:
                                  </div>
                                  <div className="whitespace-pre-wrap space-y-1">
                                    {task.solution_steps.map((step, idx) => (
                                      <div key={idx}>
                                        <MathText text={step} />
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Regenerate button */}
              <div className="text-center">
                <Button
                  variant="secondary"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                >
                  <RefreshCw className="h-4 w-4" />
                  Generuoti iš naujo
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
