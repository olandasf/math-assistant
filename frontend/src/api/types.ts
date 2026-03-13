/**
 * Tipai - atitinka backend Pydantic schemas
 */

// === Base Types ===
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// === School Year ===
export interface SchoolYear {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  created_at: string;
}

export interface SchoolYearCreate {
  name: string;
  start_date: string;
  end_date: string;
  is_active?: boolean;
}

export interface SchoolYearUpdate {
  name?: string;
  start_date?: string;
  end_date?: string;
  is_active?: boolean;
}

// === School Class ===
export interface SchoolClass {
  id: number;
  name: string;
  grade: number;
  school_year_id: number;
  student_count?: number;
  created_at: string;
}

export interface SchoolClassCreate {
  name: string;
  grade: number;
  school_year_id: number;
}

export interface SchoolClassUpdate {
  name?: string;
  grade?: number;
}

export interface SchoolClassWithStudents extends SchoolClass {
  students: Student[];
}

// === Student ===
export interface Student {
  id: number;
  first_name: string;
  last_name: string;
  unique_code: string;
  class_id: number;
  notes?: string;
  is_active: boolean;
  created_at: string;
}

export interface StudentCreate {
  first_name: string;
  last_name: string;
  class_id: number;
  notes?: string;
}

export interface StudentUpdate {
  first_name?: string;
  last_name?: string;
  class_id?: number;
  notes?: string;
  is_active?: boolean;
}

export interface StudentBulkCreate {
  students: StudentCreate[];
}

// === Test ===
export interface Test {
  id: number;
  title: string;
  description?: string;
  test_date: string;
  topic?: string;
  max_points: number;
  time_limit_minutes?: number;
  status: "draft" | "active" | "completed";
  school_year_id: number;
  class_id: number;
  created_at: string;
  updated_at: string;
}

export interface TestCreate {
  title: string;
  description?: string;
  test_date: string;
  topic?: string;
  time_limit_minutes?: number;
  school_year_id: number;
  class_id: number;
}

export interface TestUpdate {
  title?: string;
  description?: string;
  test_date?: string;
  topic?: string;
  time_limit_minutes?: number;
  status?: "draft" | "active" | "completed";
}

export interface TestWithDetails extends Test {
  class_name?: string;
  variants_count: number;
  submissions_count: number;
  checked_count: number;
}

// === Variant ===
export interface Variant {
  id: number;
  name: string;
  max_points: number;
  test_id: number;
  created_at: string;
  updated_at: string;
}

export interface VariantCreate {
  name: string;
  test_id: number;
}

export interface VariantUpdate {
  name?: string;
}

export interface VariantWithTasks extends Variant {
  tasks: Task[];
  tasks_count: number;
}

// === Task ===
export interface Task {
  id: number;
  number: string;
  text?: string;
  correct_answer: string;
  correct_answer_numeric?: number;
  points: number;
  topic?: string;
  difficulty: number;
  order_index: number;
  solution_steps?: string;
  variant_id: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  number: string;
  text?: string;
  correct_answer: string;
  correct_answer_numeric?: number;
  points: number;
  topic?: string;
  difficulty?: number;
  order_index?: number;
  solution_steps?: string;
  variant_id: number;
}

export interface TaskUpdate {
  number?: string;
  text?: string;
  correct_answer?: string;
  correct_answer_numeric?: number;
  points?: number;
  topic?: string;
  difficulty?: number;
  order_index?: number;
  solution_steps?: string;
}

// === Submission ===
export interface Submission {
  id: number;
  student_id: number;
  variant_id: number;
  image_path?: string;
  total_points?: number;
  grade?: number;
  status: "pending" | "ocr_done" | "checked" | "reviewed";
  teacher_notes?: string;
  submitted_at: string;
  checked_at?: string;
}

// === Answer ===
export interface Answer {
  id: number;
  submission_id: number;
  task_id: number;
  raw_ocr_text?: string;
  interpreted_answer?: string;
  is_correct?: boolean;
  points_earned: number;
  needs_review: boolean;
  ocr_confidence?: number;
}

// === Error ===
export interface StudentError {
  id: number;
  answer_id: number;
  error_type: string;
  description: string;
  ai_explanation?: string;
  severity: "minor" | "major" | "critical";
}

// === Dashboard ===
export interface DashboardStats {
  total_students: number;
  total_classes: number;
  total_tests: number;
  pending_submissions: number;
  completed_today: number;
  average_grade: number | null;
}

// === Exam (kontrolinis su PDF) ===
export interface Exam {
  id: number;
  exam_id: string; // QR kodui (pvz. "7EB58EB2")
  title: string;
  test_date: string;
  topic?: string;
  max_points: number;
  status: "draft" | "active" | "completed";
  class_id: number;
  class_name?: string;
  variants_count: number;
  tasks_count: number;
  student_pdf?: string;
  teacher_pdf?: string;
  created_at: string;
}

export interface ExamTask {
  id: number;
  number: string;
  text: string;
  correct_answer: string;
  correct_answer_numeric?: number;
  points: number;
  variant_id: number;
  variant_name: string;
}

export interface ExamWithTasks extends Exam {
  tasks: ExamTask[];
}

export interface ClassStat {
  class_id: number;
  class_name: string;
  student_count: number;
  test_count: number;
  avg_grade?: number;
}
