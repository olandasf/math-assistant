/**
 * Bendri TypeScript tipai aplikacijai.
 */

// === Mokslo metai ===
export interface SchoolYear {
  id: number
  name: string
  startDate: string
  endDate: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

// === Klasė ===
export interface SchoolClass {
  id: number
  name: string
  grade: number
  schoolYearId: number
  studentsCount?: number
  createdAt: string
  updatedAt: string
}

// === Mokinys ===
export interface Student {
  id: number
  uniqueCode: string
  firstName: string
  lastName: string
  classId: number
  className?: string
  createdAt: string
  updatedAt: string
}

// === Kontrolinis ===
export type TestStatus = 'draft' | 'active' | 'completed'

export interface Test {
  id: number
  title: string
  description?: string
  testDate: string
  topic?: string
  maxPoints: number
  timeLimitMinutes?: number
  status: TestStatus
  schoolYearId: number
  classId: number
  className?: string
  variantsCount?: number
  submissionsCount?: number
  createdAt: string
  updatedAt: string
}

// === Variantas ===
export interface Variant {
  id: number
  name: string
  maxPoints: number
  testId: number
  tasksCount?: number
}

// === Užduotis ===
export interface Task {
  id: number
  number: string
  text?: string
  correctAnswer: string
  correctAnswerNumeric?: number
  points: number
  solutionSteps?: string
  topic?: string
  difficulty: number
  orderIndex: number
  variantId: number
}

// === Pateikimas ===
export type SubmissionStatus = 
  | 'uploaded'
  | 'processing'
  | 'ocr_done'
  | 'checking'
  | 'reviewed'
  | 'completed'

export interface Submission {
  id: number
  filePath: string
  fileName: string
  fileType: string
  status: SubmissionStatus
  totalPoints: number
  maxPoints: number
  percentage: number
  grade?: number
  teacherNotes?: string
  studentId: number
  studentName?: string
  testId: number
  testTitle?: string
  variantId?: number
  variantName?: string
  submittedAt: string
  checkedAt?: string
}

// === Atsakymas ===
export interface Answer {
  id: number
  recognizedText?: string
  recognizedLatex?: string
  ocrConfidence: number
  isCorrect?: boolean
  earnedPoints: number
  maxPoints: number
  aiExplanation?: string
  teacherOverride: boolean
  teacherPoints?: number
  teacherComment?: string
  imageRegion?: string
  submissionId: number
  taskId: number
  taskNumber?: string
}

// === Klaida ===
export interface ErrorRecord {
  id: number
  errorType: string
  errorCode?: string
  description: string
  explanation?: string
  suggestion?: string
  severity: number
  answerId: number
}

// === Statistika ===
export interface StudentStatistics {
  id: number
  topic: string
  testsCount: number
  averageScore: number
  averageGrade: number
  bestScore: number
  worstScore: number
  commonErrors?: string
  improvementTrend: number
  studentId: number
}

export interface ClassStatistics {
  id: number
  topic: string
  testsCount: number
  averageScore: number
  averageGrade: number
  bestScore: number
  worstScore: number
  passRate: number
  commonErrors?: string
  classId: number
}

// === API atsakymai ===
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ApiError {
  detail: string
  status: number
}
