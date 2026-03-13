/**
 * MathEditor - LaTeX matematikos formulių redagavimo komponentas
 * Leidžia įvesti ir redaguoti matematines formules su realaus laiko peržiūra
 */

import { useState, useCallback, useRef, useEffect } from "react";
import { MathRenderer } from "./MathRenderer";
import { Button } from "./button";
import { cn } from "../../lib/utils";

// Simbolio tipas
interface MathSymbol {
  symbol: string;
  latex: string;
  cursor?: number;
}

// Matematikos simbolių kategorijos
const MATH_SYMBOLS: Record<string, MathSymbol[]> = {
  Pagrindiniai: [
    { symbol: "+", latex: "+" },
    { symbol: "−", latex: "-" },
    { symbol: "×", latex: "\\times" },
    { symbol: "÷", latex: "\\div" },
    { symbol: "=", latex: "=" },
    { symbol: "≠", latex: "\\neq" },
    { symbol: "<", latex: "<" },
    { symbol: ">", latex: ">" },
    { symbol: "≤", latex: "\\leq" },
    { symbol: "≥", latex: "\\geq" },
  ],
  Trupmenos: [
    { symbol: "a/b", latex: "\\frac{a}{b}", cursor: 6 },
    { symbol: "a½", latex: "\\frac{1}{2}" },
    { symbol: "a⅓", latex: "\\frac{1}{3}" },
    { symbol: "a¼", latex: "\\frac{1}{4}" },
  ],
  Laipsniai: [
    { symbol: "x²", latex: "^{2}", cursor: 2 },
    { symbol: "x³", latex: "^{3}", cursor: 2 },
    { symbol: "xⁿ", latex: "^{n}", cursor: 2 },
    { symbol: "√", latex: "\\sqrt{}", cursor: 6 },
    { symbol: "∛", latex: "\\sqrt[3]{}", cursor: 9 },
    { symbol: "ⁿ√", latex: "\\sqrt[n]{}", cursor: 7 },
  ],
  Graikiškos: [
    { symbol: "π", latex: "\\pi" },
    { symbol: "α", latex: "\\alpha" },
    { symbol: "β", latex: "\\beta" },
    { symbol: "γ", latex: "\\gamma" },
    { symbol: "θ", latex: "\\theta" },
    { symbol: "φ", latex: "\\phi" },
  ],
  Geometrija: [
    { symbol: "°", latex: "^{\\circ}" },
    { symbol: "∠", latex: "\\angle" },
    { symbol: "△", latex: "\\triangle" },
    { symbol: "⊥", latex: "\\perp" },
    { symbol: "∥", latex: "\\parallel" },
    { symbol: "≅", latex: "\\cong" },
    { symbol: "∼", latex: "\\sim" },
  ],
  Kiti: [
    { symbol: "±", latex: "\\pm" },
    { symbol: "∓", latex: "\\mp" },
    { symbol: "∞", latex: "\\infty" },
    { symbol: "∈", latex: "\\in" },
    { symbol: "∉", latex: "\\notin" },
    { symbol: "∅", latex: "\\emptyset" },
    { symbol: "∪", latex: "\\cup" },
    { symbol: "∩", latex: "\\cap" },
  ],
};

interface MathEditorProps {
  /** Pradinė LaTeX reikšmė */
  value: string;
  /** Callback kai keičiasi reikšmė */
  onChange: (value: string) => void;
  /** Placeholder tekstas */
  placeholder?: string;
  /** Papildoma CSS klasė */
  className?: string;
  /** Ar rodyti simbolių paletę */
  showPalette?: boolean;
  /** Ar renderinti preview */
  showPreview?: boolean;
  /** Ar redaktorius disabled */
  disabled?: boolean;
  /** Callback kai paspaudžiamas Enter */
  onSubmit?: () => void;
  /** Aukštis (rows) */
  rows?: number;
}

export function MathEditor({
  value,
  onChange,
  placeholder = "Įveskite LaTeX formulę...",
  className,
  showPalette = true,
  showPreview = true,
  disabled = false,
  onSubmit,
  rows = 2,
}: MathEditorProps) {
  const [activeCategory, setActiveCategory] = useState<string>("Pagrindiniai");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Įterpti simbolį į tekstą ties kursoriaus pozicija
  const insertSymbol = useCallback(
    (latex: string, cursorOffset?: number) => {
      const textarea = textareaRef.current;
      if (!textarea || disabled) return;

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newValue = value.substring(0, start) + latex + value.substring(end);

      onChange(newValue);

      // Nustatyti kursoriaus poziciją
      const newPosition = cursorOffset
        ? start + latex.length - cursorOffset
        : start + latex.length;

      requestAnimationFrame(() => {
        textarea.focus();
        textarea.setSelectionRange(newPosition, newPosition);
      });
    },
    [value, onChange, disabled]
  );

  // Klaviatūros shortcuts
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && e.ctrlKey && onSubmit) {
        e.preventDefault();
        onSubmit();
        return;
      }

      // Automatinis skliaustų užbaigimas
      const pairs: Record<string, string> = {
        "(": ")",
        "[": "]",
        "{": "}",
      };

      if (pairs[e.key]) {
        e.preventDefault();
        const textarea = e.currentTarget;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = value.substring(start, end);
        const newValue =
          value.substring(0, start) +
          e.key +
          selectedText +
          pairs[e.key] +
          value.substring(end);

        onChange(newValue);

        requestAnimationFrame(() => {
          textarea.focus();
          textarea.setSelectionRange(
            start + 1,
            start + 1 + selectedText.length
          );
        });
      }
    },
    [value, onChange, onSubmit]
  );

  return (
    <div className={cn("space-y-2", className)}>
      {/* Simbolių paletė */}
      {showPalette && (
        <div className="border border-slate-200 rounded-lg p-2 bg-slate-50">
          {/* Kategorijų tabs */}
          <div className="flex flex-wrap gap-1 mb-2">
            {Object.keys(MATH_SYMBOLS).map((category) => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                disabled={disabled}
                className={cn(
                  "px-2 py-1 text-xs rounded transition-colors",
                  activeCategory === category
                    ? "bg-blue-500 text-white"
                    : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200",
                  disabled && "opacity-50 cursor-not-allowed"
                )}
              >
                {category}
              </button>
            ))}
          </div>

          {/* Simboliai */}
          <div className="flex flex-wrap gap-1">
            {MATH_SYMBOLS[activeCategory as keyof typeof MATH_SYMBOLS].map(
              (item, index) => (
                <button
                  key={index}
                  onClick={() => insertSymbol(item.latex, item.cursor)}
                  disabled={disabled}
                  title={item.latex}
                  className={cn(
                    "w-8 h-8 flex items-center justify-center text-lg",
                    "bg-white border border-slate-200 rounded",
                    "hover:bg-blue-50 hover:border-blue-300 transition-colors",
                    disabled && "opacity-50 cursor-not-allowed"
                  )}
                >
                  {item.symbol}
                </button>
              )
            )}
          </div>
        </div>
      )}

      {/* LaTeX įvedimo laukas */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={rows}
          className={cn(
            "w-full px-3 py-2 font-mono text-sm",
            "border border-slate-300 rounded-lg",
            "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            "placeholder:text-slate-400 resize-none",
            disabled && "bg-slate-100 cursor-not-allowed opacity-60"
          )}
        />
        {onSubmit && (
          <div className="absolute bottom-2 right-2 text-xs text-slate-400">
            Ctrl+Enter išsaugoti
          </div>
        )}
      </div>

      {/* Preview */}
      {showPreview && value && (
        <div className="p-3 bg-white border border-slate-200 rounded-lg">
          <div className="text-xs text-slate-500 mb-1">Peržiūra:</div>
          <div className="text-lg">
            <MathRenderer math={value} block />
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Kompaktiškas inline math editorius
 */
interface InlineMathEditorProps {
  value: string;
  onChange: (value: string) => void;
  onSave?: () => void;
  onCancel?: () => void;
  className?: string;
}

export function InlineMathEditor({
  value,
  onChange,
  onSave,
  onCancel,
  className,
}: InlineMathEditorProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
    inputRef.current?.select();
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && onSave) {
      e.preventDefault();
      onSave();
    } else if (e.key === "Escape" && onCancel) {
      e.preventDefault();
      onCancel();
    }
  };

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        className="flex-1 px-2 py-1 text-sm font-mono border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <div className="flex gap-1">
        {onSave && (
          <Button size="sm" onClick={onSave}>
            ✓
          </Button>
        )}
        {onCancel && (
          <Button size="sm" variant="outline" onClick={onCancel}>
            ✕
          </Button>
        )}
      </div>
    </div>
  );
}

export default MathEditor;
