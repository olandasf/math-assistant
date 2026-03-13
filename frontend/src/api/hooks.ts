/**
 * API Hooks - TanStack Query hooks
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "./client";
import type {
  SchoolYear,
  SchoolYearCreate,
  SchoolYearUpdate,
  SchoolClass,
  SchoolClassCreate,
  SchoolClassUpdate,
  SchoolClassWithStudents,
  Student,
  StudentCreate,
  StudentUpdate,
  StudentBulkCreate,
  Test,
  TestCreate,
  TestUpdate,
  Variant,
  VariantCreate,
  VariantUpdate,
  VariantWithTasks,
  Task,
  TaskCreate,
  TaskUpdate,
  DashboardStats,
  PaginatedResponse,
  Exam,
  ExamWithTasks,
} from "./types";

// === Query Keys ===
export const queryKeys = {
  schoolYears: ["schoolYears"] as const,
  schoolYear: (id: number) => ["schoolYears", id] as const,
  activeSchoolYear: ["schoolYears", "active"] as const,

  classes: (schoolYearId?: number) => ["classes", { schoolYearId }] as const,
  class: (id: number) => ["classes", id] as const,
  classWithStudents: (id: number) => ["classes", id, "students"] as const,

  students: (classId?: number) => ["students", { classId }] as const,
  student: (id: number) => ["students", id] as const,
  studentByCode: (code: string) => ["students", "code", code] as const,

  tests: (classId?: number) => ["tests", { classId }] as const,
  test: (id: number) => ["tests", id] as const,
  testWithVariants: (id: number) => ["tests", id, "variants"] as const,

  variants: (testId: number) => ["variants", { testId }] as const,
  variant: (id: number) => ["variants", id] as const,
  variantWithTasks: (id: number) => ["variants", id, "tasks"] as const,

  tasks: (variantId: number) => ["tasks", { variantId }] as const,
  task: (id: number) => ["tasks", id] as const,

  dashboard: ["dashboard"] as const,
};

// === School Years ===
export function useSchoolYears() {
  return useQuery({
    queryKey: queryKeys.schoolYears,
    queryFn: async () => {
      const { data } = await apiClient.get<SchoolYear[]>("/school-years/");
      return data;
    },
  });
}

export function useActiveSchoolYear() {
  return useQuery({
    queryKey: queryKeys.activeSchoolYear,
    queryFn: async () => {
      const { data } = await apiClient.get<SchoolYear>("/school-years/active");
      return data;
    },
  });
}

export function useCreateSchoolYear() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: SchoolYearCreate) => {
      const { data } = await apiClient.post<SchoolYear>(
        "/school-years/",
        payload,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schoolYears });
    },
  });
}

export function useActivateSchoolYear() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.post<SchoolYear>(
        `/school-years/${id}/activate`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schoolYears });
      queryClient.invalidateQueries({ queryKey: queryKeys.activeSchoolYear });
    },
  });
}

// === Classes ===
export function useClasses(schoolYearId?: number) {
  return useQuery({
    queryKey: queryKeys.classes(schoolYearId),
    queryFn: async () => {
      const params = schoolYearId ? { school_year_id: schoolYearId } : {};
      const { data } = await apiClient.get<SchoolClass[]>("/classes/", {
        params,
      });
      return data;
    },
  });
}

export function useClass(id: number) {
  return useQuery({
    queryKey: queryKeys.class(id),
    queryFn: async () => {
      const { data } = await apiClient.get<SchoolClass>(`/classes/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useClassWithStudents(id: number) {
  return useQuery({
    queryKey: queryKeys.classWithStudents(id),
    queryFn: async () => {
      const { data } = await apiClient.get<SchoolClassWithStudents>(
        `/classes/${id}/with-students`,
      );
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: SchoolClassCreate) => {
      const { data } = await apiClient.post<SchoolClass>("/classes/", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["classes"] });
    },
  });
}

export function useUpdateClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: SchoolClassUpdate;
    }) => {
      const { data } = await apiClient.put<SchoolClass>(
        `/classes/${id}`,
        payload,
      );
      return data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["classes"] });
      queryClient.invalidateQueries({ queryKey: queryKeys.class(id) });
    },
  });
}

export function useDeleteClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/classes/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["classes"] });
    },
  });
}

// === Students ===
export function useStudents(classId?: number, page = 1, size = 50) {
  return useQuery({
    queryKey: [...queryKeys.students(classId), page, size],
    queryFn: async () => {
      const params: Record<string, unknown> = {
        skip: (page - 1) * size,
        limit: size,
      };
      if (classId) params.class_id = classId;
      const { data } = await apiClient.get<Student[]>("/students/", { params });
      return data;
    },
  });
}

export function useStudent(id: number) {
  return useQuery({
    queryKey: queryKeys.student(id),
    queryFn: async () => {
      const { data } = await apiClient.get<Student>(`/students/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useSearchStudents(query: string) {
  return useQuery({
    queryKey: ["students", "search", query],
    queryFn: async () => {
      const { data } = await apiClient.get<Student[]>("/students/search", {
        params: { q: query },
      });
      return data;
    },
    enabled: query.length >= 2,
  });
}

export function useCreateStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: StudentCreate) => {
      const { data } = await apiClient.post<Student>("/students/", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students"] });
      queryClient.invalidateQueries({ queryKey: ["classes"] });
    },
  });
}

export function useBulkCreateStudents() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: StudentBulkCreate) => {
      const { data } = await apiClient.post<Student[]>(
        "/students/bulk",
        payload,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students"] });
      queryClient.invalidateQueries({ queryKey: ["classes"] });
    },
  });
}

export function useUpdateStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: StudentUpdate;
    }) => {
      const { data } = await apiClient.put<Student>(`/students/${id}`, payload);
      return data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["students"] });
      queryClient.invalidateQueries({ queryKey: queryKeys.student(id) });
    },
  });
}

export function useDeleteStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/students/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students"] });
      queryClient.invalidateQueries({ queryKey: ["classes"] });
    },
  });
}

// === Tests ===
export function useTests(classId?: number) {
  return useQuery({
    queryKey: queryKeys.tests(classId),
    queryFn: async () => {
      const params = classId ? { class_id: classId } : {};
      const { data } = await apiClient.get<Test[]>("/tests/", { params });
      return data;
    },
  });
}

export function useTest(id: number) {
  return useQuery({
    queryKey: queryKeys.test(id),
    queryFn: async () => {
      const { data } = await apiClient.get<Test>(`/tests/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateTest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: TestCreate) => {
      const { data } = await apiClient.post<Test>("/tests/", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tests"] });
    },
  });
}

export function useUpdateTest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: TestUpdate;
    }) => {
      const { data } = await apiClient.put<Test>(`/tests/${id}`, payload);
      return data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["tests"] });
      queryClient.invalidateQueries({ queryKey: queryKeys.test(id) });
    },
  });
}

export function useDeleteTest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/tests/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tests"] });
    },
  });
}

// === Variants ===
export function useVariants(testId: number) {
  return useQuery({
    queryKey: queryKeys.variants(testId),
    queryFn: async () => {
      const { data } = await apiClient.get<Variant[]>(
        `/tests/${testId}/variants/`,
      );
      return data;
    },
    enabled: !!testId,
  });
}

export function useVariantWithTasks(testId: number, variantId: number) {
  return useQuery({
    queryKey: queryKeys.variantWithTasks(variantId),
    queryFn: async () => {
      const { data } = await apiClient.get<VariantWithTasks>(
        `/tests/${testId}/variants/${variantId}/with-tasks`,
      );
      return data;
    },
    enabled: !!testId && !!variantId,
  });
}

export function useCreateVariant(testId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: VariantCreate) => {
      const { data } = await apiClient.post<Variant>(
        `/tests/${testId}/variants/`,
        payload,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.variants(testId) });
    },
  });
}

// === Tasks ===
export function useTasks(testId: number, variantId: number) {
  return useQuery({
    queryKey: queryKeys.tasks(variantId),
    queryFn: async () => {
      const { data } = await apiClient.get<Task[]>(
        `/tests/${testId}/variants/${variantId}/tasks/`,
      );
      return data;
    },
    enabled: !!testId && !!variantId,
  });
}

export function useCreateTask(testId: number, variantId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: TaskCreate) => {
      const { data } = await apiClient.post<Task>(
        `/tests/${testId}/variants/${variantId}/tasks/`,
        payload,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks(variantId) });
      queryClient.invalidateQueries({ queryKey: ["tests"] });
    },
  });
}

export function useBulkCreateTasks(testId: number, variantId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (tasks: TaskCreate[]) => {
      const { data } = await apiClient.post<Task[]>(
        `/tests/${testId}/variants/${variantId}/tasks/bulk`,
        { tasks },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks(variantId) });
      queryClient.invalidateQueries({ queryKey: ["tests"] });
    },
  });
}

// === Dashboard ===
export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardStats>("/dashboard/stats");
      return data;
    },
  });
}

// === Math Checker ===
export interface TaskDefinition {
  task_number: string;
  expected_answer: string;
  max_points: number;
  task_type?: string;
}

export interface TaskCheckResult {
  task_number: string;
  student_answer: string | null;
  expected_answer: string;
  is_correct: boolean;
  points_earned: number;
  max_points: number;
  error_type?: string;
  error_description?: string;
  suggestion?: string;
}

export interface FullWorkCheckResponse {
  success: boolean;
  total_points: number;
  max_points: number;
  percentage: number;
  task_results: TaskCheckResult[];
  summary: string;
  ai_explanation?: string;
}

export function useCheckFullWork() {
  return useMutation({
    mutationFn: async (payload: {
      latex_content: string;
      tasks: TaskDefinition[];
      grade_level?: number;
    }): Promise<FullWorkCheckResponse> => {
      const { data } = await apiClient.post<FullWorkCheckResponse>(
        "/math/check-full-work",
        payload,
      );
      return data;
    },
  });
}

// === Auto Check (be iš anksto nustatytų atsakymų) ===
export interface SolutionStep {
  step_number: number;
  description: string;
  expression: string;
  result: string | null;
}

export interface SolutionMethod {
  method_name: string;
  steps: SolutionStep[];
  final_answer: string;
}

export interface ErrorAnalysis {
  error_type: string;
  error_location: string;
  what_went_wrong: string;
  why_wrong: string;
  how_to_fix: string;
}

export interface AutoTaskResult {
  task_id: string;
  task_text: string;
  student_solution: string;
  student_answer: string;
  calculated_answer?: string;
  is_correct?: boolean;
  error_description?: string;
  error_analysis?: ErrorAnalysis;
  solution_methods?: SolutionMethod[];
  suggestion?: string;
  confidence: number;
}

export interface AutoCheckResponse {
  success: boolean;
  task_results: AutoTaskResult[];
  total_tasks: number;
  correct_count: number;
  incorrect_count: number;
  unknown_count: number;
  summary: string;
  ai_analysis?: string;
}

export function useAutoCheck() {
  return useMutation({
    mutationFn: async (payload: {
      latex_content: string;
      grade_level?: number;
      check_calculations?: boolean;
    }): Promise<AutoCheckResponse> => {
      const { data } = await apiClient.post<AutoCheckResponse>(
        "/math/check-auto",
        payload,
      );
      return data;
    },
  });
}

// === Submissions ===
export interface AnswerCreate {
  task_id: number;
  recognized_text?: string;
  recognized_latex?: string;
  is_correct: boolean;
  earned_points: number;
  max_points: number;
  ai_explanation?: string;
}

export interface SaveCheckResultsRequest {
  student_id: number;
  test_id: number;
  variant_id?: number;
  file_path: string;
  file_name: string;
  latex_content: string;
  answers: AnswerCreate[];
  total_points: number;
  max_points: number;
  ai_explanation?: string;
}

export interface SubmissionSummary {
  id: number;
  student_id: number;
  student_name: string;
  test_id: number;
  test_title: string;
  status: string;
  total_points: number;
  max_points: number;
  percentage: number;
  grade?: number;
  submitted_at: string;
}

export function useSubmissions(
  testId?: number,
  studentId?: number,
  classId?: number,
) {
  return useQuery({
    queryKey: ["submissions", { testId, studentId, classId }],
    queryFn: async () => {
      const params: Record<string, number> = {};
      if (testId) params.test_id = testId;
      if (studentId) params.student_id = studentId;
      if (classId) params.class_id = classId;
      const { data } = await apiClient.get<SubmissionSummary[]>(
        "/submissions/",
        { params },
      );
      return data;
    },
  });
}

export function useSaveCheckResults() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: SaveCheckResultsRequest) => {
      const { data } = await apiClient.post(
        "/submissions/save-results",
        payload,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["submissions"] });
    },
  });
}

export function useUpdateGrade() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      submissionId,
      grade,
      teacherNotes,
    }: {
      submissionId: number;
      grade: number;
      teacherNotes?: string;
    }) => {
      const { data } = await apiClient.patch(
        `/submissions/${submissionId}/grade`,
        {
          grade,
          teacher_notes: teacherNotes,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["submissions"] });
    },
  });
}

// === PDF Exports ===
export interface GeneratePdfRequest {
  submission_id: number;
  include_explanations?: boolean;
  teacher_comments?: string;
}

export function useGenerateStudentPdf() {
  return useMutation({
    mutationFn: async (request: GeneratePdfRequest) => {
      const { data } = await apiClient.post("/exports/student-report", request);
      return data;
    },
  });
}

export function useExportsList() {
  return useQuery({
    queryKey: ["exports"],
    queryFn: async () => {
      const { data } = await apiClient.get("/exports/files");
      return data;
    },
  });
}

// === Alternative Solutions ===
export interface AlternativeSolutionsRequest {
  problem: string;
  correct_answer: string;
  grade_level?: number;
  num_solutions?: number;
}

export interface AlternativeSolutionsResponse {
  success: boolean;
  solutions: string;
  error?: string;
}

// === Upload Delete ===
export function useDeleteUpload() {
  return useMutation({
    mutationFn: async (fileId: string) => {
      const { data } = await apiClient.delete(`/upload/${fileId}`);
      return data;
    },
  });
}

// === Submissions Delete ===
export function useDeleteSubmission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (submissionId: number) => {
      const { data } = await apiClient.delete(`/submissions/${submissionId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["submissions"] });
    },
  });
}

export function useAlternativeSolutions() {
  return useMutation({
    mutationFn: async (
      payload: AlternativeSolutionsRequest,
    ): Promise<AlternativeSolutionsResponse> => {
      const { data } = await apiClient.post<AlternativeSolutionsResponse>(
        "/math/alternative-solutions",
        {
          problem: payload.problem,
          correct_answer: payload.correct_answer,
          grade_level: payload.grade_level ?? 6,
          num_solutions: payload.num_solutions ?? 3,
        },
      );
      return data;
    },
  });
}

// === Detailed Explanation with Thinking ===
export interface DetailedExplanationRequest {
  problem: string;
  student_answer: string;
  correct_answer: string;
  is_correct: boolean;
  grade_level?: number;
}

export interface DetailedExplanationResponse {
  success: boolean;
  explanation: string;
  error?: string;
}

export function useDetailedExplanation() {
  return useMutation({
    mutationFn: async (
      payload: DetailedExplanationRequest,
    ): Promise<DetailedExplanationResponse> => {
      const { data } = await apiClient.post<DetailedExplanationResponse>(
        "/math/detailed-explanation",
        {
          problem: payload.problem,
          student_answer: payload.student_answer,
          correct_answer: payload.correct_answer,
          is_correct: payload.is_correct,
          grade_level: payload.grade_level ?? 6,
        },
      );
      return data;
    },
  });
}

// === Exams (kontroliniai su PDF ir atsakymais) ===
export function useExams(classId?: number) {
  return useQuery({
    queryKey: ["exams", { classId }],
    queryFn: async () => {
      const params = classId ? { class_id: classId } : {};
      const { data } = await apiClient.get<Exam[]>("/exams/", { params });
      return data;
    },
  });
}

export function useExam(id: number) {
  return useQuery({
    queryKey: ["exams", id],
    queryFn: async () => {
      const { data } = await apiClient.get<ExamWithTasks>(`/exams/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useExamByQR(examId: string) {
  return useQuery({
    queryKey: ["exams", "qr", examId],
    queryFn: async () => {
      const { data } = await apiClient.get<ExamWithTasks>(
        `/exams/by-qr/${examId}`,
      );
      return data;
    },
    enabled: !!examId && examId.length > 0,
  });
}

// === Export ===
export * from "./types";
