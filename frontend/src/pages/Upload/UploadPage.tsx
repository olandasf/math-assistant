/**
 * Failų įkėlimo puslapis
 * Drag & drop zona mokinių darbų įkėlimui
 */

import { useState, useCallback } from "react";
import {
  Upload,
  File,
  FileImage,
  FileText,
  X,
  CheckCircle,
  AlertCircle,
  Loader2,
  ChevronRight,
  Eye,
  Trash2,
  FileCheck,
  QrCode,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { PageHeader, Button, Modal } from "@/components/ui";
import {
  useTests,
  useClasses,
  useStudents,
  useActiveSchoolYear,
  useExams,
} from "@/api/hooks";
import apiClient from "@/api/client";
import { useUploadStore } from "@/stores";
import type { Exam } from "@/api/types";

interface UploadedFile {
  id: string;
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  progress: number;
  result?: {
    file_id: string;
    pages: number;
    file_type: string;
  };
  error?: string;
}

interface OCRResult {
  text: string;
  latex?: string;
  confidence: number;
  source: string;
  is_math: boolean;
}

export default function UploadPage() {
  const navigate = useNavigate();
  const { data: activeYear } = useActiveSchoolYear();
  const { data: classes } = useClasses(activeYear?.id);
  const { data: tests } = useTests();
  const { data: exams } = useExams(); // Naujas hook kontroliniams

  // Class and student selection
  const [selectedClassId, setSelectedClassId] = useState<number>(0);
  const { data: students } = useStudents(selectedClassId || undefined);
  const [selectedStudentId, setSelectedStudentId] = useState<number>(0);

  // Zustand store for sharing files with ReviewPage
  const { addFile: addToStore, updateFile: updateInStore } = useUploadStore();

  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [selectedTestId, setSelectedTestId] = useState<number>(0);
  const [isDragging, setIsDragging] = useState(false);
  const [previewFile, setPreviewFile] = useState<UploadedFile | null>(null);
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Reset student when class changes
  const handleClassChange = (classId: number) => {
    setSelectedClassId(classId);
    setSelectedStudentId(0);
  };

  // Drag & Drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = (newFiles: File[]) => {
    const validExtensions = [
      ".jpg",
      ".jpeg",
      ".png",
      ".pdf",
      ".tiff",
      ".tif",
      ".bmp",
      ".webp",
    ];

    const validFiles = newFiles.filter((file) => {
      const ext = "." + file.name.split(".").pop()?.toLowerCase();
      return validExtensions.includes(ext);
    });

    const uploadFiles: UploadedFile[] = validFiles.map((file) => ({
      id: Math.random().toString(36).substring(7),
      file,
      status: "pending",
      progress: 0,
    }));

    setFiles((prev) => [...prev, ...uploadFiles]);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const uploadFile = async (uploadFile: UploadedFile) => {
    setFiles((prev) =>
      prev.map((f) =>
        f.id === uploadFile.id ? { ...f, status: "uploading" } : f,
      ),
    );

    try {
      const formData = new FormData();
      formData.append("file", uploadFile.file);
      if (selectedTestId) {
        formData.append("test_id", selectedTestId.toString());
      }
      if (selectedStudentId) {
        formData.append("student_id", selectedStudentId.toString());
      }

      const response = await apiClient.post("/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          setFiles((prev) =>
            prev.map((f) => (f.id === uploadFile.id ? { ...f, progress } : f)),
          );
        },
      });

      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? {
                ...f,
                status: "success",
                progress: 100,
                result: response.data,
              }
            : f,
        ),
      );

      // Add to Zustand store for ReviewPage
      const storeId = uploadFile.id;
      addToStore({
        id: storeId,
        fileName: uploadFile.file.name,
        fileSize: uploadFile.file.size,
        fileType: uploadFile.file.type || "image/jpeg",
        status: "processing",
        fileId: response.data.file_id,
        pages: response.data.pages || 1,
        testId: selectedTestId || undefined,
        studentId: selectedStudentId || undefined,
      });

      // Automatiškai paleisti OCR VISIEMS PUSLAPIAMS
      try {
        const ocrResponse = await apiClient.post("/upload/ocr/all-pages", {
          file_id: response.data.file_id,
          detect_math: true,
        });

        // Atnaujinti store su OCR rezultatais (visi puslapiai)
        updateInStore(storeId, {
          status: "completed",
          ocrResult: {
            text: ocrResponse.data.text,
            latex: ocrResponse.data.latex,
            confidence: ocrResponse.data.confidence,
            source: ocrResponse.data.source,
            isMath: ocrResponse.data.is_math,
          },
        });

        console.log(
          "[INFO] OCR automatiškai atliktas (visi puslapiai):",
          response.data.file_id,
          {
            pages: ocrResponse.data.pages,
            separatorCount:
              ocrResponse.data.latex?.split("§§§").length - 1 || 0,
          },
        );
      } catch (ocrError) {
        console.error("[ERROR] Automatinis OCR nepavyko:", ocrError);
        // Pažymime kad OCR nepavyko, bet failas įkeltas
        updateInStore(storeId, {
          status: "completed",
        });
      }
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Nepavyko įkelti failo";
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? { ...f, status: "error", error: errorMessage }
            : f,
        ),
      );
    }
  };

  const uploadAll = async () => {
    const pendingFiles = files.filter((f) => f.status === "pending");
    for (const file of pendingFiles) {
      await uploadFile(file);
    }
  };

  const performOCR = async (fileId: string) => {
    setIsProcessing(true);
    setOcrResult(null);

    try {
      const response = await apiClient.post("/upload/ocr/all-pages", {
        file_id: fileId,
        detect_math: true,
      });
      setOcrResult(response.data);
      console.log("[INFO] Manual OCR completed (all pages):", {
        pages: response.data.pages,
        separatorCount: response.data.latex?.split("§§§").length - 1 || 0,
      });
    } catch (error) {
      console.error("OCR klaida:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split(".").pop()?.toLowerCase();
    if (ext === "pdf") return FileText;
    return FileImage;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1024 / 1024).toFixed(1) + " MB";
  };

  const pendingCount = files.filter((f) => f.status === "pending").length;
  const successCount = files.filter((f) => f.status === "success").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Įkelti darbus"
        description="Įkelkite mokinių skanuotus arba nufotografuotus kontrolinius"
      />

      {/* Class, Student, and Test selection */}
      <div className="rounded-lg border bg-white p-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {/* Class selection */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Klasė
            </label>
            <select
              value={selectedClassId}
              onChange={(e) => handleClassChange(parseInt(e.target.value))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value={0}>Pasirinkite klasę...</option>
              {classes?.map((cls) => (
                <option key={cls.id} value={cls.id}>
                  {cls.name}
                </option>
              ))}
            </select>
          </div>

          {/* Student selection */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Mokinys
            </label>
            <select
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(parseInt(e.target.value))}
              disabled={!selectedClassId}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value={0}>
                {selectedClassId
                  ? "Pasirinkite mokinį..."
                  : "Pirma pasirinkite klasę"}
              </option>
              {students?.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.first_name} {student.last_name}
                </option>
              ))}
            </select>
          </div>

          {/* Exam selection - PATOBULINTAS */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              <span className="flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-blue-500" />
                Kontrolinis darbas
              </span>
            </label>
            <select
              value={selectedTestId}
              onChange={(e) => setSelectedTestId(parseInt(e.target.value))}
              className={`w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none ${
                selectedTestId > 0
                  ? "border-green-500 bg-green-50"
                  : "border-gray-300"
              }`}
            >
              <option value={0}>-- Pasirinkite kontrolinį --</option>
              {exams?.map((exam) => (
                <option key={exam.id} value={exam.id}>
                  📝 {exam.title} | {exam.test_date} | {exam.max_points} tšk.
                </option>
              ))}
              {/* Fallback to tests if no exams */}
              {(!exams || exams.length === 0) &&
                tests?.map((test) => (
                  <option key={test.id} value={test.id}>
                    {test.title} -{" "}
                    {classes?.find((c) => c.id === test.class_id)?.name}
                  </option>
                ))}
            </select>
            {selectedTestId > 0 && (
              <p className="mt-1 text-xs text-green-600 flex items-center gap-1">
                <QrCode className="h-3 w-3" />
                Tikrinimas bus greitesnis - atsakymai bus lyginami su DB
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Drop zone */}
      <div
        className={`relative rounded-xl border-2 border-dashed p-12 text-center transition-colors ${
          isDragging
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 bg-gray-50 hover:border-gray-400"
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.pdf,.tiff,.tif,.bmp,.webp"
          onChange={handleFileInput}
          className="absolute inset-0 cursor-pointer opacity-0"
        />

        <Upload
          className={`mx-auto h-12 w-12 ${
            isDragging ? "text-blue-500" : "text-gray-400"
          }`}
        />

        <h3 className="mt-4 text-lg font-medium text-gray-900">
          {isDragging ? "Paleiskite failus čia" : "Tempkite failus čia"}
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          arba paspauskite norėdami pasirinkti
        </p>
        <p className="mt-2 text-xs text-gray-400">
          Palaikomi formatai: JPG, PNG, PDF, TIFF, BMP, WEBP (max 50 MB)
        </p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="rounded-lg border bg-white">
          <div className="flex items-center justify-between border-b px-4 py-3">
            <div className="text-sm text-gray-600">
              <span className="font-medium">{files.length}</span> failai
              {successCount > 0 && (
                <span className="ml-2 text-green-600">
                  ({successCount} įkelta)
                </span>
              )}
            </div>
            {pendingCount > 0 && (
              <Button onClick={uploadAll}>Įkelti visus ({pendingCount})</Button>
            )}
          </div>

          <ul className="divide-y">
            {files.map((file) => {
              const FileIcon = getFileIcon(file.file.name);
              return (
                <li key={file.id} className="flex items-center gap-4 px-4 py-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gray-100">
                    <FileIcon className="h-5 w-5 text-gray-500" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-gray-900">
                      {file.file.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(file.file.size)}
                      {file.result?.pages && file.result.pages > 1 && (
                        <span className="ml-2">
                          • {file.result.pages} puslapiai
                        </span>
                      )}
                    </p>
                  </div>

                  {/* Status */}
                  <div className="flex items-center gap-2">
                    {file.status === "pending" && (
                      <span className="text-sm text-gray-400">Laukia</span>
                    )}
                    {file.status === "uploading" && (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                        <span className="text-sm text-blue-600">
                          {file.progress}%
                        </span>
                      </div>
                    )}
                    {file.status === "success" && (
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <button
                          onClick={() => {
                            setPreviewFile(file);
                            if (file.result?.file_id) {
                              performOCR(file.result.file_id);
                            }
                          }}
                          className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                          title="Peržiūrėti ir OCR"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                    {file.status === "error" && (
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-5 w-5 text-red-500" />
                        <span className="text-sm text-red-600">
                          {file.error}
                        </span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => removeFile(file.id)}
                    className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {/* Quick actions */}
      {successCount > 0 && (
        <div className="flex items-center justify-between gap-4 rounded-lg border bg-green-50 p-4">
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle className="h-5 w-5" />
            <span className="font-medium">
              {successCount} failai sėkmingai įkelti
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/kontroliniai"
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Grįžti į kontrolinius
            </Link>
            <Button onClick={() => navigate("/perziureti")}>
              Peržiūrėti rezultatus
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* OCR Preview Modal */}
      <Modal
        isOpen={!!previewFile}
        onClose={() => {
          setPreviewFile(null);
          setOcrResult(null);
        }}
        title={previewFile?.file.name || "Peržiūra"}
        size="xl"
      >
        <div className="grid gap-6 md:grid-cols-2">
          {/* Image preview */}
          <div className="overflow-hidden rounded-lg border bg-gray-100">
            {previewFile?.result?.file_id && (
              <img
                src={`/api/v1/upload/${previewFile.result.file_id}/page/1`}
                alt="Vaizdas"
                className="h-full w-full object-contain"
              />
            )}
          </div>

          {/* OCR Result */}
          <div>
            <h4 className="mb-2 text-sm font-medium text-gray-700">
              OCR rezultatas
            </h4>

            {isProcessing && (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Apdorojama...
              </div>
            )}

            {ocrResult && (
              <div className="space-y-4">
                <div className="rounded-lg border bg-gray-50 p-4">
                  <p className="whitespace-pre-wrap text-gray-900">
                    {ocrResult.text}
                  </p>
                </div>

                {ocrResult.latex && (
                  <div>
                    <h5 className="mb-1 text-xs font-medium text-gray-500">
                      LaTeX
                    </h5>
                    <pre className="overflow-x-auto rounded bg-gray-800 p-3 text-sm text-green-400">
                      {ocrResult.latex}
                    </pre>
                  </div>
                )}

                <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                  <span className="rounded bg-gray-100 px-2 py-1">
                    Tikimybė: {Math.round(ocrResult.confidence * 100)}%
                  </span>
                  <span className="rounded bg-gray-100 px-2 py-1">
                    Šaltinis: {ocrResult.source}
                  </span>
                  {ocrResult.is_math && (
                    <span className="rounded bg-blue-100 px-2 py-1 text-blue-700">
                      Matematika aptikta
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}
