/**
 * ReviewPage - Įkeltų darbų peržiūra ir OCR rezultatai
 */

import { useState, useEffect, useMemo } from "react";
import {
  Eye,
  FileImage,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  ZoomIn,
  ZoomOut,
  RotateCw,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Search,
  Upload,
  ExternalLink,
  Trash2,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import {
  PageHeader,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Badge,
  EmptyState,
  Modal,
} from "@/components/ui";
import { useDeleteUpload } from "@/api/hooks";
import { MathRenderer } from "@/components/ui/MathRenderer";
import { cn } from "@/lib/utils";
import { useUploadStore, type UploadedFileData } from "@/stores";

// Tipai
interface UploadedFile {
  file_id: string;
  store_id: string; // Originalus ID iš Zustand store
  original_name: string;
  file_type: string;
  pages: number;
  size_bytes: number;
  uploaded_at: string;
  status: "pending" | "processing" | "completed" | "error";
  ocr_results?: OCRResult[];
}

interface OCRResult {
  page: number;
  text: string;
  latex?: string;
  confidence: number;
  source: string;
  is_math: boolean;
}

// Tuščias masyvas - demo duomenys pašalinti
const DEMO_FILES: UploadedFile[] = [];

export default function ReviewPage() {
  const navigate = useNavigate();

  // Zustand store
  const {
    files: storeFiles,
    removeFile: removeFromStore,
    clearFiles,
  } = useUploadStore();

  // API mutation
  const deleteUploadMutation = useDeleteUpload();

  // Convert store files to UploadedFile format
  const uploadedFiles = useMemo<UploadedFile[]>(() => {
    // Jei nėra realių failų - tuščias sąrašas (be demo)
    if (storeFiles.length === 0) {
      return [];
    }

    return storeFiles.map((f) => ({
      file_id: f.fileId || f.id,
      store_id: f.id, // Saugome originalų store ID
      original_name: f.fileName,
      file_type: f.fileType,
      pages: f.pages || 1,
      size_bytes: f.fileSize,
      uploaded_at: f.uploadedAt,
      status: f.status,
      ocr_results: f.ocrResult
        ? [
            {
              page: 1,
              text: f.ocrResult.text,
              latex: f.ocrResult.latex,
              confidence: f.ocrResult.confidence,
              source: f.ocrResult.source,
              is_math: f.ocrResult.isMath,
            },
          ]
        : undefined,
    }));
  }, [storeFiles]);

  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(false);
  const [previewModal, setPreviewModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    file_id: string;
    store_id: string;
  } | null>(null);

  // Ištrinti failą
  const handleDeleteFile = (file: UploadedFile, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setDeleteConfirm({ file_id: file.file_id, store_id: file.store_id });
  };

  const confirmDelete = async () => {
    if (deleteConfirm) {
      try {
        // Ištrinti iš backend
        await deleteUploadMutation.mutateAsync(deleteConfirm.file_id);
      } catch (error) {
        console.error("Klaida trinant failą iš serverio:", error);
      }
      // Ištrinti iš local store (naudojame store_id)
      removeFromStore(deleteConfirm.store_id);
      if (selectedFile?.file_id === deleteConfirm.file_id) {
        setSelectedFile(null);
      }
      setDeleteConfirm(null);
    }
  };

  // Filtruoti failus
  const filteredFiles = uploadedFiles.filter((file) => {
    const matchesSearch = file.original_name
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || file.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Formatuoti failo dydį
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1024 / 1024).toFixed(1) + " MB";
  };

  // Formatuoti datą
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString("lt-LT", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Statuso badge
  const getStatusBadge = (status: UploadedFile["status"]) => {
    switch (status) {
      case "completed":
        return (
          <Badge className="bg-green-100 text-green-700">
            <CheckCircle className="w-3 h-3 mr-1" />
            Apdorotas
          </Badge>
        );
      case "processing":
        return (
          <Badge className="bg-blue-100 text-blue-700">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Apdorojamas
          </Badge>
        );
      case "pending":
        return (
          <Badge className="bg-amber-100 text-amber-700">
            <Clock className="w-3 h-3 mr-1" />
            Laukia
          </Badge>
        );
      case "error":
        return (
          <Badge className="bg-red-100 text-red-700">
            <XCircle className="w-3 h-3 mr-1" />
            Klaida
          </Badge>
        );
    }
  };

  // Failo ikona
  const getFileIcon = (fileType: string) => {
    if (fileType === "application/pdf") {
      return <FileText className="w-8 h-8 text-red-500" />;
    }
    return <FileImage className="w-8 h-8 text-blue-500" />;
  };

  // OCR vykdymas
  const runOCR = async (fileId: string) => {
    setIsLoading(true);
    // Simuliuojame OCR
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Jei naudojame store, atnaujinti jame
    const storeFile = storeFiles.find(
      (f) => f.fileId === fileId || f.id === fileId
    );
    if (storeFile) {
      // TODO: Iškviesti tikrą OCR API ir atnaujinti store
      console.log("OCR paleistas failui:", storeFile.fileName);
    }

    // Atnaujinti pasirinktą failą peržiūroje
    if (selectedFile && selectedFile.file_id === fileId) {
      setSelectedFile({
        ...selectedFile,
        status: "completed",
        ocr_results: [
          {
            page: 1,
            text: "Atpažintas tekstas...\n1. x + 5 = 12\n2. 3y = 15",
            latex: "x + 5 = 12 \\\\ 3y = 15",
            confidence: 0.89,
            source: "hybrid",
            is_math: true,
          },
        ],
      });
    }

    setIsLoading(false);
  };

  // Pasirinkti failą peržiūrai
  const handleSelectFile = (file: UploadedFile) => {
    setSelectedFile(file);
    setCurrentPage(1);
    setZoom(100);
    setRotation(0);
  };

  // Atidaryti failą pilnam redagavimui
  const handleOpenFile = (file: UploadedFile) => {
    navigate(`/perziureti/${file.file_id}`);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Peržiūrėti darbus"
        description="Įkeltų mokinių darbų peržiūra ir OCR rezultatai"
        actions={
          uploadedFiles.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              className="text-red-600 border-red-300 hover:bg-red-50"
              onClick={() => {
                if (
                  window.confirm(
                    "Ar tikrai norite ištrinti visus įkeltus darbus?"
                  )
                ) {
                  clearFiles();
                  setSelectedFile(null);
                }
              }}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Išvalyti visus
            </Button>
          )
        }
      />

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Kairė pusė - failų sąrašas */}
        <div className="w-full lg:w-1/3 space-y-4">
          {/* Paieška ir filtrai */}
          <Card>
            <CardContent className="p-4 space-y-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Ieškoti pagal pavadinimą..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>

              <div className="flex gap-2 flex-wrap">
                {["all", "pending", "processing", "completed"].map((status) => (
                  <Button
                    key={status}
                    variant={statusFilter === status ? "default" : "outline"}
                    size="sm"
                    onClick={() => setStatusFilter(status)}
                  >
                    {status === "all" && "Visi"}
                    {status === "pending" && "Laukia"}
                    {status === "processing" && "Apdorojami"}
                    {status === "completed" && "Baigti"}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Failų sąrašas */}
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {filteredFiles.length === 0 ? (
              <Card>
                <CardContent className="p-6">
                  <EmptyState
                    icon={<FileImage className="w-8 h-8" />}
                    title="Nėra failų"
                    description="Įkelkite mokinių darbus, kad galėtumėte peržiūrėti rezultatus"
                  />
                  <div className="text-center mt-4">
                    <Link to="/ikelti">
                      <Button>
                        <Upload className="w-4 h-4 mr-2" />
                        Įkelti darbus
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ) : (
              filteredFiles.map((file) => (
                <Card
                  key={file.file_id}
                  className={cn(
                    "cursor-pointer transition-all hover:shadow-md",
                    selectedFile?.file_id === file.file_id &&
                      "ring-2 ring-primary"
                  )}
                  onClick={() => handleSelectFile(file)}
                  onDoubleClick={() => handleOpenFile(file)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {getFileIcon(file.file_type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm truncate">
                            {file.original_name}
                          </p>
                          <div className="flex items-center gap-1 shrink-0">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                              onClick={(e) => handleDeleteFile(file, e)}
                              title="Ištrinti"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleOpenFile(file);
                              }}
                              title="Atidaryti redagavimui"
                            >
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                          <span>{formatSize(file.size_bytes)}</span>
                          <span>•</span>
                          <span>
                            {file.pages}{" "}
                            {file.pages === 1 ? "puslapis" : "puslapiai"}
                          </span>
                        </div>
                        <div className="flex items-center justify-between mt-2">
                          {getStatusBadge(file.status)}
                          <span className="text-xs text-muted-foreground">
                            {formatDate(file.uploaded_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>

        {/* Dešinė pusė - peržiūra */}
        <div className="flex-1">
          {selectedFile ? (
            <Card className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">
                    {selectedFile.original_name}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    {selectedFile.status !== "completed" && (
                      <Button
                        size="sm"
                        onClick={() => runOCR(selectedFile.file_id)}
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                        ) : (
                          <RefreshCw className="w-4 h-4 mr-1" />
                        )}
                        Paleisti OCR
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setPreviewModal(true)}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      Viso dydžio
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleOpenFile(selectedFile)}
                    >
                      <ExternalLink className="w-4 h-4 mr-1" />
                      Atidaryti
                    </Button>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Vaizdo peržiūra */}
                <div className="bg-slate-100 rounded-lg p-4 min-h-[300px] flex items-center justify-center relative overflow-hidden">
                  {/* Rodome vaizdą tiek image, tiek PDF failams (PDF konvertuojamas į PNG backend'e) */}
                  {selectedFile.file_type.startsWith("image/") ||
                  selectedFile.file_type === "application/pdf" ? (
                    <div
                      className="transition-transform"
                      style={{
                        transform: `scale(${
                          zoom / 100
                        }) rotate(${rotation}deg)`,
                      }}
                    >
                      <img
                        src={`/api/v1/upload/${selectedFile.file_id}/page/${currentPage}`}
                        alt={selectedFile.original_name}
                        className="max-w-full max-h-[400px] rounded shadow-lg bg-white"
                        onError={(e) => {
                          // Fallback jei vaizdas nepasiekiamas
                          const target = e.target as HTMLImageElement;
                          target.style.display = "none";
                          target.parentElement!.innerHTML = `
                            <div class="w-[400px] h-[300px] bg-white rounded shadow-lg flex items-center justify-center text-gray-500">
                              <div class="text-center">
                                <p class="text-sm">Vaizdo peržiūra</p>
                                <p class="text-xs">(Nepavyko įkelti)</p>
                              </div>
                            </div>
                          `;
                        }}
                      />
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground">
                      <FileText className="w-16 h-16 mx-auto mb-2 opacity-50" />
                      <p>PDF peržiūra</p>
                    </div>
                  )}

                  {/* Zoom/Rotation controls */}
                  <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-white/90 rounded-lg px-3 py-2 shadow">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setZoom((z) => Math.max(50, z - 25))}
                    >
                      <ZoomOut className="w-4 h-4" />
                    </Button>
                    <span className="text-sm font-medium w-12 text-center">
                      {zoom}%
                    </span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setZoom((z) => Math.min(200, z + 25))}
                    >
                      <ZoomIn className="w-4 h-4" />
                    </Button>
                    <div className="w-px h-6 bg-slate-300" />
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setRotation((r) => (r + 90) % 360)}
                    >
                      <RotateCw className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Puslapiavimas */}
                  {selectedFile.pages > 1 && (
                    <div className="absolute bottom-4 right-4 flex items-center gap-2 bg-white/90 rounded-lg px-3 py-2 shadow">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          setCurrentPage((p) => Math.max(1, p - 1))
                        }
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </Button>
                      <span className="text-sm">
                        {currentPage} / {selectedFile.pages}
                      </span>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          setCurrentPage((p) =>
                            Math.min(selectedFile.pages, p + 1)
                          )
                        }
                        disabled={currentPage === selectedFile.pages}
                      >
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </div>

                {/* OCR rezultatai */}
                {selectedFile.ocr_results &&
                selectedFile.ocr_results.length > 0 ? (
                  <div className="space-y-4">
                    <h3 className="font-medium flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      OCR rezultatai
                      <Badge variant="outline">
                        {Math.round(
                          selectedFile.ocr_results[0].confidence * 100
                        )}
                        % tikslumas
                      </Badge>
                    </h3>

                    {/* Atpažintas tekstas */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium mb-2">
                          Atpažintas tekstas
                        </h4>
                        <div className="bg-slate-50 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap min-h-[100px]">
                          {selectedFile.ocr_results[0].text}
                        </div>
                      </div>

                      {selectedFile.ocr_results[0].latex && (
                        <div>
                          <h4 className="text-sm font-medium mb-2">
                            LaTeX formulės
                          </h4>
                          <div className="bg-slate-50 rounded-lg p-4 min-h-[100px]">
                            <MathRenderer
                              math={selectedFile.ocr_results[0].latex || ""}
                              block={true}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>
                        Šaltinis:{" "}
                        <Badge variant="outline">
                          {selectedFile.ocr_results[0].source}
                        </Badge>
                      </span>
                      {selectedFile.ocr_results[0].is_math && (
                        <Badge className="bg-purple-100 text-purple-700">
                          Matematika aptikta
                        </Badge>
                      )}
                    </div>
                  </div>
                ) : selectedFile.status === "pending" ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>Laukia OCR apdorojimo</p>
                    <Button
                      className="mt-4"
                      onClick={() => runOCR(selectedFile.file_id)}
                      disabled={isLoading}
                    >
                      Paleisti OCR
                    </Button>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          ) : (
            <Card className="h-full min-h-[500px] flex items-center justify-center">
              <EmptyState
                icon={<Eye className="w-10 h-10" />}
                title="Pasirinkite failą"
                description="Pasirinkite failą iš sąrašo kairėje, kad peržiūrėtumėte"
              />
            </Card>
          )}
        </div>
      </div>

      {/* Viso dydžio peržiūros modalas */}
      <Modal
        isOpen={previewModal}
        onClose={() => setPreviewModal(false)}
        title={selectedFile?.original_name || "Peržiūra"}
        size="xl"
      >
        <div className="h-[80vh] bg-slate-100 rounded-lg flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <FileImage className="w-24 h-24 mx-auto mb-4 opacity-50" />
            <p className="text-lg">Viso dydžio vaizdo peržiūra</p>
            <p className="text-sm">(Įkelkite tikrą failą)</p>
          </div>
        </div>
      </Modal>

      {/* Trinimo patvirtinimo modalas */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Ištrinti failą?"
      >
        <div className="space-y-4">
          <p className="text-muted-foreground">
            Ar tikrai norite ištrinti šį failą? Šio veiksmo negalima atšaukti.
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDeleteConfirm(null)}>
              Atšaukti
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              <Trash2 className="w-4 h-4 mr-2" />
              Ištrinti
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
