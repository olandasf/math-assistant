/**
 * Quick Check Page - Greitas darbų tikrinimo režimas
 *
 * Funkcijos:
 * - Greita navigacija su klaviatūra
 * - Vaizdų peržiūra su OCR rezultatais
 * - Greiti pažymių įvedimas
 * - Batch operacijos
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  ChevronLeft,
  ChevronRight,
  Check,
  X,
  Keyboard,
  Zap,
  Eye,
  FileCheck,
  Save,
  SkipForward,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

// Demo darbai
const demoWorks = [
  {
    id: 1,
    studentName: "Jonas Jonaitis",
    className: "5a",
    status: "pending",
    imageUrl: "/demo/work1.jpg",
  },
  {
    id: 2,
    studentName: "Petras Petraitis",
    className: "5a",
    status: "pending",
    imageUrl: "/demo/work2.jpg",
  },
  {
    id: 3,
    studentName: "Ona Onaitė",
    className: "5a",
    status: "pending",
    imageUrl: "/demo/work3.jpg",
  },
  {
    id: 4,
    studentName: "Marija Marijaitė",
    className: "5a",
    status: "pending",
    imageUrl: "/demo/work4.jpg",
  },
  {
    id: 5,
    studentName: "Tomas Tomaitis",
    className: "5a",
    status: "pending",
    imageUrl: "/demo/work5.jpg",
  },
];

// Pažymių mygtukai
const gradeButtons = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1];

export function QuickCheckPage() {
  const navigate = useNavigate();
  const [works, setWorks] = useState(demoWorks);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentGrade, setCurrentGrade] = useState<number | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [checkedCount, setCheckedCount] = useState(0);

  const currentWork = works[currentIndex];
  const totalWorks = works.length;
  const progress = Math.round((checkedCount / totalWorks) * 100);

  // Eiti į ankstesnį darbą
  const goToPrevious = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setCurrentGrade(null);
    }
  }, [currentIndex]);

  // Eiti į kitą darbą
  const goToNext = useCallback(() => {
    if (currentIndex < totalWorks - 1) {
      setCurrentIndex(currentIndex + 1);
      setCurrentGrade(null);
    }
  }, [currentIndex, totalWorks]);

  // Išsaugoti pažymį ir eiti toliau
  const saveAndNext = useCallback(() => {
    if (currentGrade === null) return;

    setWorks((prev) =>
      prev.map((w, i) =>
        i === currentIndex
          ? { ...w, status: "checked", grade: currentGrade }
          : w
      )
    );
    setCheckedCount((prev) => prev + 1);

    if (currentIndex < totalWorks - 1) {
      setCurrentIndex(currentIndex + 1);
      setCurrentGrade(null);
    }
  }, [currentGrade, currentIndex, totalWorks]);

  // Praleisti darbą
  const skipWork = useCallback(() => {
    setWorks((prev) =>
      prev.map((w, i) => (i === currentIndex ? { ...w, status: "skipped" } : w))
    );

    if (currentIndex < totalWorks - 1) {
      setCurrentIndex(currentIndex + 1);
      setCurrentGrade(null);
    }
  }, [currentIndex, totalWorks]);

  // Klaviatūros shortcut'ai
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Jei focus'as input'e, ignoruojam
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      switch (e.key) {
        case "ArrowLeft":
          e.preventDefault();
          goToPrevious();
          break;
        case "ArrowRight":
          e.preventDefault();
          goToNext();
          break;
        case "Enter":
          e.preventDefault();
          saveAndNext();
          break;
        case "s":
        case "S":
          e.preventDefault();
          skipWork();
          break;
        case "?":
          e.preventDefault();
          setShowShortcuts(!showShortcuts);
          break;
        case "Escape":
          e.preventDefault();
          setShowShortcuts(false);
          break;
        // Skaičių klavišai pažymiams
        case "0":
          e.preventDefault();
          setCurrentGrade(10);
          break;
        case "1":
        case "2":
        case "3":
        case "4":
        case "5":
        case "6":
        case "7":
        case "8":
        case "9":
          e.preventDefault();
          setCurrentGrade(parseInt(e.key));
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [goToPrevious, goToNext, saveAndNext, skipWork, showShortcuts]);

  const getGradeColor = (grade: number) => {
    if (grade >= 9) return "bg-green-500 hover:bg-green-600 text-white";
    if (grade >= 7) return "bg-blue-500 hover:bg-blue-600 text-white";
    if (grade >= 5) return "bg-amber-500 hover:bg-amber-600 text-white";
    return "bg-red-500 hover:bg-red-600 text-white";
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <PageHeader
          title="Greitas tikrinimas"
          description={`${currentIndex + 1} / ${totalWorks} darbų`}
        />

        <div className="flex items-center gap-3">
          {/* Progresas */}
          <div className="flex items-center gap-2 text-sm">
            <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="text-muted-foreground">
              {checkedCount}/{totalWorks}
            </span>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowShortcuts(!showShortcuts)}
          >
            <Keyboard className="h-4 w-4 mr-1" />
            Shortcuts
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 grid grid-cols-3 gap-4 min-h-0">
        {/* Left: Darbų sąrašas */}
        <Card className="overflow-hidden">
          <CardHeader className="py-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <FileCheck className="h-4 w-4" />
              Darbai ({totalWorks})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-2 overflow-auto max-h-[calc(100vh-16rem)]">
            <div className="space-y-1">
              {works.map((work, index) => (
                <button
                  key={work.id}
                  onClick={() => {
                    setCurrentIndex(index);
                    setCurrentGrade(null);
                  }}
                  className={`w-full p-2 rounded-lg text-left text-sm transition-colors flex items-center justify-between ${
                    index === currentIndex
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                >
                  <div>
                    <div className="font-medium">{work.studentName}</div>
                    <div className="text-xs opacity-70">{work.className}</div>
                  </div>
                  {work.status === "checked" && (
                    <Badge
                      variant="outline"
                      className="bg-green-50 text-green-700 border-green-200"
                    >
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      {(work as any).grade}
                    </Badge>
                  )}
                  {work.status === "skipped" && (
                    <Badge
                      variant="outline"
                      className="bg-amber-50 text-amber-700 border-amber-200"
                    >
                      <SkipForward className="h-3 w-3" />
                    </Badge>
                  )}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Center: Darbo vaizdas */}
        <Card className="col-span-2 overflow-hidden flex flex-col">
          <CardHeader className="py-3 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-base">
                {currentWork.studentName}
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                {currentWork.className}
              </p>
            </div>

            {/* Navigacija */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={goToPrevious}
                disabled={currentIndex === 0}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm text-muted-foreground">
                {currentIndex + 1} / {totalWorks}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={goToNext}
                disabled={currentIndex === totalWorks - 1}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-4">
            {/* Vaizdo vieta */}
            <div className="flex-1 bg-gray-100 rounded-lg flex items-center justify-center min-h-[300px] mb-4">
              <div className="text-center text-muted-foreground">
                <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Darbo vaizdas</p>
                <p className="text-xs">
                  (Čia bus OCR rezultatai ir originalus vaizdas)
                </p>
              </div>
            </div>

            {/* Pažymių įvedimas */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Pažymys:</span>
                {currentGrade !== null && (
                  <Badge className={getGradeColor(currentGrade)}>
                    {currentGrade}
                  </Badge>
                )}
              </div>

              <div className="flex gap-1">
                {gradeButtons.map((grade) => (
                  <Button
                    key={grade}
                    variant={currentGrade === grade ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentGrade(grade)}
                    className={`w-9 h-9 ${
                      currentGrade === grade ? getGradeColor(grade) : ""
                    }`}
                  >
                    {grade}
                  </Button>
                ))}
              </div>

              <div className="flex gap-2 pt-2">
                <Button
                  onClick={saveAndNext}
                  disabled={currentGrade === null}
                  className="flex-1"
                >
                  <Check className="h-4 w-4 mr-2" />
                  Išsaugoti ir tęsti (Enter)
                </Button>
                <Button variant="outline" onClick={skipWork}>
                  <SkipForward className="h-4 w-4 mr-2" />
                  Praleisti (S)
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Shortcuts modal */}
      {showShortcuts && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowShortcuts(false)}
        >
          <Card className="w-96" onClick={(e) => e.stopPropagation()}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Keyboard className="h-5 w-5" />
                Klaviatūros spartieji klavišai
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div className="flex justify-between p-2 bg-muted rounded">
                  <span>Ankstesnis</span>
                  <kbd className="px-2 py-0.5 bg-background rounded border">
                    ←
                  </kbd>
                </div>
                <div className="flex justify-between p-2 bg-muted rounded">
                  <span>Kitas</span>
                  <kbd className="px-2 py-0.5 bg-background rounded border">
                    →
                  </kbd>
                </div>
                <div className="flex justify-between p-2 bg-muted rounded">
                  <span>Išsaugoti</span>
                  <kbd className="px-2 py-0.5 bg-background rounded border">
                    Enter
                  </kbd>
                </div>
                <div className="flex justify-between p-2 bg-muted rounded">
                  <span>Praleisti</span>
                  <kbd className="px-2 py-0.5 bg-background rounded border">
                    S
                  </kbd>
                </div>
                <div className="flex justify-between p-2 bg-muted rounded col-span-2">
                  <span>Pažymys 1-9</span>
                  <div className="flex gap-1">
                    <kbd className="px-2 py-0.5 bg-background rounded border">
                      1
                    </kbd>
                    <span>-</span>
                    <kbd className="px-2 py-0.5 bg-background rounded border">
                      9
                    </kbd>
                  </div>
                </div>
                <div className="flex justify-between p-2 bg-muted rounded col-span-2">
                  <span>Pažymys 10</span>
                  <kbd className="px-2 py-0.5 bg-background rounded border">
                    0
                  </kbd>
                </div>
              </div>
              <p className="text-xs text-muted-foreground pt-2">
                Paspauskite{" "}
                <kbd className="px-1 py-0.5 bg-muted rounded border text-xs">
                  ?
                </kbd>{" "}
                bet kuriuo metu norėdami pamatyti šiuos sparčiuosius klavišus.
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
