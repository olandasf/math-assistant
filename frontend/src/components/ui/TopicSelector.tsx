/**
 * TopicSelector - Temų pasirinkimo komponentas
 * Leidžia pasirinkti matematikos temą užduotims
 */

import { useState, useMemo } from "react";
import { Check, ChevronDown, Search, BookOpen } from "lucide-react";
import { Button, Input, Badge } from "@/components/ui";
import { cn } from "@/lib/utils";

// Temų tipai
export interface Topic {
  id: string;
  name: string;
  category: string;
  category_name?: string;
  grade_levels: number[];
}

export interface TopicCategory {
  name: string;
  topics: Topic[];
}

// Statiniai temų duomenys (iš backend)
const TOPIC_DATA: Record<string, TopicCategory> = {
  arithmetic: {
    name: "Aritmetika",
    topics: [
      {
        id: "natural_numbers",
        name: "Natūralieji skaičiai",
        category: "arithmetic",
        grade_levels: [5, 6],
      },
      {
        id: "integers",
        name: "Sveikieji skaičiai",
        category: "arithmetic",
        grade_levels: [6, 7],
      },
      {
        id: "fractions",
        name: "Trupmenos",
        category: "arithmetic",
        grade_levels: [5, 6, 7],
      },
      {
        id: "decimals",
        name: "Dešimtainės trupmenos",
        category: "arithmetic",
        grade_levels: [5, 6],
      },
      {
        id: "percentages",
        name: "Procentai",
        category: "arithmetic",
        grade_levels: [6, 7, 8],
      },
      {
        id: "ratios",
        name: "Santykiai ir proporcijos",
        category: "arithmetic",
        grade_levels: [6, 7, 8],
      },
      {
        id: "powers",
        name: "Laipsniai",
        category: "arithmetic",
        grade_levels: [7, 8],
      },
      {
        id: "roots",
        name: "Šaknys",
        category: "arithmetic",
        grade_levels: [8],
      },
    ],
  },
  algebra: {
    name: "Algebra",
    topics: [
      {
        id: "expressions",
        name: "Reiškiniai",
        category: "algebra",
        grade_levels: [6, 7, 8],
      },
      {
        id: "linear_equations",
        name: "Tiesinės lygtys",
        category: "algebra",
        grade_levels: [6, 7, 8],
      },
      {
        id: "quadratic_equations",
        name: "Kvadratinės lygtys",
        category: "algebra",
        grade_levels: [8, 10],
      },
      {
        id: "inequalities",
        name: "Nelygybės",
        category: "algebra",
        grade_levels: [7, 8],
      },
      {
        id: "equation_systems",
        name: "Lygčių sistemos",
        category: "algebra",
        grade_levels: [8, 10],
      },
      {
        id: "functions",
        name: "Funkcijos",
        category: "algebra",
        grade_levels: [8, 10],
      },
      {
        id: "sequences",
        name: "Sekos",
        category: "algebra",
        grade_levels: [8, 10],
      },
      {
        id: "polynomials",
        name: "Daugianariai",
        category: "algebra",
        grade_levels: [7, 8],
      },
    ],
  },
  geometry: {
    name: "Geometrija",
    topics: [
      {
        id: "basic_shapes",
        name: "Pagrindinės figūros",
        category: "geometry",
        grade_levels: [5, 6],
      },
      {
        id: "angles",
        name: "Kampai",
        category: "geometry",
        grade_levels: [5, 6, 7],
      },
      {
        id: "triangles",
        name: "Trikampiai",
        category: "geometry",
        grade_levels: [6, 7, 8],
      },
      {
        id: "quadrilaterals",
        name: "Keturkampiai",
        category: "geometry",
        grade_levels: [6, 7, 8],
      },
      {
        id: "circles",
        name: "Apskritimai",
        category: "geometry",
        grade_levels: [6, 7, 8],
      },
      {
        id: "perimeter_area",
        name: "Perimetras ir plotas",
        category: "geometry",
        grade_levels: [5, 6, 7, 8],
      },
      {
        id: "volume",
        name: "Tūris",
        category: "geometry",
        grade_levels: [6, 7, 8],
      },
      {
        id: "coordinate_geometry",
        name: "Koordinatės",
        category: "geometry",
        grade_levels: [7, 8],
      },
      {
        id: "transformations",
        name: "Transformacijos",
        category: "geometry",
        grade_levels: [7, 8],
      },
      {
        id: "pythagorean",
        name: "Pitagoro teorema",
        category: "geometry",
        grade_levels: [8],
      },
    ],
  },
  statistics: {
    name: "Statistika ir tikimybės",
    topics: [
      {
        id: "data_analysis",
        name: "Duomenų analizė",
        category: "statistics",
        grade_levels: [5, 6, 7, 8],
      },
      {
        id: "mean_median",
        name: "Vidurkis ir mediana",
        category: "statistics",
        grade_levels: [6, 7, 8],
      },
      {
        id: "probability",
        name: "Tikimybės",
        category: "statistics",
        grade_levels: [7, 8],
      },
      {
        id: "graphs_charts",
        name: "Grafikai ir diagramos",
        category: "statistics",
        grade_levels: [5, 6, 7, 8],
      },
    ],
  },
  other: {
    name: "Kita",
    topics: [
      {
        id: "word_problems",
        name: "Tekstiniai uždaviniai",
        category: "other",
        grade_levels: [5, 6, 7, 8],
      },
      {
        id: "units_conversion",
        name: "Matų vienetai",
        category: "other",
        grade_levels: [5, 6, 7],
      },
      {
        id: "money",
        name: "Pinigai ir sąskaitos",
        category: "other",
        grade_levels: [5, 6],
      },
      { id: "time", name: "Laikas", category: "other", grade_levels: [5, 6] },
    ],
  },
};

// Spalvos kategorijoms
const CATEGORY_COLORS: Record<string, string> = {
  arithmetic: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  algebra:
    "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  geometry: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  statistics:
    "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  other: "bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200",
};

interface TopicSelectorProps {
  /** Pasirinkta tema */
  value?: string;
  /** Callback kai pasirenkama tema */
  onChange: (topicId: string | undefined) => void;
  /** Filtruoti pagal klasę */
  gradeFilter?: number;
  /** Ar galima pasirinkti kelias temas */
  multiple?: boolean;
  /** Pasirinktos temos (jei multiple) */
  values?: string[];
  /** Callback kelioms temoms */
  onMultiChange?: (topicIds: string[]) => void;
  /** Placeholder tekstas */
  placeholder?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Papildoma CSS klasė */
  className?: string;
}

export function TopicSelector({
  value,
  onChange,
  gradeFilter,
  multiple = false,
  values = [],
  onMultiChange,
  placeholder = "Pasirinkite temą...",
  disabled = false,
  className,
}: TopicSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Filtruoti temas pagal paiešką ir klasę
  const filteredData = useMemo(() => {
    const result: Record<string, TopicCategory> = {};

    Object.entries(TOPIC_DATA).forEach(([categoryId, category]) => {
      const filteredTopics = category.topics.filter((topic) => {
        // Filtras pagal klasę
        if (gradeFilter && !topic.grade_levels.includes(gradeFilter)) {
          return false;
        }
        // Filtras pagal paiešką
        if (searchQuery) {
          return topic.name.toLowerCase().includes(searchQuery.toLowerCase());
        }
        return true;
      });

      if (filteredTopics.length > 0) {
        result[categoryId] = {
          name: category.name,
          topics: filteredTopics,
        };
      }
    });

    return result;
  }, [gradeFilter, searchQuery]);

  // Gauti pasirinktą temą
  const selectedTopic = useMemo(() => {
    if (!value) return null;
    for (const category of Object.values(TOPIC_DATA)) {
      const found = category.topics.find((t) => t.id === value);
      if (found) return found;
    }
    return null;
  }, [value]);

  // Gauti pasirinktas temas (multi mode)
  const selectedTopics = useMemo(() => {
    if (!multiple) return [];
    const topics: Topic[] = [];
    values.forEach((v) => {
      for (const category of Object.values(TOPIC_DATA)) {
        const found = category.topics.find((t) => t.id === v);
        if (found) {
          topics.push(found);
          break;
        }
      }
    });
    return topics;
  }, [values, multiple]);

  const handleSelect = (topicId: string) => {
    if (multiple && onMultiChange) {
      if (values.includes(topicId)) {
        onMultiChange(values.filter((v) => v !== topicId));
      } else {
        onMultiChange([...values, topicId]);
      }
    } else {
      onChange(topicId);
      setIsOpen(false);
    }
  };

  const handleClear = () => {
    if (multiple && onMultiChange) {
      onMultiChange([]);
    } else {
      onChange(undefined);
    }
  };

  return (
    <div className={cn("relative", className)}>
      {/* Trigger button */}
      <Button
        type="button"
        variant="outline"
        role="combobox"
        aria-expanded={isOpen}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className="w-full justify-between font-normal"
      >
        {multiple ? (
          selectedTopics.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {selectedTopics.slice(0, 2).map((t) => (
                <Badge key={t.id} variant="secondary" className="text-xs">
                  {t.name}
                </Badge>
              ))}
              {selectedTopics.length > 2 && (
                <Badge variant="secondary" className="text-xs">
                  +{selectedTopics.length - 2}
                </Badge>
              )}
            </div>
          ) : (
            <span className="text-muted-foreground">{placeholder}</span>
          )
        ) : selectedTopic ? (
          <div className="flex items-center gap-2">
            <Badge
              className={cn("text-xs", CATEGORY_COLORS[selectedTopic.category])}
            >
              {TOPIC_DATA[selectedTopic.category]?.name}
            </Badge>
            <span>{selectedTopic.name}</span>
          </div>
        ) : (
          <span className="text-muted-foreground">{placeholder}</span>
        )}
        <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </Button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full min-w-[300px] rounded-md border bg-popover shadow-lg">
          {/* Search */}
          <div className="p-2 border-b">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Ieškoti temos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
                autoFocus
              />
            </div>
          </div>

          {/* Topics list */}
          <div className="max-h-[300px] overflow-y-auto p-2">
            {Object.entries(filteredData).length === 0 ? (
              <div className="text-center py-4 text-muted-foreground">
                <BookOpen className="mx-auto h-8 w-8 mb-2 opacity-50" />
                <p>Temų nerasta</p>
              </div>
            ) : (
              Object.entries(filteredData).map(([categoryId, category]) => (
                <div key={categoryId} className="mb-3 last:mb-0">
                  {/* Category header */}
                  <div className="px-2 py-1 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                    {category.name}
                  </div>

                  {/* Topics in category */}
                  <div className="space-y-0.5">
                    {category.topics.map((topic) => {
                      const isSelected = multiple
                        ? values.includes(topic.id)
                        : value === topic.id;

                      return (
                        <button
                          key={topic.id}
                          type="button"
                          onClick={() => handleSelect(topic.id)}
                          className={cn(
                            "w-full flex items-center justify-between px-2 py-1.5 rounded-md text-sm transition-colors",
                            isSelected
                              ? "bg-primary text-primary-foreground"
                              : "hover:bg-accent"
                          )}
                        >
                          <span>{topic.name}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs opacity-60">
                              {topic.grade_levels.join(", ")} kl.
                            </span>
                            {isSelected && <Check className="h-4 w-4" />}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {(value || (multiple && values.length > 0)) && (
            <div className="p-2 border-t">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="w-full"
              >
                Išvalyti pasirinkimą
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Backdrop to close dropdown */}
      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
      )}
    </div>
  );
}

/**
 * Temos Badge - mažas komponentas temų rodymui
 */
interface TopicBadgeProps {
  topicId: string;
  className?: string;
}

export function TopicBadge({ topicId, className }: TopicBadgeProps) {
  const topic = useMemo(() => {
    for (const category of Object.values(TOPIC_DATA)) {
      const found = category.topics.find((t) => t.id === topicId);
      if (found) return found;
    }
    return null;
  }, [topicId]);

  if (!topic) {
    return (
      <Badge variant="outline" className={className}>
        {topicId}
      </Badge>
    );
  }

  return (
    <Badge className={cn(CATEGORY_COLORS[topic.category], className)}>
      {topic.name}
    </Badge>
  );
}

export default TopicSelector;
