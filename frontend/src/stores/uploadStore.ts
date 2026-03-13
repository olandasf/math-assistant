/**
 * Zustand store for managing uploaded files
 * Shares uploaded file data between UploadPage and ReviewPage
 */

import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

export interface UploadedFileData {
  id: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  uploadedAt: string;
  status: "pending" | "processing" | "completed" | "error";
  fileId?: string; // Backend file ID
  pages?: number;
  testId?: number;
  studentId?: number;
  variantId?: number;
  ocrResult?: {
    text: string;
    latex?: string;
    confidence: number;
    source: string;
    isMath: boolean;
    regions?: Array<{
      id: string;
      type: "text" | "math" | "diagram";
      content: string;
      latex?: string;
      confidence: number;
      bounds: { x: number; y: number; width: number; height: number };
    }>;
  };
}

interface UploadStore {
  // State
  files: UploadedFileData[];
  selectedFileId: string | null;

  // Actions
  addFile: (file: Omit<UploadedFileData, "uploadedAt">) => void;
  updateFile: (id: string, updates: Partial<UploadedFileData>) => void;
  removeFile: (id: string) => void;
  clearFiles: () => void;
  selectFile: (id: string | null) => void;

  // Selectors
  getFileById: (id: string) => UploadedFileData | undefined;
  getCompletedFiles: () => UploadedFileData[];
  getPendingFiles: () => UploadedFileData[];
}

export const useUploadStore = create<UploadStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        files: [],
        selectedFileId: null,

        // Actions
        addFile: (file) =>
          set(
            (state) => ({
              files: [
                ...state.files,
                {
                  ...file,
                  uploadedAt: new Date().toISOString(),
                },
              ],
            }),
            false,
            "addFile"
          ),

        updateFile: (id, updates) =>
          set(
            (state) => ({
              files: state.files.map((f) =>
                f.id === id ? { ...f, ...updates } : f
              ),
            }),
            false,
            "updateFile"
          ),

        removeFile: (id) =>
          set(
            (state) => ({
              files: state.files.filter((f) => f.id !== id),
              selectedFileId:
                state.selectedFileId === id ? null : state.selectedFileId,
            }),
            false,
            "removeFile"
          ),

        clearFiles: () =>
          set({ files: [], selectedFileId: null }, false, "clearFiles"),

        selectFile: (id) => set({ selectedFileId: id }, false, "selectFile"),

        // Selectors
        getFileById: (id) => get().files.find((f) => f.id === id),

        getCompletedFiles: () =>
          get().files.filter((f) => f.status === "completed"),

        getPendingFiles: () =>
          get().files.filter(
            (f) => f.status === "pending" || f.status === "processing"
          ),
      }),
      {
        name: "upload-storage", // localStorage key
        partialize: (state) => ({
          files: state.files,
        }),
      }
    ),
    { name: "UploadStore" }
  )
);

export default useUploadStore;
