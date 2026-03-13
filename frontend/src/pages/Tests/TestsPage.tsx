/**
 * Kontroliniai puslapis - testų sąrašas ir valdymas
 */

import { useState } from "react";
import {
  FileText,
  Plus,
  Edit,
  Trash2,
  ChevronRight,
  Calendar,
  Award,
  Clock,
  CheckCircle,
  Sparkles,
} from "lucide-react";
import { Link } from "react-router-dom";
import {
  useTests,
  useClasses,
  useActiveSchoolYear,
  useCreateTest,
  useDeleteTest,
} from "@/api/hooks";
import type { Test, TestCreate, SchoolClass } from "@/api/types";
import {
  PageHeader,
  PageLoader,
  EmptyState,
  Modal,
  Button,
} from "@/components/ui";

const statusLabels: Record<Test["status"], string> = {
  draft: "Juodraštis",
  active: "Aktyvus",
  completed: "Įvertintas",
};

const statusColors: Record<Test["status"], string> = {
  draft: "bg-gray-100 text-gray-600",
  active: "bg-blue-100 text-blue-600",
  completed: "bg-green-100 text-green-600",
};

const statusIcons: Record<Test["status"], React.ReactNode> = {
  draft: <Clock className="h-3 w-3" />,
  active: <FileText className="h-3 w-3" />,
  completed: <CheckCircle className="h-3 w-3" />,
};

export default function TestsPage() {
  const { data: activeYear } = useActiveSchoolYear();
  const { data: classes } = useClasses(activeYear?.id);
  const { data: tests, isLoading, error } = useTests();

  const createMutation = useCreateTest();
  const deleteMutation = useDeleteTest();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<Test | null>(null);

  // Form state
  const [formData, setFormData] = useState<TestCreate>({
    title: "",
    description: "",
    class_id: 0,
    school_year_id: 0,
    topic: "",
    test_date: new Date().toISOString().split("T")[0],
  });

  const openCreateModal = () => {
    setFormData({
      title: "",
      description: "",
      class_id: classes?.[0]?.id || 0,
      school_year_id: activeYear?.id || 0,
      topic: "",
      test_date: new Date().toISOString().split("T")[0],
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createMutation.mutateAsync(formData);
    setIsModalOpen(false);
  };

  const handleDelete = async () => {
    if (deleteConfirm) {
      await deleteMutation.mutateAsync(deleteConfirm.id);
      setDeleteConfirm(null);
    }
  };

  const getClassName = (classId: number) => {
    return classes?.find((c) => c.id === classId)?.name || "Nežinoma";
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("lt-LT", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (isLoading) {
    return <PageLoader text="Kraunami kontroliniai..." />;
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-600">
        Klaida kraunant kontrolinius: {error.message}
      </div>
    );
  }

  // Group tests by status
  const activeTests =
    tests?.filter((t) => t.status === "active" || t.status === "draft") || [];
  const completedTests = tests?.filter((t) => t.status === "completed") || [];

  return (
    <div>
      <PageHeader
        title="Kontroliniai"
        description={`Iš viso: ${tests?.length || 0} kontrolinių`}
        actions={
          <div className="flex gap-2">
            <Link to="/kontroliniai/generuoti">
              <Button variant="secondary">
                <Sparkles className="h-4 w-4" />
                Generuoti su AI
              </Button>
            </Link>
            <Button onClick={openCreateModal}>
              <Plus className="h-4 w-4" />
              Naujas kontrolinis
            </Button>
          </div>
        }
      />

      {!tests?.length ? (
        <EmptyState
          icon={<FileText className="h-12 w-12" />}
          title="Nėra kontrolinių"
          description="Sukurkite pirmąjį kontrolinį darbą"
          action={{
            label: "Sukurti kontrolinį",
            onClick: openCreateModal,
          }}
        />
      ) : (
        <div className="space-y-8">
          {/* Active/Draft tests */}
          {activeTests.length > 0 && (
            <section>
              <h2 className="mb-4 text-lg font-semibold text-gray-900">
                Aktyvūs kontroliniai
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {activeTests.map((test) => (
                  <TestCard
                    key={test.id}
                    test={test}
                    className={getClassName(test.class_id)}
                    onDelete={() => setDeleteConfirm(test)}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Completed tests */}
          {completedTests.length > 0 && (
            <section>
              <h2 className="mb-4 text-lg font-semibold text-gray-900">
                Įvertinti kontroliniai
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {completedTests.map((test) => (
                  <TestCard
                    key={test.id}
                    test={test}
                    className={getClassName(test.class_id)}
                    onDelete={() => setDeleteConfirm(test)}
                  />
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Naujas kontrolinis"
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Atšaukti
            </Button>
            <Button onClick={handleSubmit} isLoading={createMutation.isPending}>
              Sukurti
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Pavadinimas
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) =>
                setFormData({ ...formData, title: e.target.value })
              }
              placeholder="pvz. Kontrolinis Nr. 1"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Klasė
              </label>
              <select
                value={formData.class_id}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    class_id: parseInt(e.target.value),
                  })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              >
                <option value={0} disabled>
                  Pasirinkite klasę
                </option>
                {classes?.map((cls) => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Data
              </label>
              <input
                type="date"
                value={formData.test_date}
                onChange={(e) =>
                  setFormData({ ...formData, test_date: e.target.value })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Tema
            </label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) =>
                setFormData({ ...formData, topic: e.target.value })
              }
              placeholder="pvz. Trupmenų sudėtis ir atimtis"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Aprašymas (neprivaloma)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={2}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Ištrinti kontrolinį?"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>
              Atšaukti
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              isLoading={deleteMutation.isPending}
            >
              Ištrinti
            </Button>
          </>
        }
      >
        <p className="text-gray-600">
          Ar tikrai norite ištrinti kontrolinį{" "}
          <strong>{deleteConfirm?.title}</strong>? Bus ištrinti ir visi susiję
          variantai bei užduotys.
        </p>
      </Modal>
    </div>
  );
}

// Test card component
interface TestCardProps {
  test: Test;
  className: string;
  onDelete: () => void;
}

function TestCard({ test, className, onDelete }: TestCardProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("lt-LT", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="group rounded-lg border bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="mb-4 flex items-start justify-between">
        <div className="flex-1">
          <div className="mb-2 flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                statusColors[test.status]
              }`}
            >
              {statusIcons[test.status]}
              {statusLabels[test.status]}
            </span>
          </div>
          <h3 className="font-semibold text-gray-900">{test.title}</h3>
          <p className="text-sm text-gray-500">{className}</p>
        </div>
        <button
          onClick={(e) => {
            e.preventDefault();
            onDelete();
          }}
          className="rounded p-1 text-gray-400 opacity-0 transition-all group-hover:opacity-100 hover:bg-red-50 hover:text-red-600"
          title="Ištrinti"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      <p className="mb-4 line-clamp-1 text-sm text-gray-600">
        {test.topic || "Tema nenurodyta"}
      </p>

      <div className="mb-4 flex items-center gap-4 text-sm text-gray-500">
        <span className="flex items-center gap-1">
          <Calendar className="h-4 w-4" />
          {formatDate(test.test_date)}
        </span>
        <span className="flex items-center gap-1">
          <Award className="h-4 w-4" />
          {test.max_points} tšk.
        </span>
      </div>

      <Link
        to={`/kontroliniai/${test.id}`}
        className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700"
      >
        Atidaryti
        <ChevronRight className="h-4 w-4" />
      </Link>
    </div>
  );
}
