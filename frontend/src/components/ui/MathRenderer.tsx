/**
 * MathRenderer - LaTeX matematikos formuli renderinimo komponentas
 * Naudoja KaTeX biblioteka
 */

console.log("[MathRenderer] FILE LOADED - v6 - improved textToLatex");

import "katex/dist/katex.min.css";
import { InlineMath, BlockMath } from "react-katex";

interface MathRendererProps {
  math: string;
  block?: boolean;
  className?: string;
  errorColor?: string;
}

/**
 * Ištraukia confidence reikšmę iš [conf:X.XX] prefikso
 * Grąžina { confidence, cleanedLine } arba { confidence: null, cleanedLine: originalLine }
 */
function extractConfidence(line: string): {
  confidence: number | null;
  cleanedLine: string;
} {
  const confMatch = line.match(/^\[conf:(\d+\.?\d*)\](.*)/);
  if (confMatch) {
    return {
      confidence: parseFloat(confMatch[1]),
      cleanedLine: confMatch[2].trim(),
    };
  }
  return { confidence: null, cleanedLine: line };
}

/**
 * Grąžina spalvą pagal confidence lygį
 */
function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return "bg-green-100 text-green-700 border-green-300";
  if (confidence >= 0.7) return "bg-blue-100 text-blue-700 border-blue-300";
  if (confidence >= 0.5) return "bg-amber-100 text-amber-700 border-amber-300";
  return "bg-red-100 text-red-700 border-red-300";
}

/**
 * Grąžina ikoną pagal confidence lygį
 */
function getConfidenceIcon(confidence: number): string {
  if (confidence >= 0.9) return "✓";
  if (confidence >= 0.7) return "○";
  return "⚠️";
}

function cleanLatexForKatex(latex: string): string {
  if (!latex) return "";
  let cleaned = latex;
  // Pirmiausia pašaliname [conf:X.XX] prefiksą jei dar liko
  cleaned = cleaned.replace(/^\[conf:\d+\.?\d*\]/, "").trim();
  cleaned = cleaned.replace(/^\$+|\$+$/g, "").trim();
  cleaned = cleaned.replace(/\\textbf\{([^}]*)\}/g, "\\mathbf{$1}");
  cleaned = cleaned.replace(/\\quad/g, "\\;");
  cleaned = cleaned.replace(/\\\\\[[\d.]+em\]/g, "");
  cleaned = cleaned.replace(/\\\\/g, "");
  cleaned = cleaned.replace(/Ats\./g, "\\text{Ats.}");
  cleaned = cleaned.replace(/\[([^\]]+)\]/g, "\\text{[$1]}");
  cleaned = cleaned.replace(/(\d)Ats/g, "$1 \\text{Ats.}");
  return cleaned;
}

function looksLikeLaTeX(text: string): boolean {
  return /\\[a-zA-Z]/.test(text) || /\{.*\}/.test(text);
}

function textToLatex(text: string): string {
  if (!text) return "";
  let latex = text;

  console.log("[textToLatex] Input:", text);

  // Konvertuojame daugybos simbolius
  latex = latex.replace(/\*/g, " \\cdot ");
  latex = latex.replace(/\u00d7/g, " \\cdot ");
  latex = latex.replace(/\u00b7/g, " \\cdot ");
  latex = latex.replace(/\u00f7/g, " \\div ");

  // Konvertuojame dalybos simbolį : į \div (bet ne laiko formatas)
  latex = latex.replace(/(\d)\s*:\s*(\d)/g, "$1 \\div $2");

  // Specialus atvejis: trupmenų dalyba kaip 7/15/(-14/45)
  // Konvertuojame į \frac{7}{15} \div \left(-\frac{14}{45}\right)
  const fractionDivisionMatch = latex.match(
    /^(\d+)\/(\d+)\/\((-?)(\d+)\/(\d+)\)$/,
  );
  if (fractionDivisionMatch) {
    const [, a, b, sign, c, d] = fractionDivisionMatch;
    latex = `\\frac{${a}}{${b}} \\div \\left(${sign}\\frac{${c}}{${d}}\\right)`;
    console.log("[textToLatex] Fraction division detected:", latex);
    return latex;
  }

  // Konvertuojame trupmenas su skliausteliais: (-14/45) -> \left(-\frac{14}{45}\right)
  latex = latex.replace(
    /\(\s*(-?)\s*(\d+)\s*\/\s*(\d+)\s*\)/g,
    (match, sign, num, den) => {
      return `\\left(${sign}\\frac{${num}}{${den}}\\right)`;
    },
  );

  // Konvertuojame paprastas trupmenas: 7/15 -> \frac{7}{15}
  latex = latex.replace(/(\d+)\s*\/\s*(\d+)/g, "\\frac{$1}{$2}");

  console.log("[textToLatex] Output:", latex);

  return latex;
}

export function MathRenderer({
  math,
  block = false,
  className = "",
}: MathRendererProps) {
  // DEBUG: Log what we receive
  console.log(
    "[MathRenderer] Rendering, math length:",
    math?.length,
    "has §§§:",
    math?.includes("§§§"),
  );
  if (math && math.length < 500) {
    console.log("[MathRenderer] Full math:", math);
  }

  if (!math || math.trim() === "") {
    return null;
  }

  // 1. Bandome "§§§" separatoriu
  if (math.includes("\u00a7\u00a7\u00a7")) {
    let lines = math
      .split("\u00a7\u00a7\u00a7")
      .filter((line) => line.trim() !== "");

    // PIRMA: Pašaliname dublikatus pagal task ID
    const seenTaskIds = new Set<string>();
    const uniqueLines: string[] = [];

    for (const line of lines) {
      const trimmedLine = line.trim();
      if (!trimmedLine) continue;

      // Ištraukiame task ID (pvz. "1a", "1b", "2a", "c", "d")
      // SVARBU: Task ID turi būti eilutės pradžioje!
      const taskIdMatch = trimmedLine.match(/^(\d*[a-z]?)\)/i);
      if (taskIdMatch) {
        const taskId = taskIdMatch[1].toLowerCase();
        if (taskId && !seenTaskIds.has(taskId)) {
          seenTaskIds.add(taskId);
          uniqueLines.push(trimmedLine);
        } else if (taskId) {
          console.log(`[MathRenderer] 🗑️ Pašalintas dublikatas: ${taskId}`);
        } else {
          // Tuščias task ID - pridedame
          uniqueLines.push(trimmedLine);
        }
      } else {
        // Nėra task ID formato - pridedame
        uniqueLines.push(trimmedLine);
      }
    }

    console.log(
      `[MathRenderer] §§§ separator: ${lines.length} -> ${uniqueLines.length} unique lines`,
    );

    if (uniqueLines.length > 0) {
      return (
        <div className={className}>
          {uniqueLines.map((line, index) => {
            const { confidence, cleanedLine } = extractConfidence(line);
            return (
              <div
                key={index}
                className="mb-3 pb-2 border-b border-gray-200 last:border-0 flex items-start gap-2"
              >
                {/* Confidence badge */}
                {confidence !== null && (
                  <span
                    className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium border ${getConfidenceColor(
                      confidence,
                    )}`}
                    title={`OCR pasitikėjimas: ${Math.round(
                      confidence * 100,
                    )}%`}
                  >
                    {getConfidenceIcon(confidence)}{" "}
                    {Math.round(confidence * 100)}%
                  </span>
                )}
                <div className="flex-1">
                  <MathLine math={cleanedLine} />
                </div>
              </div>
            );
          })}
        </div>
      );
    }
  }

  // 2. Jei nėra separatoriaus - PROBLEMA! Output neturi separatoriaus.
  // Bandome išskaidyti pagal task ID pattern (bet tai nepatikima)
  console.warn(
    "[MathRenderer] ⚠️ Nėra §§§ separatoriaus! Bandome išskaidyti pagal task ID...",
  );

  // Ieškome task ID kurie prasideda nuo pradžios arba po "Ats."
  // Pattern: pradžia arba po skaičiaus/teksto, tada task ID
  const taskSplitPattern = /(?:^|(?<=Ats\.?\s*-?\d*[½¼¾]?\s*))(\d+[a-z]?\))/gi;
  const parts = math.split(taskSplitPattern).filter((p) => p && p.trim());

  if (parts.length > 1) {
    // Sujungiame task ID su jų turiniu
    const tasks: string[] = [];
    let currentTask = "";

    for (const part of parts) {
      if (/^\d+[a-z]?\)$/i.test(part)) {
        // Tai task ID - pradedame naują task
        if (currentTask) {
          tasks.push(currentTask.trim());
        }
        currentTask = part;
      } else {
        // Tai turinys - pridedame prie dabartinio task
        currentTask += part;
      }
    }
    if (currentTask) {
      tasks.push(currentTask.trim());
    }

    // Pašaliname dublikatus
    const seenIds = new Set<string>();
    const uniqueTasks: string[] = [];

    for (const task of tasks) {
      const idMatch = task.match(/^(\d+[a-z]?)\)/i);
      if (idMatch) {
        const taskId = idMatch[1].toLowerCase();
        if (!seenIds.has(taskId)) {
          seenIds.add(taskId);
          uniqueTasks.push(task);
        } else {
          console.log(
            `[MathRenderer] 🗑️ Pašalintas dublikatas (no sep): ${taskId}`,
          );
        }
      } else {
        uniqueTasks.push(task);
      }
    }

    if (uniqueTasks.length > 0) {
      return (
        <div className={className}>
          {uniqueTasks.map((task, index) => {
            const { confidence, cleanedLine } = extractConfidence(task);
            return (
              <div
                key={index}
                className="mb-3 pb-2 border-b border-gray-200 last:border-0 flex items-start gap-2"
              >
                {/* Confidence badge */}
                {confidence !== null && (
                  <span
                    className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium border ${getConfidenceColor(
                      confidence,
                    )}`}
                    title={`OCR pasitikėjimas: ${Math.round(
                      confidence * 100,
                    )}%`}
                  >
                    {getConfidenceIcon(confidence)}{" "}
                    {Math.round(confidence * 100)}%
                  </span>
                )}
                <div className="flex-1">
                  <MathLine math={cleanedLine} />
                </div>
              </div>
            );
          })}
        </div>
      );
    }
  }

  // 3. Fallback - tiesiog renderuojame kaip yra
  const cleanedMath = removeDuplicateTasks(math);
  return <MathLine math={cleanedMath} block={block} className={className} />;
}

/**
 * Pašalina inline dublikatus iš LaTeX string.
 * Pvz: "1b)23*(-16)=?Ats.-3681b)23*(-16)=?Ats.-368" -> "1b)23*(-16)=?Ats.-368"
 *
 * Taip pat aptinka kai tas pats turinys kartojasi su skirtingais simboliais:
 * "23*(-16)=-368 23·(-16)=-368" -> "23*(-16)=-368"
 */
function removeDuplicateTasks(text: string): string {
  if (!text || text.length < 10) return text;

  // PIRMA: Normalizuojame ir tikriname ar visa eilutė yra dubliuota
  const normalizeForComparison = (s: string): string => {
    return s
      .replace(/·/g, "*")
      .replace(/×/g, "*")
      .replace(/⋅/g, "*")
      .replace(/÷/g, "/")
      .replace(/:/g, "/")
      .replace(/−/g, "-")
      .replace(/–/g, "-")
      .replace(/\s+/g, "")
      .toLowerCase();
  };

  const normalized = normalizeForComparison(text);
  const textLen = normalized.length;

  // Tikriname ar tekstas yra dubliuotas (pirma pusė ≈ antra pusė)
  for (
    let splitPoint = Math.floor(textLen / 2) - 5;
    splitPoint <= Math.floor(textLen / 2) + 10;
    splitPoint++
  ) {
    if (splitPoint <= 5 || splitPoint >= textLen - 5) continue;

    const firstHalf = normalized.slice(0, splitPoint);
    const secondHalf = normalized.slice(splitPoint);

    // Tikriname ar pirmi 15 simbolių sutampa
    const compareLen = Math.min(15, firstHalf.length, secondHalf.length);
    if (compareLen < 10) continue;

    if (firstHalf.slice(0, compareLen) === secondHalf.slice(0, compareLen)) {
      // Rastas dublikatas - grąžiname tik pirmą pusę
      // Randame tikrą padalinimo tašką originaliame tekste
      for (
        let i = Math.floor(text.length / 2) - 10;
        i <= Math.floor(text.length / 2) + 15;
        i++
      ) {
        if (i <= 5 || i >= text.length - 5) continue;

        const origFirst = normalizeForComparison(text.slice(0, i));
        const origSecond = normalizeForComparison(text.slice(i));

        if (
          origFirst.slice(0, compareLen) === origSecond.slice(0, compareLen)
        ) {
          console.log(`[MathRenderer] 🗑️ Pašalintas turinio dublikatas`);
          return text.slice(0, i).trim();
        }
      }
    }
  }

  // ANTRA: Randame visus task ID ir jų pozicijas
  const taskPattern = /(\d+[a-z]?)\)/gi;
  const matches = [...text.matchAll(taskPattern)];

  if (matches.length <= 1) return text;

  // Grupuojame pagal task ID
  const taskOccurrences = new Map<string, { start: number; id: string }[]>();
  for (const match of matches) {
    const taskId = match[1].toLowerCase();
    const start = match.index!;
    if (!taskOccurrences.has(taskId)) {
      taskOccurrences.set(taskId, []);
    }
    taskOccurrences.get(taskId)!.push({ start, id: match[0] });
  }

  // Jei yra dublikatų, pašaliname juos
  let result = text;
  let removed = 0;

  for (const [taskId, occurrences] of taskOccurrences) {
    if (occurrences.length > 1) {
      console.log(
        `[MathRenderer] Rastas dublikatas: ${taskId} (${occurrences.length} kartai)`,
      );

      // Pašaliname visus išskyrus pirmą (nuo galo, kad nepakeistume pozicijų)
      for (let i = occurrences.length - 1; i >= 1; i--) {
        const currentStart = occurrences[i].start - removed;

        // Randame kur baigiasi šis dublikatas (iki kito task arba pabaigos)
        let endPos = result.length;
        for (const [, otherOccs] of taskOccurrences) {
          for (const occ of otherOccs) {
            const adjustedPos = occ.start - removed;
            if (adjustedPos > currentStart && adjustedPos < endPos) {
              endPos = adjustedPos;
            }
          }
        }

        const toRemove = result.slice(currentStart, endPos);
        result = result.slice(0, currentStart) + result.slice(endPos);
        removed += toRemove.length;
        console.log(`[MathRenderer] Pašalinta: "${toRemove.slice(0, 30)}..."`);
      }
    }
  }

  return result;
}

function MathLine({
  math,
  block = false,
  className = "",
}: {
  math: string;
  block?: boolean;
  className?: string;
}) {
  console.log("[MathLine] Input:", math);
  const cleanMath = cleanLatexForKatex(math);
  console.log("[MathLine] After clean:", cleanMath);

  // VISADA bandome konvertuoti į LaTeX (trupmenas, daugybą ir t.t.)
  let finalMath = textToLatex(cleanMath);
  console.log("[MathLine] After textToLatex:", finalMath);

  // Jei po konvertavimo vis dar nėra LaTeX - rodome kaip paprastą tekstą
  if (!looksLikeLaTeX(finalMath)) {
    console.log("[MathLine] No LaTeX, showing monospace");
    return (
      <span className={className} style={{ fontFamily: "monospace" }}>
        {cleanMath}
      </span>
    );
  }

  if (block) {
    return (
      <div className={className}>
        <BlockMath
          math={finalMath}
          renderError={() => (
            <span style={{ fontFamily: "monospace" }}>{math}</span>
          )}
        />
      </div>
    );
  }

  return (
    <span className={className}>
      <InlineMath
        math={finalMath}
        renderError={() => (
          <span style={{ fontFamily: "monospace" }}>{math}</span>
        )}
      />
    </span>
  );
}

export function MathSolution({
  solution,
  className = "",
}: {
  solution: string;
  className?: string;
}) {
  console.log("[MathSolution] Received:", solution);
  if (!solution || solution.trim() === "") {
    return (
      <span
        className={className}
        style={{ color: "#666", fontStyle: "italic" }}
      >
        [Nera sprendimo]
      </span>
    );
  }
  return <MathRenderer math={solution} className={className} />;
}

export function MathText({
  text,
  className = "",
}: {
  text: string;
  className?: string;
}) {
  // Naudojame MixedMathText, kad tekstas būtų rodomas kaip tekstas,
  // o matematika - kaip LaTeX (tik $...$ blokai arba trupmenos)
  return <MixedMathText text={text} className={className} />;
}

/**
 * MixedMathText - Renderina tekstą su LaTeX formulėmis ($...$ blokais)
 * Naudojamas AI paaiškinimams, kuriuose yra mišrus tekstas su matematika
 */
export function MixedMathText({
  text,
  className = "",
}: {
  text: string;
  className?: string;
}) {
  if (!text) return null;

  console.log("[MixedMathText] Input:", text);

  const parts: React.ReactNode[] = [];

  // Pirmiausia patikriname ar yra $ simbolių arba LaTeX komandų
  const hasLatexCommands =
    text.includes("$") ||
    text.includes("\\frac") ||
    text.includes("\\cdot") ||
    text.includes("\\div") ||
    text.includes("\\left") ||
    text.includes("\\right");

  // Taip pat tikriname ar yra paprastos matematikos išraiškos (trupmenos, skaičiavimai)
  const hasSimpleMath = /\d+\/\d+|\(-?\d+\/\d+\)|\d+\s*[*×·]\s*\d+/.test(text);

  if (!hasLatexCommands && !hasSimpleMath) {
    // Paprastas tekstas be matematikos
    return <span className={className}>{text}</span>;
  }

  // Jei yra $...$ blokų - naudojame standartinę logiką
  if (text.includes("$")) {
    const regex = /\$([^$]+)\$/g;
    let lastIndex = 0;
    let match;
    let key = 0;

    while ((match = regex.exec(text)) !== null) {
      // Pridedame tekstą prieš formulę
      if (match.index > lastIndex) {
        const beforeText = text.slice(lastIndex, match.index);
        // Apdorojame tekstą prieš formulę - gali turėti paprastą matematiką
        parts.push(
          <span key={`text-${key++}`}>
            {renderSimpleMath(beforeText, key)}
          </span>,
        );
      }

      // Pridedame formulę su KaTeX
      const latexContent = match[1];
      try {
        console.log("[MixedMathText] Rendering LaTeX:", latexContent);
        parts.push(
          <span
            key={`math-${key++}`}
            className="inline-block align-middle mx-0.5"
          >
            <InlineMath math={cleanLatexForKatex(latexContent)} />
          </span>,
        );
      } catch (e) {
        console.warn("[MixedMathText] KaTeX error:", e);
        parts.push(
          <code key={`err-${key++}`} className="text-red-600">
            {match[0]}
          </code>,
        );
      }

      lastIndex = regex.lastIndex;
    }

    // Pridedame likusį tekstą po paskutinės formulės
    if (lastIndex < text.length) {
      const afterText = text.slice(lastIndex);
      parts.push(
        <span key={`text-end`}>{renderSimpleMath(afterText, 999)}</span>,
      );
    }

    console.log("[MixedMathText] Final parts:", parts.length);
    return <span className={className}>{parts}</span>;
  }

  // Jei nėra $ bet yra LaTeX komandos arba paprasta matematika
  return <span className={className}>{renderSimpleMath(text, 0)}</span>;
}

/**
 * Renderina paprastą matematiką (trupmenas, skaičiavimus) kaip LaTeX
 */
function renderSimpleMath(text: string, keyOffset: number): React.ReactNode {
  if (!text) return null;

  // Pattern'ai paprastai matematikai:
  // - Trupmenos su skliausteliais: (-14/45), (7/15)
  // - Paprastos trupmenos: 7/15, 14/45
  // - Skaičiai su operatoriais: -1.5, = -1
  const mathPattern =
    /(\(-?\d+(?:\/\d+)?\)|\d+\/\d+(?:\/\(-?\d+\/\d+\))?|-?\d+\.?\d*\s*[=]\s*-?\d+\.?\d*)/g;

  const parts: React.ReactNode[] = [];
  let lastIdx = 0;
  let m;
  let k = keyOffset;

  while ((m = mathPattern.exec(text)) !== null) {
    // Tekstas prieš
    if (m.index > lastIdx) {
      parts.push(<span key={`st-${k++}`}>{text.slice(lastIdx, m.index)}</span>);
    }

    // Konvertuojame į LaTeX ir renderuojame
    const mathExpr = m[0];
    const latex = convertToLatex(mathExpr);

    try {
      parts.push(
        <span key={`sm-${k++}`} className="inline-block align-middle mx-0.5">
          <InlineMath math={latex} />
        </span>,
      );
    } catch {
      parts.push(<span key={`se-${k++}`}>{mathExpr}</span>);
    }

    lastIdx = mathPattern.lastIndex;
  }

  // Likęs tekstas
  if (lastIdx < text.length) {
    parts.push(<span key={`st-${k++}`}>{text.slice(lastIdx)}</span>);
  }

  if (parts.length === 0) {
    return text;
  }

  return <>{parts}</>;
}

/**
 * Konvertuoja paprastą matematikos išraišką į LaTeX
 */
function convertToLatex(expr: string): string {
  let latex = expr;

  // Kompleksinė trupmena: 7/15/(-14/45)
  const complexFrac = latex.match(/^(\d+)\/(\d+)\/\((-?\d+)\/(\d+)\)$/);
  if (complexFrac) {
    const [, a, b, c, d] = complexFrac;
    return `\\frac{${a}}{${b}} \\div \\left(\\frac{${c}}{${d}}\\right)`;
  }

  // Trupmena skliausteliuose: (-14/45) arba (7/15)
  latex = latex.replace(/\((-?\d+)\/(\d+)\)/g, "\\left(\\frac{$1}{$2}\\right)");

  // Paprasta trupmena: 7/15
  latex = latex.replace(/(\d+)\/(\d+)/g, "\\frac{$1}{$2}");

  return latex;
}

export default MathRenderer;
