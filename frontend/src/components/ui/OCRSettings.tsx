/**
 * OCRSettings - OCR nustatymų komponentas įkėlimo puslapiui
 * Leidžia pasirinkti OCR tiekėją ir nustatymus prieš apdorojimą
 */

import { useState } from "react";
import {
  Settings,
  Image as ImageIcon,
  FileText,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Info,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Label, Select, Button } from "@/components/ui";

export interface OCRSettingsConfig {
  /** Pagrindinis OCR tiekėjas */
  primaryProvider: "mathpix" | "google_vision" | "tesseract";
  /** Atsarginis OCR tiekėjas */
  fallbackProvider: "tesseract" | "none";
  /** Ar naudoti hibridinį režimą */
  useHybrid: boolean;
  /** Ar taikyti vaizdo pagerinimą */
  enhanceImage: boolean;
  /** Ar automatiškai aptikti orientaciją */
  autoRotate: boolean;
  /** Ar pašalinti triukšmą */
  denoise: boolean;
  /** Ar padidinti kontrastą */
  increaseContrast: boolean;
  /** Matematikos aptikimo jautrumas (0-1) */
  mathSensitivity: number;
  /** Kalba */
  language: "lt" | "en" | "mixed";
}

const DEFAULT_SETTINGS: OCRSettingsConfig = {
  primaryProvider: "mathpix",
  fallbackProvider: "tesseract",
  useHybrid: true,
  enhanceImage: true,
  autoRotate: true,
  denoise: true,
  increaseContrast: false,
  mathSensitivity: 0.7,
  language: "lt",
};

interface OCRSettingsProps {
  /** Dabartiniai nustatymai */
  settings: OCRSettingsConfig;
  /** Callback kai keičiasi nustatymai */
  onChange: (settings: OCRSettingsConfig) => void;
  /** Ar rodyti išplėstus nustatymus */
  showAdvanced?: boolean;
  /** Papildoma CSS klasė */
  className?: string;
  /** Kompaktiškas režimas */
  compact?: boolean;
}

export function OCRSettings({
  settings,
  onChange,
  showAdvanced: initialShowAdvanced = false,
  className,
  compact = false,
}: OCRSettingsProps) {
  const [showAdvanced, setShowAdvanced] = useState(initialShowAdvanced);

  const updateSetting = <K extends keyof OCRSettingsConfig>(
    key: K,
    value: OCRSettingsConfig[K]
  ) => {
    onChange({ ...settings, [key]: value });
  };

  const OCR_PROVIDERS = [
    {
      value: "mathpix",
      label: "MathPix",
      description: "Geriausias matematikai (mokamas)",
      icon: <Sparkles className="w-4 h-4 text-purple-500" />,
    },
    {
      value: "google_vision",
      label: "Google Vision",
      description: "Geras tekstui ir rašysenai",
      icon: <FileText className="w-4 h-4 text-blue-500" />,
    },
    {
      value: "tesseract",
      label: "Tesseract",
      description: "Nemokamas, lokalus",
      icon: <ImageIcon className="w-4 h-4 text-green-500" />,
    },
  ];

  if (compact) {
    return (
      <div className={cn("flex items-center gap-4", className)}>
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-slate-500" />
          <span className="text-sm text-slate-600">OCR:</span>
        </div>
        <Select
          value={settings.primaryProvider}
          onChange={(e) =>
            updateSetting(
              "primaryProvider",
              e.target.value as OCRSettingsConfig["primaryProvider"]
            )
          }
          className="text-sm"
        >
          {OCR_PROVIDERS.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </Select>
        <label className="flex items-center gap-1 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={settings.enhanceImage}
            onChange={(e) => updateSetting("enhanceImage", e.target.checked)}
            className="rounded border-slate-300"
          />
          <span>Pagerinti vaizdą</span>
        </label>
      </div>
    );
  }

  return (
    <div
      className={cn("border border-slate-200 rounded-lg bg-white", className)}
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-slate-600" />
          <h3 className="font-medium text-slate-900">OCR nustatymai</h3>
        </div>
      </div>

      {/* Pagrindiniai nustatymai */}
      <div className="p-4 space-y-4">
        {/* OCR tiekėjas */}
        <div>
          <Label className="mb-2 block">Pagrindinis OCR tiekėjas</Label>
          <div className="grid grid-cols-3 gap-2">
            {OCR_PROVIDERS.map((provider) => (
              <button
                key={provider.value}
                onClick={() =>
                  updateSetting(
                    "primaryProvider",
                    provider.value as OCRSettingsConfig["primaryProvider"]
                  )
                }
                className={cn(
                  "p-3 rounded-lg border text-left transition-all",
                  settings.primaryProvider === provider.value
                    ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500"
                    : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                )}
              >
                <div className="flex items-center gap-2 mb-1">
                  {provider.icon}
                  <span className="font-medium text-sm">{provider.label}</span>
                </div>
                <p className="text-xs text-slate-500">{provider.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Hibridinis režimas */}
        <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
          <div>
            <div className="font-medium text-sm text-slate-900">
              Hibridinis režimas
            </div>
            <p className="text-xs text-slate-500">
              Naudoti kelis OCR tiekėjus geresniam rezultatui
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.useHybrid}
              onChange={(e) => updateSetting("useHybrid", e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        {/* Vaizdo pagerinimas */}
        <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
          <div>
            <div className="font-medium text-sm text-slate-900">
              Vaizdo pagerinimas
            </div>
            <p className="text-xs text-slate-500">
              Automatiškai pagerinti vaizdo kokybę prieš OCR
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.enhanceImage}
              onChange={(e) => updateSetting("enhanceImage", e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>

      {/* Išplėstiniai nustatymai */}
      <div className="border-t border-slate-100">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full p-3 flex items-center justify-between text-sm text-slate-600 hover:bg-slate-50 transition-colors"
        >
          <span>Išplėstiniai nustatymai</span>
          {showAdvanced ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </button>

        {showAdvanced && (
          <div className="p-4 pt-0 space-y-4">
            {/* Automatinis sukimas */}
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoRotate}
                onChange={(e) => updateSetting("autoRotate", e.target.checked)}
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span className="text-sm text-slate-700">
                  Automatinis orientacijos aptikimas
                </span>
                <p className="text-xs text-slate-500">
                  Automatiškai pasukti pakreiptus vaizdus
                </p>
              </div>
            </label>

            {/* Triukšmo pašalinimas */}
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.denoise}
                onChange={(e) => updateSetting("denoise", e.target.checked)}
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span className="text-sm text-slate-700">
                  Triukšmo pašalinimas
                </span>
                <p className="text-xs text-slate-500">
                  Pašalinti smulkius taškelius ir defektus
                </p>
              </div>
            </label>

            {/* Kontrasto padidinimas */}
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.increaseContrast}
                onChange={(e) =>
                  updateSetting("increaseContrast", e.target.checked)
                }
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span className="text-sm text-slate-700">
                  Kontrasto padidinimas
                </span>
                <p className="text-xs text-slate-500">
                  Padidinti skirtumą tarp teksto ir fono
                </p>
              </div>
            </label>

            {/* Matematikos jautrumas */}
            <div>
              <Label className="mb-2 block">
                Matematikos aptikimo jautrumas:{" "}
                {Math.round(settings.mathSensitivity * 100)}%
              </Label>
              <input
                type="range"
                min="0"
                max="100"
                value={settings.mathSensitivity * 100}
                onChange={(e) =>
                  updateSetting(
                    "mathSensitivity",
                    parseInt(e.target.value) / 100
                  )
                }
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>Mažas</span>
                <span>Didelis</span>
              </div>
            </div>

            {/* Kalba */}
            <div>
              <Label className="mb-2 block">Teksto kalba</Label>
              <Select
                value={settings.language}
                onChange={(e) =>
                  updateSetting(
                    "language",
                    e.target.value as OCRSettingsConfig["language"]
                  )
                }
              >
                <option value="lt">Lietuvių</option>
                <option value="en">Anglų</option>
                <option value="mixed">Mišri (LT+EN)</option>
              </Select>
            </div>

            {/* Atsarginis tiekėjas */}
            <div>
              <Label className="mb-2 block">
                Atsarginis tiekėjas (jei nepavyksta)
              </Label>
              <Select
                value={settings.fallbackProvider}
                onChange={(e) =>
                  updateSetting(
                    "fallbackProvider",
                    e.target.value as OCRSettingsConfig["fallbackProvider"]
                  )
                }
              >
                <option value="tesseract">Tesseract</option>
                <option value="none">Nėra</option>
              </Select>
            </div>

            {/* Info */}
            <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg text-sm text-blue-700">
              <Info className="w-4 h-4 mt-0.5 shrink-0" />
              <p>
                Šie nustatymai bus taikomi visiems įkeliamiems failams. Galite
                juos keisti bet kuriuo metu.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Eksportuojame default nustatymus
export { DEFAULT_SETTINGS as DEFAULT_OCR_SETTINGS };

export default OCRSettings;
