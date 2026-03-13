/**
 * Kontrolinio detalių puslapis - variantai ir užduotys
 */

import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Plus,
  Edit,
  Trash2,
  Save,
  X,
  GripVertical,
  Calendar,
  Award,
  Clock,
  FileText,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import {
  useTest,
  useVariants,
  useTasks,
  useUpdateTest,
  useCreateVariant,
  useCreateTask,
  useDeleteTest,
} from "@/api/hooks";
import type {
  Test,
  Variant,
  Task,
  VariantCreate,
  TaskCreate,
  TestUpdate,
} from "@/api/types";
import { PageLoader, Modal, Button } from "@/components/ui";

export default function TestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const testId = parseInt(id || "0");

  const { data: test, isLoading: testLoading } = useTest(testId);
  const {
    data: variants,
    isLoading: variantsLoading,
    refetch: refetchVariants,
  } = useVariants(testId);

  const updateTestMutation = useUpdateTest();
  const deleteTestMutation = useDeleteTest();
  const createVariantMutation = useCreateVariant(testId);

  const [activeVariantId, setActiveVariantId] = useState<number | null>(null);
  const [isVariantModalOpen, setIsVariantModalOpen] = useState(false);
  const [newVariantName, setNewVariantName] = useState("I variantas");
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  // Set first variant as active when loaded
  if (variants?.length && !activeVariantId) {
    setActiveVariantId(variants[0].id);
  }

  const handleCreateVariant = async () => {
    await createVariantMutation.mutateAsync({
      name: newVariantName,
      test_id: testId,
    });
    setIsVariantModalOpen(false);
    setNewVariantName("");
    refetchVariants();
  };

  const handleDeleteTest = async () => {
    await deleteTestMutation.mutateAsync(testId);
    navigate("/kontroliniai");
  };

  const handleUpdateStatus = async (status: Test["status"]) => {
    await updateTestMutation.mutateAsync({
      id: testId,
      payload: { status },
    });
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("lt-LT", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (testLoading || variantsLoading) {
    return <PageLoader text="Kraunamas kontrolinis..." />;
  }

  if (!test) {
    return (
      <div className="rounded-lg bg-red-50 p-8 text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
        <h2 className="mt-4 text-lg font-medium text-red-800">
          Kontrolinis nerastas
        </h2>
        <Link
          to="/kontroliniai"
          className="mt-4 inline-block text-blue-600 hover:underline"
        >
          Grįžti į sąrašą
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/kontroliniai"
            className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{test.title}</h1>
            <div className="mt-1 flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {formatDate(test.test_date)}
              </span>
              <span className="flex items-center gap-1">
                <Award className="h-4 w-4" />
                {test.max_points} tšk.
              </span>
              {test.topic && (
                <span className="flex items-center gap-1">
                  <FileText className="h-4 w-4" />
                  {test.topic}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Status buttons */}
          <select
            value={test.status}
            onChange={(e) =>
              handleUpdateStatus(e.target.value as Test["status"])
            }
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="draft">Juodraštis</option>
            <option value="active">Aktyvus</option>
            <option value="completed">Įvertintas</option>
          </select>

          <button
            onClick={() => setIsDeleteModalOpen(true)}
            className="rounded-lg border border-red-300 p-2 text-red-600 hover:bg-red-50"
            title="Ištrinti"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Description */}
      {test.description && <p className="text-gray-600">{test.description}</p>}

      {/* Variants tabs */}
      <div className="border-b border-gray-200">
        <div className="flex items-center gap-2">
          {variants?.map((variant) => (
            <button
              key={variant.id}
              onClick={() => setActiveVariantId(variant.id)}
              className={`flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
                activeVariantId === variant.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
              }`}
            >
              {variant.name}
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                {variant.max_points} tšk.
              </span>
            </button>
          ))}
          <button
            onClick={() => setIsVariantModalOpen(true)}
            className="flex items-center gap-1 border-b-2 border-transparent px-4 py-3 text-sm text-gray-400 hover:text-gray-600"
          >
            <Plus className="h-4 w-4" />
            Pridėti variantą
          </button>
        </div>
      </div>

      {/* Variant content */}
      {activeVariantId ? (
        <VariantEditor testId={testId} variantId={activeVariantId} />
      ) : (
        <div className="rounded-lg border-2 border-dashed border-gray-200 p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            Nėra variantų
          </h3>
          <p className="mt-1 text-gray-500">
            Sukurkite pirmąjį kontrolinio variantą
          </p>
          <button
            onClick={() => setIsVariantModalOpen(true)}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600"
          >
            <Plus className="h-4 w-4" />
            Sukurti variantą
          </button>
        </div>
      )}

      {/* New Variant Modal */}
      <Modal
        isOpen={isVariantModalOpen}
        onClose={() => setIsVariantModalOpen(false)}
        title="Naujas variantas"
        size="sm"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setIsVariantModalOpen(false)}
            >
              Atšaukti
            </Button>
            <Button
              onClick={handleCreateVariant}
              isLoading={createVariantMutation.isPending}
            >
              Sukurti
            </Button>
          </>
        }
      >
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Varianto pavadinimas
          </label>
          <input
            type="text"
            value={newVariantName}
            onChange={(e) => setNewVariantName(e.target.value)}
            placeholder="pvz. I variantas"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Ištrinti kontrolinį?"
        size="sm"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setIsDeleteModalOpen(false)}
            >
              Atšaukti
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteTest}
              isLoading={deleteTestMutation.isPending}
            >
              Ištrinti
            </Button>
          </>
        }
      >
        <p className="text-gray-600">
          Ar tikrai norite ištrinti kontrolinį <strong>{test.title}</strong>?
          Bus ištrinti ir visi susiję variantai bei užduotys.
        </p>
      </Modal>
    </div>
  );
}

// === Variant Editor Component ===
interface VariantEditorProps {
  testId: number;
  variantId: number;
}

function VariantEditor({ testId, variantId }: VariantEditorProps) {
  const { data: tasks, isLoading, refetch } = useTasks(testId, variantId);
  const createTaskMutation = useCreateTask(testId, variantId);

  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [taskForm, setTaskForm] = useState<Partial<TaskCreate>>({
    number: "",
    text: "",
    correct_answer: "",
    points: 2,
    difficulty: 1,
  });

  const openNewTaskModal = () => {
    setEditingTask(null);
    setTaskForm({
      number: String((tasks?.length || 0) + 1),
      text: "",
      correct_answer: "",
      points: 2,
      difficulty: 1,
    });
    setIsTaskModalOpen(true);
  };

  const handleSaveTask = async () => {
    await createTaskMutation.mutateAsync({
      ...(taskForm as TaskCreate),
      variant_id: variantId,
      order_index: tasks?.length || 0,
    });
    setIsTaskModalOpen(false);
    refetch();
  };

  if (isLoading) {
    return (
      <div className="p-8 text-center text-gray-500">Kraunamos užduotys...</div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Tasks list */}
      {tasks?.length ? (
        <div className="space-y-3">
          {tasks.map((task, index) => (
            <TaskCard
              key={task.id}
              task={task}
              onEdit={() => {
                setEditingTask(task);
                setTaskForm({
                  number: task.number,
                  text: task.text,
                  correct_answer: task.correct_answer,
                  points: task.points,
                  difficulty: task.difficulty,
                });
                setIsTaskModalOpen(true);
              }}
            />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border-2 border-dashed border-gray-200 p-8 text-center">
          <p className="text-gray-500">Nėra užduočių šiame variante</p>
        </div>
      )}

      {/* Add task button */}
      <button
        onClick={openNewTaskModal}
        className="flex w-full items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-300 py-4 text-gray-500 transition-colors hover:border-blue-400 hover:text-blue-500"
      >
        <Plus className="h-5 w-5" />
        Pridėti užduotį
      </button>

      {/* Task Modal */}
      <Modal
        isOpen={isTaskModalOpen}
        onClose={() => setIsTaskModalOpen(false)}
        title={editingTask ? "Redaguoti užduotį" : "Nauja užduotis"}
        size="lg"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setIsTaskModalOpen(false)}
            >
              Atšaukti
            </Button>
            <Button
              onClick={handleSaveTask}
              isLoading={createTaskMutation.isPending}
            >
              {editingTask ? "Išsaugoti" : "Pridėti"}
            </Button>
          </>
        }
      >
        <TaskForm form={taskForm} onChange={setTaskForm} />
      </Modal>
    </div>
  );
}

// === Task Card Component ===
interface TaskCardProps {
  task: Task;
  onEdit: () => void;
}

function TaskCard({ task, onEdit }: TaskCardProps) {
  return (
    <div className="group flex items-start gap-4 rounded-lg border bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-600">
        {task.number}
      </div>

      <div className="min-w-0 flex-1">
        <div className="mb-2 text-gray-900">
          {task.text || <span className="italic text-gray-400">Be teksto</span>}
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <CheckCircle className="h-4 w-4 text-green-500" />
            {task.correct_answer}
          </span>
          <span className="flex items-center gap-1">
            <Award className="h-4 w-4" />
            {task.points} tšk.
          </span>
          <span className="flex items-center gap-1">
            Sudėtingumas: {"★".repeat(task.difficulty)}
            {"☆".repeat(5 - task.difficulty)}
          </span>
        </div>
      </div>

      <button
        onClick={onEdit}
        className="rounded p-1 text-gray-400 opacity-0 transition-all group-hover:opacity-100 hover:bg-gray-100 hover:text-gray-600"
      >
        <Edit className="h-4 w-4" />
      </button>
    </div>
  );
}

// === Task Form Component ===
interface TaskFormProps {
  form: Partial<TaskCreate>;
  onChange: (form: Partial<TaskCreate>) => void;
}

function TaskForm({ form, onChange }: TaskFormProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Numeris
          </label>
          <input
            type="text"
            value={form.number || ""}
            onChange={(e) => onChange({ ...form, number: e.target.value })}
            placeholder="1"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Taškai
          </label>
          <input
            type="number"
            value={form.points || ""}
            onChange={(e) =>
              onChange({ ...form, points: parseFloat(e.target.value) })
            }
            min={0}
            step={0.5}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Sudėtingumas
          </label>
          <select
            value={form.difficulty || 1}
            onChange={(e) =>
              onChange({ ...form, difficulty: parseInt(e.target.value) })
            }
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value={1}>★ Lengva</option>
            <option value={2}>★★ Paprasta</option>
            <option value={3}>★★★ Vidutinė</option>
            <option value={4}>★★★★ Sudėtinga</option>
            <option value={5}>★★★★★ Labai sudėtinga</option>
          </select>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Užduoties tekstas
        </label>
        <textarea
          value={form.text || ""}
          onChange={(e) => onChange({ ...form, text: e.target.value })}
          rows={3}
          placeholder="Apskaičiuokite: 1/2 + 1/4"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <p className="mt-1 text-xs text-gray-500">
          Galite naudoti LaTeX: {"$\\frac{1}{2} + \\frac{1}{4}$"}
        </p>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Teisingas atsakymas
        </label>
        <input
          type="text"
          value={form.correct_answer || ""}
          onChange={(e) =>
            onChange({ ...form, correct_answer: e.target.value })
          }
          placeholder="3/4 arba \frac{3}{4}"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <p className="mt-1 text-xs text-gray-500">
          Galite naudoti LaTeX formatą
        </p>
      </div>
    </div>
  );
}
