/**
 * TopicFilter - Temų ir potemių pasirinkimo komponentas
 *
 * Naudojamas kontrolinių generavime - leidžia pasirinkti temas ir potemes
 * iš Lietuvos matematikos bendrosios programos.
 */

import { useState, useEffect, useCallback } from "react";
import { ChevronDown, ChevronRight, Check, Filter, X } from "lucide-react";
import { cn } from "@/lib/utils";

// === Tipai ===
export interface SubtopicData {
  id: string;
  name: string;
  description?: string;
  skills?: string[];
}

export interface TopicData {
  id: string;
  name: string;
  name_en?: string;
  content_area?: string;
  subtopics: SubtopicData[];
}

export interface TopicFilterProps {
  /** Pasirinkta klasė */
  grade: number;
  /** Pasirinktos temos (topic IDs) */
  selectedTopics: string[];
  /** Pasirinktos potemės (subtopic IDs) */
  selectedSubtopics: string[];
  /** Callback kai pasikeičia pasirinktos temos */
  onTopicsChange: (topicIds: string[]) => void;
  /** Callback kai pasikeičia pasirinktos potemės */
  onSubtopicsChange: (subtopicIds: string[]) => void;
  /** Ar rodyti tik pažymėtas */
  showOnlySelected?: boolean;
  /** Klasės pavadinimas CSS */
  className?: string;
}

// === API funkcijos ===
async function fetchCurriculumTopics(grade: number): Promise<TopicData[]> {
  try {
    const response = await fetch(`/api/tests/curriculum/topics/${grade}`);
    if (!response.ok) {
      throw new Error("Failed to fetch curriculum topics");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching curriculum topics:", error);
    return [];
  }
}

// === Komponentas ===
export function TopicFilter({
  grade,
  selectedTopics,
  selectedSubtopics,
  onTopicsChange,
  onSubtopicsChange,
  showOnlySelected = false,
  className,
}: TopicFilterProps) {
  const [topics, setTopics] = useState<TopicData[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");

  // Užkrauti temas kai pasikeičia klasė
  useEffect(() => {
    const loadTopics = async () => {
      setLoading(true);
      const data = await fetchCurriculumTopics(grade);
      setTopics(data);
      setLoading(false);
    };
    loadTopics();
  }, [grade]);

  // Išskleisti/suskleisti temą
  const toggleTopicExpanded = useCallback((topicId: string) => {
    setExpandedTopics((prev) => {
      const next = new Set(prev);
      if (next.has(topicId)) {
        next.delete(topicId);
      } else {
        next.add(topicId);
      }
      return next;
    });
  }, []);

  // Pasirinkti/atžymėti temą (su visomis potemėmis)
  const toggleTopic = useCallback(
    (topic: TopicData) => {
      const isSelected = selectedTopics.includes(topic.id);
      const subtopicIds = topic.subtopics.map((st) => st.id);

      if (isSelected) {
        // Atžymėti temą ir visas potemes
        onTopicsChange(selectedTopics.filter((id) => id !== topic.id));
        onSubtopicsChange(
          selectedSubtopics.filter((id) => !subtopicIds.includes(id)),
        );
      } else {
        // Pasirinkti temą ir visas potemes
        onTopicsChange([...selectedTopics, topic.id]);
        onSubtopicsChange([
          ...selectedSubtopics,
          ...subtopicIds.filter((id) => !selectedSubtopics.includes(id)),
        ]);
        // Automatiškai išskleisti
        setExpandedTopics((prev) => new Set([...prev, topic.id]));
      }
    },
    [selectedTopics, selectedSubtopics, onTopicsChange, onSubtopicsChange],
  );

  // Pasirinkti/atžymėti potemę
  const toggleSubtopic = useCallback(
    (topicId: string, subtopicId: string, topic: TopicData) => {
      const isSelected = selectedSubtopics.includes(subtopicId);
      const subtopicIds = topic.subtopics.map((st) => st.id);

      if (isSelected) {
        // Atžymėti potemę
        const newSubtopics = selectedSubtopics.filter(
          (id) => id !== subtopicId,
        );
        onSubtopicsChange(newSubtopics);

        // Jei nebeliko nė vienos potemės iš temos - atžymėti ir temą
        const hasAnySubtopic = subtopicIds.some((id) =>
          newSubtopics.includes(id),
        );
        if (!hasAnySubtopic) {
          onTopicsChange(selectedTopics.filter((id) => id !== topicId));
        }
      } else {
        // Pasirinkti potemę
        onSubtopicsChange([...selectedSubtopics, subtopicId]);

        // Automatiškai pažymėti temą jei dar nepažymėta
        if (!selectedTopics.includes(topicId)) {
          onTopicsChange([...selectedTopics, topicId]);
        }
      }
    },
    [selectedTopics, selectedSubtopics, onTopicsChange, onSubtopicsChange],
  );

  // Išvalyti viską
  const clearAll = useCallback(() => {
    onTopicsChange([]);
    onSubtopicsChange([]);
  }, [onTopicsChange, onSubtopicsChange]);

  // Pasirinkti viską
  const selectAll = useCallback(() => {
    const allTopicIds = topics.map((t) => t.id);
    const allSubtopicIds = topics.flatMap((t) =>
      t.subtopics.map((st) => st.id),
    );
    onTopicsChange(allTopicIds);
    onSubtopicsChange(allSubtopicIds);
    setExpandedTopics(new Set(allTopicIds));
  }, [topics, onTopicsChange, onSubtopicsChange]);

  // Filtruoti pagal paiešką
  const filteredTopics = topics.filter((topic) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      topic.name.toLowerCase().includes(query) ||
      topic.subtopics.some((st) => st.name.toLowerCase().includes(query))
    );
  });

  // Rodyti tik pasirinktas
  const displayTopics = showOnlySelected
    ? filteredTopics.filter(
        (t) =>
          selectedTopics.includes(t.id) ||
          t.subtopics.some((st) => selectedSubtopics.includes(st.id)),
      )
    : filteredTopics;

  if (loading) {
    return (
      <div className={cn("p-4 text-center text-gray-500", className)}>
        <div className="animate-spin inline-block w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full mr-2" />
        Kraunamos temos...
      </div>
    );
  }

  const selectedCount = selectedSubtopics.length;

  return (
    <div className={cn("space-y-3", className)}>
      {/* Antraštė ir veiksmai */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="font-medium text-sm">Temos ir potemės</span>
          {selectedCount > 0 && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              {selectedCount} pasirinkta
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
        <input
          type="text"
          placeholder="Ieškoti temų..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

      {/* Temų sąrašas */}
      <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg divide-y">
        {displayTopics.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            {searchQuery
              ? "Nerasta temų pagal paiešką"
              : "Nėra temų šiai klasei"}
          </div>
        ) : (
          displayTopics.map((topic) => {
            const isTopicSelected = selectedTopics.includes(topic.id);
            const isExpanded = expandedTopics.has(topic.id);
            const selectedSubtopicCount = topic.subtopics.filter((st) =>
              selectedSubtopics.includes(st.id),
            ).length;
            const allSubtopicsSelected =
              selectedSubtopicCount === topic.subtopics.length;
            const someSubtopicsSelected =
              selectedSubtopicCount > 0 && !allSubtopicsSelected;

            return (
              <div key={topic.id} className="bg-white">
                {/* Temos eilutė */}
                <div
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer",
                    isTopicSelected && "bg-blue-50",
                  )}
                >
                  {/* Išskleidimo mygtukas */}
                  <button
                    onClick={() => toggleTopicExpanded(topic.id)}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    )}
                  </button>

                  {/* Checkbox */}
                  <button
                    onClick={() => toggleTopic(topic)}
                    className={cn(
                      "w-5 h-5 rounded border-2 flex items-center justify-center transition-colors",
                      allSubtopicsSelected
                        ? "bg-blue-500 border-blue-500"
                        : someSubtopicsSelected
                          ? "bg-blue-200 border-blue-400"
                          : "border-gray-300 hover:border-blue-400",
                    )}
                  >
                    {(allSubtopicsSelected || someSubtopicsSelected) && (
                      <Check
                        className={cn(
                          "w-3 h-3",
                          allSubtopicsSelected ? "text-white" : "text-blue-600",
                        )}
                      />
                    )}
                  </button>

                  {/* Temos pavadinimas */}
                  <span
                    className="flex-1 text-sm font-medium cursor-pointer"
                    onClick={() => toggleTopicExpanded(topic.id)}
                  >
                    {topic.name}
                  </span>

                  {/* Potemių skaičius */}
                  <span className="text-xs text-gray-400">
                    {selectedSubtopicCount}/{topic.subtopics.length}
                  </span>
                </div>

                {/* Potemės (išskleidžiamos) */}
                {isExpanded && topic.subtopics.length > 0 && (
                  <div className="bg-gray-50 border-t border-gray-100">
                    {topic.subtopics.map((subtopic) => {
                      const isSubtopicSelected = selectedSubtopics.includes(
                        subtopic.id,
                      );

                      return (
                        <div
                          key={subtopic.id}
                          className={cn(
                            "flex items-center gap-2 pl-10 pr-3 py-2 hover:bg-gray-100 cursor-pointer",
                            isSubtopicSelected && "bg-blue-50",
                          )}
                          onClick={() =>
                            toggleSubtopic(topic.id, subtopic.id, topic)
                          }
                        >
                          {/* Checkbox */}
                          <div
                            className={cn(
                              "w-4 h-4 rounded border-2 flex items-center justify-center transition-colors",
                              isSubtopicSelected
                                ? "bg-blue-500 border-blue-500"
                                : "border-gray-300",
                            )}
                          >
                            {isSubtopicSelected && (
                              <Check className="w-3 h-3 text-white" />
                            )}
                          </div>

                          {/* Potemės pavadinimas */}
                          <div className="flex-1">
                            <span className="text-sm text-gray-700">
                              {subtopic.name}
                            </span>
                            {subtopic.description && (
                              <p className="text-xs text-gray-400 mt-0.5">
                                {subtopic.description}
                              </p>
                            )}
                          </div>

                          {/* Įgūdžiai (jei yra) */}
                          {subtopic.skills && subtopic.skills.length > 0 && (
                            <span className="text-xs text-gray-400">
                              {subtopic.skills.length} įgūdžiai
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Pasirinkimų santrauka */}
      {selectedCount > 0 && (
        <div className="text-xs text-gray-500">
          Pasirinkta: {selectedTopics.length} temų, {selectedSubtopics.length}{" "}
          potemių
        </div>
      )}
    </div>
  );
}

export default TopicFilter;
