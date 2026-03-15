/**
 * Settings Page - API raktų valdymas ir nustatymai
 */

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Badge } from "@/components/ui/badge";
import {
  Key,
  CheckCircle2,
  XCircle,
  Eye,
  EyeOff,
  RefreshCw,
  Save,
  AlertTriangle,
  Sparkles,
  Calculator,
  Brain,
  Zap,
  Cloud,
} from "lucide-react";

interface ApiConfig {
  name: string;
  description: string;
  icon: React.ReactNode;
  fields: ApiField[];
  testEndpoint?: string;
}

interface ApiField {
  key: string;
  label: string;
  placeholder: string;
  type: "text" | "password" | "file" | "select";
  required: boolean;
  options?: { value: string; label: string }[];
}

interface ApiStatus {
  isConnected: boolean;
  isLoading: boolean;
  message?: string;
}

// API konfigūracijos - Gemini, OpenAI, Novita, Together.ai ir WolframAlpha
const apiConfigs: ApiConfig[] = [
  {
    name: "Google Gemini",
    description: "OCR (Gemini Vision) per Google AI Studio API",
    icon: <Sparkles className="h-5 w-5" />,
    fields: [
      {
        key: "gemini_api_key",
        label: "Google AI Studio API Key",
        placeholder: "AIzaSy...",
        type: "password",
        required: true,
      },
      {
        key: "gemini_model",
        label: "Modelis",
        placeholder: "gemini-3.1-pro-preview",
        type: "select",
        required: false,
        options: [
          { value: "gemini-3.1-pro-preview", label: "Gemini 3.1 Pro Preview" },
          { value: "gemini-3-flash-preview", label: "Gemini 3 Flash Preview" },
        ],
      },
    ],
    testEndpoint: "/api/v1/settings/test/gemini",
  },
  {
    name: "OpenAI GPT",
    description: "OCR (GPT Vision) - alternatyva Gemini",
    icon: <Brain className="h-5 w-5" />,
    fields: [
      {
        key: "openai_api_key",
        label: "API Key",
        placeholder: "sk-...",
        type: "password",
        required: true,
      },
      {
        key: "openai_model",
        label: "Modelis",
        placeholder: "gpt-5.2",
        type: "text",
        required: false,
      },
    ],
    testEndpoint: "/api/v1/settings/test/openai",
  },
  {
    name: "WolframAlpha",
    description: "Sudėtingų matematinių užduočių tikrinimas",
    icon: <Calculator className="h-5 w-5" />,
    fields: [
      {
        key: "wolfram_app_id",
        label: "App ID",
        placeholder: "jūsų_wolfram_app_id",
        type: "password",
        required: true,
      },
    ],
    testEndpoint: "/api/v1/settings/test/wolfram",
  },
  {
    name: "Novita.ai (Qwen3 VL)",
    description:
      "OCR (Qwen3 Vision) - OpenAI-suderinama API, geras matematikos atpažinimas",
    icon: <Zap className="h-5 w-5" />,
    fields: [
      {
        key: "novita_api_key",
        label: "API Key",
        placeholder: "jūsų_novita_api_key",
        type: "password",
        required: true,
      },
      {
        key: "novita_model",
        label: "Modelis",
        placeholder: "qwen/qwen3.5-397b-a17b",
        type: "select",
        required: false,
        options: [
          { value: "qwen/qwen3.5-397b-a17b", label: "Qwen 3.5 397B (tikslus, lėtesnis)" },
          { value: "qwen/qwen3.5-35b-a3b", label: "Qwen 3.5 35B (greitesnis)" },
        ],
      },
    ],
    testEndpoint: "/api/v1/settings/test/novita",
  },
  {
    name: "Together.ai",
    description:
      "OCR - OpenAI-suderinama API su dideliais modeliais (Qwen, Llama)",
    icon: <Cloud className="h-5 w-5" />,
    fields: [
      {
        key: "together_api_key",
        label: "API Key",
        placeholder: "jūsų_together_api_key",
        type: "password",
        required: true,
      },
      {
        key: "together_model",
        label: "Modelis",
        placeholder: "Qwen/Qwen3.5-397B-A17B",
        type: "select",
        required: false,
        options: [
          { value: "Qwen/Qwen3.5-397B-A17B", label: "Qwen 3.5 397B" },
          { value: "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", label: "Llama 4 Maverick 17B" },
        ],
      },
    ],
    testEndpoint: "/api/v1/settings/test/together",
  },
];

function ApiCard({ config }: { config: ApiConfig }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [status, setStatus] = useState<ApiStatus>({
    isConnected: false,
    isLoading: false,
  });
  const [isSaving, setIsSaving] = useState(false);

  // Load saved values from localStorage on mount
  useEffect(() => {
    // Cleanup ALL old localStorage keys related to Google credentials (migration)
    const oldKeys = [
      "api_google_credentials_json",
      "api_google_credentials",
      "api_google_application_credentials",
      "google_credentials_json",
      "google_credentials",
    ];
    oldKeys.forEach((key) => {
      if (localStorage.getItem(key)) {
        console.log(`[Settings] Removing old key: ${key}`);
        localStorage.removeItem(key);
      }
    });

    const savedValues: Record<string, string> = {};
    config.fields.forEach((field) => {
      const saved = localStorage.getItem(`api_${field.key}`);
      if (saved) {
        savedValues[field.key] = saved;
      }
    });
    console.log(
      `[Settings] Loaded values for ${config.name}:`,
      Object.keys(savedValues),
    );
    setValues(savedValues);
  }, [config.fields, config.name]);

  const handleChange = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const toggleShowSecret = (key: string) => {
    setShowSecrets((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage (for demo - in production use backend)
      config.fields.forEach((field) => {
        const value = values[field.key];
        if (value) {
          localStorage.setItem(`api_${field.key}`, value);
        }
      });

      // Also send to backend
      const response = await fetch("/api/v1/settings/api-keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });

      if (!response.ok) {
        throw new Error("Nepavyko išsaugoti");
      }

      setStatus({
        isConnected: false,
        isLoading: false,
        message: "Išsaugota!",
      });
      setTimeout(
        () => setStatus((prev) => ({ ...prev, message: undefined })),
        2000,
      );
    } catch (error) {
      console.error("Save error:", error);
      // Still save to localStorage even if backend fails
      config.fields.forEach((field) => {
        const value = values[field.key];
        if (value) {
          localStorage.setItem(`api_${field.key}`, value);
        }
      });
      setStatus({
        isConnected: false,
        isLoading: false,
        message: "Išsaugota lokaliai",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    if (!config.testEndpoint) return;

    setStatus({ isConnected: false, isLoading: true });

    const requestBody = JSON.stringify(values);
    console.log(`[Settings] Testing ${config.name}`);
    console.log(`[Settings] Endpoint: ${config.testEndpoint}`);
    console.log(`[Settings] Request body: ${requestBody}`);

    try {
      const response = await fetch(config.testEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: requestBody,
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatus({
          isConnected: true,
          isLoading: false,
          message: data.message || "Prisijungta sėkmingai!",
        });
      } else {
        setStatus({
          isConnected: false,
          isLoading: false,
          message: data.error || "Nepavyko prisijungti",
        });
      }
    } catch (error) {
      setStatus({
        isConnected: false,
        isLoading: false,
        message: "Ryšio klaida - patikrinkite ar backend veikia",
      });
    }
  };

  // Tikrinti ar visi privalomi laukai užpildyti
  const requiredFieldsFilled = config.fields
    .filter((f) => f.required)
    .every((f) => values[f.key]?.trim());

  // Tikrinti ar bent vienas laukas užpildytas (jei visi neprivalomi)
  const hasAnyValue = config.fields.some((f) => values[f.key]?.trim());

  // Jei yra privalomų laukų - tikrinti juos, jei ne - tikrinti ar bent vienas užpildytas
  const hasRequiredFields = config.fields.some((f) => f.required)
    ? requiredFieldsFilled
    : hasAnyValue;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              {config.icon}
            </div>
            <div>
              <CardTitle className="text-lg">{config.name}</CardTitle>
              <CardDescription>{config.description}</CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {status.isLoading ? (
              <LoadingSpinner size="sm" />
            ) : status.isConnected ? (
              <Badge variant="default" className="bg-green-500">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Prisijungta
              </Badge>
            ) : status.message ? (
              <Badge variant="destructive">
                <XCircle className="h-3 w-3 mr-1" />
                Neprisijungta
              </Badge>
            ) : null}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {config.fields.map((field) => (
          <div key={field.key} className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Key className="h-3 w-3" />
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </label>
            {field.type === "file" ? (
              <div className="space-y-2">
                <input
                  type="file"
                  accept=".json"
                  title={field.label}
                  placeholder={field.placeholder}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      try {
                        const text = await file.text();
                        // Validate JSON
                        JSON.parse(text);
                        handleChange(field.key, text);
                        console.log(
                          `[DEBUG] JSON file loaded for ${field.key}, length: ${text.length}`,
                        );
                      } catch (err) {
                        console.error("Invalid JSON file:", err);
                        alert("Netinkamas JSON failas!");
                      }
                    }
                  }}
                />
                {values[field.key] && (
                  <div className="text-xs text-green-600 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    JSON failas įkeltas ({values[field.key].length} simbolių)
                  </div>
                )}
              </div>
            ) : field.type === "select" ? (
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={values[field.key] || ""}
                onChange={(e) => handleChange(field.key, e.target.value)}
              >
                <option value="">{field.placeholder}</option>
                {field.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : (
              <div className="relative">
                <Input
                  type={
                    field.type === "password" && !showSecrets[field.key]
                      ? "password"
                      : "text"
                  }
                  placeholder={field.placeholder}
                  value={values[field.key] || ""}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  className="pr-10"
                />
                {field.type === "password" && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
                    onClick={() => toggleShowSecret(field.key)}
                  >
                    {showSecrets[field.key] ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                )}
              </div>
            )}
          </div>
        ))}

        {status.message && !status.isLoading && (
          <div
            className={`flex items-center gap-2 text-sm p-2 rounded ${
              status.isConnected
                ? "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300"
                : "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300"
            }`}
          >
            {status.isConnected ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : (
              <AlertTriangle className="h-4 w-4" />
            )}
            {status.message}
          </div>
        )}

        <div className="flex gap-2 pt-2">
          <Button
            onClick={handleSave}
            disabled={!hasRequiredFields || isSaving}
            className="flex-1"
          >
            {isSaving ? (
              <LoadingSpinner size="sm" className="mr-2" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Išsaugoti
          </Button>
          <Button
            variant="outline"
            onClick={handleTest}
            disabled={!hasRequiredFields || status.isLoading}
          >
            {status.isLoading ? (
              <LoadingSpinner size="sm" className="mr-2" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Testuoti ryšį
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function SettingsPage() {
  const [gradingScale, setGradingScale] = useState({
    grade10: 95,
    grade9: 85,
    grade8: 75,
    grade7: 65,
    grade6: 55,
    grade5: 45,
    grade4: 35,
    grade3: 25,
    grade2: 15,
  });

  const [ocrProvider, setOcrProvider] = useState<string>("gemini");
  const [ocrSaving, setOcrSaving] = useState(false);

  // Užkrauti OCR provider iš backend
  useEffect(() => {
    const loadOcrProvider = async () => {
      try {
        const response = await fetch("/api/v1/settings/ocr-provider");
        if (response.ok) {
          const data = await response.json();
          setOcrProvider(data.provider || "gemini");
        }
      } catch (error) {
        console.error("[Settings] Nepavyko užkrauti OCR tiekėjo:", error);
      }
    };
    loadOcrProvider();
  }, []);

  const handleOcrProviderChange = async (provider: string) => {
    setOcrSaving(true);
    try {
      const response = await fetch("/api/v1/settings/ocr-provider", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider }),
      });
      if (response.ok) {
        setOcrProvider(provider);
        console.log(`[Settings] OCR tiekėjas pakeistas į: ${provider}`);
      }
    } catch (error) {
      console.error("[Settings] OCR tiekėjo keitimo klaida:", error);
    } finally {
      setOcrSaving(false);
    }
  };

  const handleGradeChange = (grade: string, value: number) => {
    setGradingScale((prev) => ({ ...prev, [grade]: value }));
  };

  const saveGradingScale = () => {
    localStorage.setItem("gradingScale", JSON.stringify(gradingScale));
    // TODO: Save to backend
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      <PageHeader
        title="Nustatymai"
        description="API raktų ir sistemos nustatymų valdymas"
      />

      {/* OCR Provider Selection */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Eye className="h-5 w-5" />
          OCR tiekėjas
        </h3>
        <p className="text-sm text-muted-foreground">
          Pasirinkite kurį AI naudoti teksto ir matematikos atpažinimui iš
          nuotraukų
        </p>

        <Card>
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <Button
                variant={ocrProvider === "gemini" ? "default" : "outline"}
                onClick={() => handleOcrProviderChange("gemini")}
                disabled={ocrSaving}
                className="flex-1"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Google Gemini
                {ocrProvider === "gemini" && (
                  <CheckCircle2 className="h-4 w-4 ml-2" />
                )}
              </Button>
              <Button
                variant={ocrProvider === "openai" ? "default" : "outline"}
                onClick={() => handleOcrProviderChange("openai")}
                disabled={ocrSaving}
                className="flex-1"
              >
                <Brain className="h-4 w-4 mr-2" />
                OpenAI GPT
                {ocrProvider === "openai" && (
                  <CheckCircle2 className="h-4 w-4 ml-2" />
                )}
              </Button>
              <Button
                variant={ocrProvider === "novita" ? "default" : "outline"}
                onClick={() => handleOcrProviderChange("novita")}
                disabled={ocrSaving}
                className="flex-1"
              >
                <Zap className="h-4 w-4 mr-2" />
                Novita.ai
                {ocrProvider === "novita" && (
                  <CheckCircle2 className="h-4 w-4 ml-2" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              {ocrProvider === "gemini"
                ? "Gemini Vision - nemokamas su Vertex AI, geras lietuvių kalbos palaikymas"
                : ocrProvider === "novita"
                  ? "Novita.ai Qwen3 VL - $0.30/1M tokenų (in), tikslus matematikos atpažinimas"
                  : "OpenAI GPT Vision - mokamas ($1.75/1M tokenų), labai tikslus"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Grading Scale Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Calculator className="h-5 w-5" />
          Vertinimo skalė
        </h3>
        <p className="text-sm text-muted-foreground">
          Nustatykite procentų ribas kiekvienam pažymiui
        </p>

        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
              {[10, 9, 8, 7, 6, 5, 4, 3, 2].map((grade) => {
                const key = `grade${grade}` as keyof typeof gradingScale;
                return (
                  <div key={grade} className="space-y-2">
                    <label className="text-sm font-medium flex items-center gap-1">
                      <span
                        className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                          grade >= 9
                            ? "bg-green-500 text-white"
                            : grade >= 7
                              ? "bg-blue-500 text-white"
                              : grade >= 5
                                ? "bg-amber-500 text-white"
                                : "bg-red-500 text-white"
                        }`}
                      >
                        {grade}
                      </span>
                      nuo %
                    </label>
                    <Input
                      type="number"
                      min={0}
                      max={100}
                      value={gradingScale[key]}
                      onChange={(e) =>
                        handleGradeChange(key, Number(e.target.value))
                      }
                      className="text-center"
                    />
                  </div>
                );
              })}
            </div>

            <div className="mt-4 p-3 bg-muted rounded-lg text-sm">
              <p className="font-medium mb-2">Peržiūra:</p>
              <div className="flex flex-wrap gap-2">
                {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((grade) => {
                  const key = `grade${grade}` as keyof typeof gradingScale;
                  const min = gradingScale[key] || 0;
                  const prevGrade = grade + 1;
                  const prevKey =
                    `grade${prevGrade}` as keyof typeof gradingScale;
                  const max = prevGrade <= 10 ? gradingScale[prevKey] - 1 : 100;

                  return (
                    <Badge key={grade} variant="outline">
                      {grade}: {min}%{grade < 10 ? `-${max}%` : "+"}
                    </Badge>
                  );
                })}
              </div>
            </div>

            <Button onClick={saveGradingScale} className="mt-4">
              <Save className="h-4 w-4 mr-2" />
              Išsaugoti skalę
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* API Keys Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Key className="h-5 w-5" />
          API raktai
        </h3>
        <p className="text-sm text-muted-foreground">
          Įveskite savo API raktus, kad sistema galėtų naudoti išorines
          paslaugas. Raktai saugomi saugiai ir niekada nerodomi pilnai.
        </p>

        {/* Cleanup button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            // Remove all old API keys and OCR settings from localStorage
            const keysToRemove: string[] = [];
            for (let i = 0; i < localStorage.length; i++) {
              const key = localStorage.key(i);
              if (
                key &&
                (key.startsWith("api_google_credentials") ||
                  key.startsWith("api_mathpix") ||
                  key.startsWith("api_google_vision") ||
                  key === "api_google_application_credentials" ||
                  key === "ocrSettings")
              ) {
                keysToRemove.push(key);
              }
            }
            keysToRemove.forEach((key) => {
              console.log(`[Cleanup] Removing: ${key}`);
              localStorage.removeItem(key);
            });
            alert(
              `Išvalyta ${keysToRemove.length} senų nustatymų. Atnaujinkite puslapį.`,
            );
            window.location.reload();
          }}
          className="text-xs"
        >
          🧹 Išvalyti senus nustatymus
        </Button>

        <div className="grid gap-4 md:grid-cols-2">
          {apiConfigs.map((config) => (
            <ApiCard key={config.name} config={config} />
          ))}
        </div>
      </div>

      {/* Info Section */}
      <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <AlertTriangle className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0" />
            <div className="text-sm text-blue-800 dark:text-blue-200 space-y-2">
              <p className="font-medium">Kaip gauti API raktus:</p>
              <ul className="list-disc list-inside space-y-1 text-blue-700 dark:text-blue-300">
                <li>
                  <strong>Google Gemini:</strong>{" "}
                  <a
                    href="https://aistudio.google.com/apikey"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-900"
                  >
                    aistudio.google.com/apikey
                  </a>{" "}
                  - nemokamas OCR ir AI
                </li>
                <li>
                  <strong>OpenAI:</strong>{" "}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-900"
                  >
                    platform.openai.com/api-keys
                  </a>{" "}
                  - GPT-5.2 Vision OCR
                </li>
                <li>
                  <strong>Novita.ai:</strong>{" "}
                  <a
                    href="https://novita.ai/dashboard/key"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-900"
                  >
                    novita.ai/dashboard/key
                  </a>{" "}
                  - Qwen3 VL Vision OCR
                </li>
                <li>
                  <strong>WolframAlpha:</strong>{" "}
                  <a
                    href="https://products.wolframalpha.com/api/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-900"
                  >
                    products.wolframalpha.com/api
                  </a>{" "}
                  - matematikos tikrinimas
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default SettingsPage;
