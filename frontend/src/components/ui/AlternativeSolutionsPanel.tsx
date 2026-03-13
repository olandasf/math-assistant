/**
 * AlternativeSolutionsPanel - Alternatyvių sprendimų komponentas
 * Rodo 2-3 skirtingus būdus, kaip galima išspręsti uždavinį
 */

import { useState } from "react";
import {
  Lightbulb,
  ChevronDown,
  ChevronUp,
  Loader2,
  RefreshCw,
  BookOpen,
  Sparkles,
} from "lucide-react";
import { Button, Badge } from "@/components/ui";
import { MathRenderer } from "@/components/ui/MathRenderer";
import { useAlternativeSolutions } from "@/api/hooks";
import { cn } from "@/lib/utils";

interface AlternativeSolutionsPanelProps {
  problem: string;
  correctAnswer: string;
  gradeLevel?: number;
  className?: string;
}

export function AlternativeSolutionsPanel({
  problem,
  correctAnswer,
  gradeLevel = 6,
  className,
}: AlternativeSolutionsPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [solutions, setSolutions] = useState<string | null>(null);
  const [hasLoaded, setHasLoaded] = useState(false);

  const alternativeSolutions = useAlternativeSolutions();

  const handleLoadSolutions = async () => {
    if (hasLoaded && solutions) {
      // Jau turime sprendimus - tik toggle
      setIsExpanded(!isExpanded);
      return;
    }

    setIsExpanded(true);

    try {
      const response = await alternativeSolutions.mutateAsync({
        problem,
        correct_answer: correctAnswer,
        grade_level: gradeLevel,
        num_solutions: 3,
      });

      if (response.success) {
        setSolutions(response.solutions);
        setHasLoaded(true);
      } else {
        setSolutions(
          `Nepavyko sugeneruoti alternatyvių sprendimų: ${
            response.error || "Nežinoma klaida"
          }`
        );
      }
    } catch (error) {
      setSolutions(
        "Klaida gaunant alternatyvius sprendimus. Patikrinkite ar Gemini API raktas nustatytas."
      );
    }
  };

  const handleRefresh = async () => {
    setHasLoaded(false);
    setSolutions(null);

    try {
      const response = await alternativeSolutions.mutateAsync({
        problem,
        correct_answer: correctAnswer,
        grade_level: gradeLevel,
        num_solutions: 3,
      });

      if (response.success) {
        setSolutions(response.solutions);
        setHasLoaded(true);
      } else {
        setSolutions(
          `Nepavyko sugeneruoti: ${response.error || "Nežinoma klaida"}`
        );
      }
    } catch (error) {
      setSolutions("Klaida gaunant sprendimus.");
    }
  };

  // Paverčiame sprendimų tekstą į formatu su LaTeX palaikymu
  const renderSolutions = (text: string) => {
    // Skaidome pagal sekcijas (## N būdas:)
    const sections = text.split(/(?=##\s*\d+\s*būdas)/gi);

    return sections.map((section, idx) => {
      if (!section.trim()) return null;

      // Ištraukiame pavadinimą
      const titleMatch = section.match(
        /##\s*(\d+)\s*būdas[:\s]*(.+?)(?=\n|$)/i
      );
      const title = titleMatch
        ? `${titleMatch[1]} būdas: ${titleMatch[2].trim()}`
        : `Sprendimas ${idx + 1}`;

      // Likusį turinį
      const content = section
        .replace(/##\s*\d+\s*būdas[:\s]*.+?(?=\n|$)/i, "")
        .trim();

      // Konvertuojame LaTeX ($...$) į MathRenderer
      const renderContent = (text: string) => {
        const parts = text.split(/(\$[^$]+\$)/g);
        return parts.map((part, i) => {
          if (part.startsWith("$") && part.endsWith("$")) {
            const latex = part.slice(1, -1);
            return <MathRenderer key={i} math={latex} />;
          }
          // Paprasti markdown formatavimas
          return (
            <span key={i}>
              {part.split("\n").map((line, j) => (
                <span key={j}>
                  {line.startsWith("**") && line.endsWith("**") ? (
                    <strong>{line.slice(2, -2)}</strong>
                  ) : line.startsWith("**") ? (
                    <strong>{line.slice(2).replace(":**", ":")}</strong>
                  ) : (
                    line
                  )}
                  {j < part.split("\n").length - 1 && <br />}
                </span>
              ))}
            </span>
          );
        });
      };

      return (
        <div
          key={idx}
          className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200"
        >
          <h4 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            {title}
          </h4>
          <div className="text-sm text-gray-700 space-y-2 whitespace-pre-wrap">
            {renderContent(content)}
          </div>
        </div>
      );
    });
  };

  return (
    <div
      className={cn(
        "border rounded-lg overflow-hidden bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200",
        className
      )}
    >
      {/* Header */}
      <button
        onClick={handleLoadSolutions}
        disabled={alternativeSolutions.isPending}
        className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-purple-100 to-blue-100 hover:from-purple-150 hover:to-blue-150 transition-colors"
      >
        <div className="flex items-center gap-3">
          {alternativeSolutions.isPending ? (
            <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />
          ) : (
            <Lightbulb className="w-5 h-5 text-purple-600" />
          )}
          <span className="font-medium text-purple-800">
            Alternatyvūs sprendimo būdai
          </span>
          <Badge className="bg-purple-200 text-purple-800">AI</Badge>
        </div>
        {hasLoaded ? (
          isExpanded ? (
            <ChevronUp className="w-5 h-5 text-purple-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-purple-600" />
          )
        ) : (
          <span className="text-sm text-purple-600">
            {alternativeSolutions.isPending
              ? "Generuojama..."
              : "Spustelėkite, kad pamatytumėte"}
          </span>
        )}
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="p-4 bg-white">
          {alternativeSolutions.isPending ? (
            <div className="flex flex-col items-center py-8">
              <Loader2 className="w-8 h-8 text-purple-500 animate-spin mb-3" />
              <p className="text-sm text-gray-600">
                AI generuoja alternatyvius sprendimo būdus...
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Tai gali užtrukti iki 10 sekundžių
              </p>
            </div>
          ) : solutions ? (
            <div>
              {/* Refresh button */}
              <div className="flex justify-end mb-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefresh}
                  disabled={alternativeSolutions.isPending}
                >
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Generuoti iš naujo
                </Button>
              </div>

              {/* Solutions */}
              <div className="space-y-4">
                {/* Uždavinio priminimas */}
                <div className="p-3 bg-gray-50 rounded-lg border">
                  <h4 className="text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Uždavinys:
                  </h4>
                  <p className="text-sm text-gray-600">{problem}</p>
                  <p className="text-sm text-gray-800 mt-1">
                    <strong>Atsakymas:</strong> {correctAnswer}
                  </p>
                </div>

                {/* Sprendimai */}
                <div className="border-t pt-4">
                  <h4 className="text-sm font-medium text-gray-800 mb-3">
                    Galimi sprendimo būdai:
                  </h4>
                  {renderSolutions(solutions)}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Lightbulb className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>Spustelėkite, kad įkeltumėte alternatyvius sprendimus</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AlternativeSolutionsPanel;
