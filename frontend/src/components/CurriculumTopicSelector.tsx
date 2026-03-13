/**
 * CurriculumTopicSelector - Temų pasirinkimas iš matematikos programos
 *
 * Rodo temas sugrupuotas pagal klases su išskleidžiamais potemėmis.
 * Kiekviena potemė turi difficulty_rules (EASY/MEDIUM/HARD) aprašymus.
 *
 * Kumuliacinė logika: 8 kl. pasirinkimas rodo 5+6+7+8 kl. temas.
 */

import { useState, useEffect, useCallback, useMemo } from "react";
import {
  ChevronDown,
  ChevronRight,
  Check,
  BookOpen,
  X,
  Search,
  Info,
} from "lucide-react";
import { cn } from "@/lib/utils";

// === Tipai ===
interface DifficultyRules {
  EASY: string;
  MEDIUM: string;
  HARD: string;
}

interface Subtopic {
  id: string;
  name: string;
  source_grade: number;
  difficulty_rules: DifficultyRules;
}

interface Topic {
  id: string;
  title: string;
  source_grade: number;
  subtopics: Subtopic[];
}

interface GradeTopics {
  [gradeStr: string]: Topic[];
}

interface ProgramResponse {
  grade: number;
  available_grades: number[];
  grades: GradeTopics;
}

export interface CurriculumTopicSelectorProps {
  /** Pasirinkta klasė */
  grade: number;
  /** Pasirinktos temos (topic IDs) */
  selectedTopics: string[];
  /** Pasirinktos potemės (subtopic IDs) */
  selectedSubtopics: string[];
  /** Pasirinktas sunkumo lygis */
  difficulty: string;
  /** Callback kai pasikeičia temos */
  onTopicsChange: (topicIds: string[]) => void;
  /** Callback kai pasikeičia potemės */
  onSubtopicsChange: (subtopicIds: string[]) => void;
  /** CSS klasė */
  className?: string;
}

// === Difficulty spalvos ===
const DIFFICULTY_COLORS: Record<string, string> = {
  EASY: "text-green-700 bg-green-50 border-green-200",
  MEDIUM: "text-amber-700 bg-amber-50 border-amber-200",
  HARD: "text-red-700 bg-red-50 border-red-200",
};

const DIFFICULTY_LABELS: Record<string, string> = {
  EASY: "Lengvas",
  MEDIUM: "Vidutinis",
  HARD: "Sudėtingas",
};

// === API ===
async function fetchProgramTopics(
  grade: number,
): Promise<ProgramResponse | null> {
  try {
    const response = await fetch(`/api/v1/tests/program/topics/${grade}`);
    if (!response.ok) throw new Error("Failed to fetch");
    return await response.json();
  } catch (error) {
    console.error("Klaida kraunant programos temas:", error);
    return null;
  }
}

// === Komponentas ===
export function CurriculumTopicSelector({
  grade,
  selectedTopics,
  selectedSubtopics,
  difficulty,
  onTopicsChange,
  onSubtopicsChange,
  className,
}: CurriculumTopicSelectorProps) {
  const [programData, setProgramData] = useState<ProgramResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedGrades, setExpandedGrades] = useState<Set<number>>(new Set());
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set());
  const [expandedSubtopics, setExpandedSubtopics] = useState<Set<string>>(
    new Set(),
  );
  const [searchQuery, setSearchQuery] = useState("");

  // Užkrauti temas kai pasikeičia klasė
  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const data = await fetchProgramTopics(grade);
      setProgramData(data);
      setLoading(false);

      // Automatiškai išskleisti dabartinę klasę
      if (data) {
        setExpandedGrades(new Set([grade]));
      }
    };
    load();
  }, [grade]);

  // Difficulty key mapinimas
  const difficultyKey = useMemo(() => {
    const map: Record<string, string> = {
      easy: "EASY",
      medium: "MEDIUM",
      hard: "HARD",
      mixed: "MEDIUM",
      vbe: "HARD",
    };
    return map[difficulty] || "MEDIUM";
  }, [difficulty]);

  // Filtruotos temos pagal paiešką
  const filteredGrades = useMemo(() => {
    if (!programData?.grades) return {};
    if (!searchQuery) return programData.grades;

    const query = searchQuery.toLowerCase();
    const result: GradeTopics = {};

    for (const [gradeStr, topics] of Object.entries(programData.grades)) {
      const filtered = topics
        .map((topic) => ({
          ...topic,
          subtopics: topic.subtopics.filter(
            (st) =>
              st.name.toLowerCase().includes(query) ||
              topic.title.toLowerCase().includes(query),
          ),
        }))
        .filter((topic) => topic.subtopics.length > 0);

      if (filtered.length > 0) {
        result[gradeStr] = filtered;
      }
    }
    return result;
  }, [programData, searchQuery]);

  // === Pasirinkimo logika ===

  // Pasirinkti/atžymėti visas temos potemes
  const toggleTopic = useCallback(
    (topic: Topic) => {
      const subtopicIds = topic.subtopics.map((st) => st.id);
      const allSelected = subtopicIds.every((id) =>
        selectedSubtopics.includes(id),
      );

      if (allSelected) {
        // Atžymėti
        onSubtopicsChange(
          selectedSubtopics.filter((id) => !subtopicIds.includes(id)),
        );
        onTopicsChange(selectedTopics.filter((id) => id !== topic.id));
      } else {
        // Pažymėti visas
        const newSubtopics = [
          ...selectedSubtopics,
          ...subtopicIds.filter((id) => !selectedSubtopics.includes(id)),
        ];
        onSubtopicsChange(newSubtopics);
        if (!selectedTopics.includes(topic.id)) {
          onTopicsChange([...selectedTopics, topic.id]);
        }
        // Automatiškai išskleisti
        setExpandedTopics((prev) => new Set([...prev, topic.id]));
      }
    },
    [selectedTopics, selectedSubtopics, onTopicsChange, onSubtopicsChange],
  );

  // Pasirinkti/atžymėti vieną potemę
  const toggleSubtopic = useCallback(
    (topic: Topic, subtopicId: string) => {
      const isSelected = selectedSubtopics.includes(subtopicId);
      const subtopicIds = topic.subtopics.map((st) => st.id);

      if (isSelected) {
        const newSubtopics = selectedSubtopics.filter(
          (id) => id !== subtopicId,
        );
        onSubtopicsChange(newSubtopics);
        // Jei nebeliko potemių - atžymėti temą
        if (!subtopicIds.some((id) => newSubtopics.includes(id))) {
          onTopicsChange(selectedTopics.filter((id) => id !== topic.id));
        }
      } else {
        onSubtopicsChange([...selectedSubtopics, subtopicId]);
        if (!selectedTopics.includes(topic.id)) {
          onTopicsChange([...selectedTopics, topic.id]);
        }
      }
    },
    [selectedTopics, selectedSubtopics, onTopicsChange, onSubtopicsChange],
  );

  // Pasirinkti visos klasės temas
  const toggleGradeAll = useCallback(
    (gradeStr: string) => {
      const topics = programData?.grades[gradeStr] || [];
      const allSubIds = topics.flatMap((t) => t.subtopics.map((st) => st.id));
      const allTopicIds = topics.map((t) => t.id);
      const allSelected = allSubIds.every((id) =>
        selectedSubtopics.includes(id),
      );

      if (allSelected) {
        onSubtopicsChange(
          selectedSubtopics.filter((id) => !allSubIds.includes(id)),
        );
        onTopicsChange(
          selectedTopics.filter((id) => !allTopicIds.includes(id)),
        );
      } else {
        onSubtopicsChange([
          ...selectedSubtopics,
          ...allSubIds.filter((id) => !selectedSubtopics.includes(id)),
        ]);
        onTopicsChange([
          ...selectedTopics,
          ...allTopicIds.filter((id) => !selectedTopics.includes(id)),
        ]);
      }
    },
    [
      programData,
      selectedTopics,
      selectedSubtopics,
      onTopicsChange,
      onSubtopicsChange,
    ],
  );

  // Pasirinkti viską
  const selectAll = useCallback(() => {
    if (!programData?.grades) return;
    const allTopicIds: string[] = [];
    const allSubIds: string[] = [];
    for (const topics of Object.values(programData.grades)) {
      for (const topic of topics) {
        allTopicIds.push(topic.id);
        for (const st of topic.subtopics) {
          allSubIds.push(st.id);
        }
      }
    }
    onTopicsChange(allTopicIds);
    onSubtopicsChange(allSubIds);
  }, [programData, onTopicsChange, onSubtopicsChange]);

  // Išvalyti viską
  const clearAll = useCallback(() => {
    onTopicsChange([]);
    onSubtopicsChange([]);
  }, [onTopicsChange, onSubtopicsChange]);

  // Toggle expand
  const toggleGradeExpanded = useCallback((g: number) => {
    setExpandedGrades((prev) => {
      const next = new Set(prev);
      if (next.has(g)) next.delete(g);
      else next.add(g);
      return next;
    });
  }, []);

  const toggleTopicExpanded = useCallback((topicId: string) => {
    setExpandedTopics((prev) => {
      const next = new Set(prev);
      if (next.has(topicId)) next.delete(topicId);
      else next.add(topicId);
      return next;
    });
  }, []);

  const toggleSubtopicInfo = useCallback((subtopicId: string) => {
    setExpandedSubtopics((prev) => {
      const next = new Set(prev);
      if (next.has(subtopicId)) next.delete(subtopicId);
      else next.add(subtopicId);
      return next;
    });
  }, []);

  // Statistikos
  const totalSubtopics = useMemo(() => {
    if (!programData?.grades) return 0;
    let count = 0;
    for (const topics of Object.values(programData.grades)) {
      for (const topic of topics) {
        count += topic.subtopics.length;
      }
    }
    return count;
  }, [programData]);

  // === Render ===

  if (loading) {
    return (
      <div className={cn("p-4 text-center text-gray-500", className)}>
        <div className="animate-spin inline-block w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full mr-2" />
        Kraunamos programos temos...
      </div>
    );
  }

  if (!programData || Object.keys(filteredGrades).length === 0) {
    return (
      <div className={cn("p-4 text-center text-gray-500", className)}>
        {searchQuery ? "Nerasta temų pagal paiešką" : "Nėra temų šiai klasei"}
      </div>
    );
  }

  const gradeEntries = Object.entries(filteredGrades).sort(
    ([a], [b]) => Number(a) - Number(b),
  );

  return (
    <div className={cn("space-y-3", className)}>
      {/* Antraštė ir veiksmai */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-blue-500" />
          <span className="font-medium text-sm">Programos temos</span>
          {selectedSubtopics.length > 0 && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              {selectedSubtopics.length}/{totalSubtopics}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={selectAll}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Visos
          </button>
          <button
            onClick={clearAll}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Išvalyti
          </button>
        </div>
      </div>

      {/* Paieška */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Ieškoti temų..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-8 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery("")}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Temų sąrašas pagal klases */}
      <div className="max-h-[500px] overflow-y-auto border border-gray-200 rounded-lg">
        {gradeEntries.map(([gradeStr, topics]) => {
          const g = Number(gradeStr);
          const isGradeExpanded = expandedGrades.has(g);
          const gradeSubIds = topics.flatMap((t) =>
            t.subtopics.map((st) => st.id),
          );
          const selectedInGrade = gradeSubIds.filter((id) =>
            selectedSubtopics.includes(id),
          ).length;
          const allGradeSelected =
            selectedInGrade === gradeSubIds.length && gradeSubIds.length > 0;
          const someGradeSelected = selectedInGrade > 0 && !allGradeSelected;
          const isCurrentGrade = g === grade;

          return (
            <div
              key={gradeStr}
              className="border-b border-gray-200 last:border-b-0"
            >
              {/* Klasės antraštė */}
              <div
                className={cn(
                  "flex items-center gap-2 px-3 py-2.5 cursor-pointer transition-colors",
                  isCurrentGrade
                    ? "bg-blue-50 hover:bg-blue-100"
                    : "bg-gray-50 hover:bg-gray-100",
                )}
              >
                <button
                  onClick={() => toggleGradeExpanded(g)}
                  className="p-0.5"
                >
                  {isGradeExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-500" />
                  )}
                </button>

                {/* Klasės checkbox */}
                <button
                  onClick={() => toggleGradeAll(gradeStr)}
                  className={cn(
                    "w-5 h-5 rounded border-2 flex items-center justify-center transition-colors",
                    allGradeSelected
                      ? "bg-blue-500 border-blue-500"
                      : someGradeSelected
                        ? "bg-blue-200 border-blue-400"
                        : "border-gray-300 hover:border-blue-400",
                  )}
                >
                  {(allGradeSelected || someGradeSelected) && (
                    <Check
                      className={cn(
                        "w-3 h-3",
                        allGradeSelected ? "text-white" : "text-blue-600",
                      )}
                    />
                  )}
                </button>

                {/* Klasės pavadinimas */}
                <span
                  className={cn(
                    "flex-1 text-sm font-semibold cursor-pointer",
                    isCurrentGrade ? "text-blue-800" : "text-gray-700",
                  )}
                  onClick={() => toggleGradeExpanded(g)}
                >
                  {g} klasė
                  {isCurrentGrade && (
                    <span className="ml-2 text-xs font-normal text-blue-600">
                      (dabartinė)
                    </span>
                  )}
                </span>

                {/* Statistika */}
                <span className="text-xs text-gray-400">
                  {selectedInGrade}/{gradeSubIds.length}
                </span>
              </div>

              {/* Temos (išskleidžiamos) */}
              {isGradeExpanded && (
                <div>
                  {topics.map((topic) => {
                    const isTopicExpanded = expandedTopics.has(topic.id);
                    const topicSubIds = topic.subtopics.map((st) => st.id);
                    const selectedSubCount = topicSubIds.filter((id) =>
                      selectedSubtopics.includes(id),
                    ).length;
                    const allSubSelected =
                      selectedSubCount === topicSubIds.length &&
                      topicSubIds.length > 0;
                    const someSubSelected =
                      selectedSubCount > 0 && !allSubSelected;

                    return (
                      <div key={topic.id}>
                        {/* Temos eilutė */}
                        <div
                          className={cn(
                            "flex items-center gap-2 pl-6 pr-3 py-2 border-t border-gray-100",
                            "hover:bg-gray-50 cursor-pointer",
                            allSubSelected && "bg-blue-50/50",
                          )}
                        >
                          <button
                            onClick={() => toggleTopicExpanded(topic.id)}
                            className="p-0.5"
                          >
                            {isTopicExpanded ? (
                              <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
                            ) : (
                              <ChevronRight className="w-3.5 h-3.5 text-gray-400" />
                            )}
                          </button>

                          <button
                            onClick={() => toggleTopic(topic)}
                            className={cn(
                              "w-4.5 h-4.5 rounded border-2 flex items-center justify-center transition-colors",
                              allSubSelected
                                ? "bg-blue-500 border-blue-500"
                                : someSubSelected
                                  ? "bg-blue-200 border-blue-400"
                                  : "border-gray-300 hover:border-blue-400",
                            )}
                          >
                            {(allSubSelected || someSubSelected) && (
                              <Check
                                className={cn(
                                  "w-2.5 h-2.5",
                                  allSubSelected
                                    ? "text-white"
                                    : "text-blue-600",
                                )}
                              />
                            )}
                          </button>

                          <span
                            className="flex-1 text-sm font-medium text-gray-800 cursor-pointer"
                            onClick={() => toggleTopicExpanded(topic.id)}
                          >
                            {topic.title}
                          </span>

                          <span className="text-xs text-gray-400">
                            {selectedSubCount}/{topic.subtopics.length}
                          </span>
                        </div>

                        {/* Potemės (išskleidžiamos) */}
                        {isTopicExpanded && (
                          <div className="bg-gray-50/50">
                            {topic.subtopics.map((subtopic) => {
                              const isSubSelected = selectedSubtopics.includes(
                                subtopic.id,
                              );
                              const isInfoExpanded = expandedSubtopics.has(
                                subtopic.id,
                              );

                              return (
                                <div key={subtopic.id}>
                                  {/* Potemės eilutė */}
                                  <div
                                    className={cn(
                                      "flex items-center gap-2 pl-12 pr-3 py-1.5",
                                      "hover:bg-gray-100 transition-colors",
                                      isSubSelected && "bg-blue-50",
                                    )}
                                  >
                                    {/* Checkbox */}
                                    <button
                                      onClick={() =>
                                        toggleSubtopic(topic, subtopic.id)
                                      }
                                      className={cn(
                                        "w-4 h-4 rounded border-2 flex items-center justify-center transition-colors flex-shrink-0",
                                        isSubSelected
                                          ? "bg-blue-500 border-blue-500"
                                          : "border-gray-300 hover:border-blue-400",
                                      )}
                                    >
                                      {isSubSelected && (
                                        <Check className="w-2.5 h-2.5 text-white" />
                                      )}
                                    </button>

                                    {/* Pavadinimas */}
                                    <span
                                      className="flex-1 text-sm text-gray-700 cursor-pointer"
                                      onClick={() =>
                                        toggleSubtopic(topic, subtopic.id)
                                      }
                                    >
                                      {subtopic.name}
                                    </span>

                                    {/* Info mygtukas */}
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        toggleSubtopicInfo(subtopic.id);
                                      }}
                                      className={cn(
                                        "p-1 rounded transition-colors flex-shrink-0",
                                        isInfoExpanded
                                          ? "bg-blue-100 text-blue-600"
                                          : "text-gray-400 hover:text-blue-500 hover:bg-gray-200",
                                      )}
                                      title="Rodyti sunkumo lygius"
                                    >
                                      <Info className="w-3.5 h-3.5" />
                                    </button>
                                  </div>

                                  {/* Difficulty rules (išskleidžiamos) */}
                                  {isInfoExpanded &&
                                    subtopic.difficulty_rules && (
                                      <div className="pl-16 pr-3 pb-2 space-y-1.5">
                                        {(
                                          ["EASY", "MEDIUM", "HARD"] as const
                                        ).map((level) => {
                                          const text =
                                            subtopic.difficulty_rules[level];
                                          if (!text) return null;
                                          const isActive =
                                            difficultyKey === level;
                                          return (
                                            <div
                                              key={level}
                                              className={cn(
                                                "text-xs p-2 rounded border",
                                                isActive
                                                  ? DIFFICULTY_COLORS[level] +
                                                      " ring-1 ring-current font-medium"
                                                  : "border-gray-200 text-gray-500 bg-white",
                                              )}
                                            >
                                              <span className="font-semibold">
                                                {DIFFICULTY_LABELS[level]}:
                                              </span>{" "}
                                              {text}
                                            </div>
                                          );
                                        })}
                                      </div>
                                    )}
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Pasirinkimų santrauka */}
      {selectedSubtopics.length > 0 && (
        <div className="text-xs text-gray-500 flex items-center justify-between">
          <span>
            Pasirinkta: {selectedTopics.length} temų, {selectedSubtopics.length}{" "}
            potemių
          </span>
          <span className="text-blue-600">
            Sunkumas: {DIFFICULTY_LABELS[difficultyKey] || "Vidutinis"}
          </span>
        </div>
      )}
    </div>
  );
}

export default CurriculumTopicSelector;
