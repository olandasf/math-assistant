/**
 * Klasės puslapis - klasių sąrašas ir valdymas
 */

import { useState } from "react";
import { Users, Plus, Edit, Trash2, GraduationCap } from "lucide-react";
import {
  useClasses,
  useCreateClass,
  useUpdateClass,
  useDeleteClass,
  useActiveSchoolYear,
} from "@/api/hooks";
import type {
  SchoolClass,
  SchoolClassCreate,
  SchoolClassUpdate,
} from "@/api/types";
import {
  PageHeader,
  PageLoader,
  EmptyState,
  Modal,
  Button,
  Card,
  Badge,
  Input,
  Select,
} from "@/components/ui";

export default function ClassesPage() {
  const { data: activeYear } = useActiveSchoolYear();
  const { data: classes, isLoading, error } = useClasses(activeYear?.id);
  const createMutation = useCreateClass();
  const updateMutation = useUpdateClass();
  const deleteMutation = useDeleteClass();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClass, setEditingClass] = useState<SchoolClass | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<SchoolClass | null>(null);

  // Form state
  const [formData, setFormData] = useState<SchoolClassCreate>({
    name: "",
    grade: 5,
    school_year_id: 0,
  });

  const openCreateModal = () => {
    setEditingClass(null);
    setFormData({
      name: "",
      grade: 5,
      school_year_id: activeYear?.id || 0,
    });
    setIsModalOpen(true);
  };

  const openEditModal = (cls: SchoolClass) => {
    setEditingClass(cls);
    setFormData({
      name: cls.name,
      grade: cls.grade,
      school_year_id: cls.school_year_id,
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (editingClass) {
      const update: SchoolClassUpdate = {
        name: formData.name,
        grade: formData.grade,
      };
      await updateMutation.mutateAsync({
        id: editingClass.id,
        payload: update,
      });
    } else {
      await createMutation.mutateAsync(formData);
    }

    setIsModalOpen(false);
  };

  const handleDelete = async () => {
    if (deleteConfirm) {
      await deleteMutation.mutateAsync(deleteConfirm.id);
      setDeleteConfirm(null);
    }
  };

  if (isLoading) {
    return <PageLoader text="Kraunamos klasės..." />;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <div className="p-4 text-red-600">
          Klaida kraunant klases: {error.message}
        </div>
      </Card>
    );
  }

  return (
    <div>
      <PageHeader
        title="Klasės"
        description={
          activeYear
            ? `Mokslo metai: ${activeYear.name}`
            : "Pasirinkite mokslo metus"
        }
        actions={
          <Button onClick={openCreateModal}>
            <Plus className="h-4 w-4 mr-2" />
            Nauja klasė
          </Button>
        }
      />

      {!classes?.length ? (
        <EmptyState
          icon={<GraduationCap className="h-10 w-10" />}
          title="Nėra klasių"
          description="Sukurkite pirmąją klasę, kad galėtumėte pridėti mokinius"
          action={{
            label: "Sukurti klasę",
            onClick: openCreateModal,
          }}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {classes.map((cls) => (
            <div key={cls.id} className="group">
              <Card className="p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-[var(--primary-50)] flex items-center justify-center ring-1 ring-[var(--primary-100)]">
                      <GraduationCap className="w-5 h-5 text-[var(--primary-700)]" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900">
                        {cls.name}
                      </h3>
                      <span className="text-xs text-slate-500">
                        {cls.grade} klasė
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => openEditModal(cls)}
                      className="p-1.5 rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                      title="Redaguoti"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(cls)}
                      className="p-1.5 rounded-md text-slate-500 hover:bg-slate-100 hover:text-[var(--error-600)]"
                      title="Ištrinti"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-sm text-slate-700">
                  <Users className="h-4 w-4 text-[var(--primary-700)]" />
                  <span>{cls.student_count || 0} mokinių</span>
                </div>
              </Card>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingClass ? "Redaguoti klasę" : "Nauja klasė"}
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Atšaukti
            </Button>
            <Button
              onClick={handleSubmit}
              isLoading={createMutation.isPending || updateMutation.isPending}
            >
              {editingClass ? "Išsaugoti" : "Sukurti"}
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Klasės pavadinimas
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="pvz. 5a, 6b, 7c"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Klasės lygis
            </label>
            <select
              value={formData.grade}
              onChange={(e) =>
                setFormData({ ...formData, grade: parseInt(e.target.value) })
              }
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {[5, 6, 7, 8, 9, 10].map((g) => (
                <option key={g} value={g}>
                  {g} klasė
                </option>
              ))}
            </select>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Ištrinti klasę?"
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
          Ar tikrai norite ištrinti klasę <strong>{deleteConfirm?.name}</strong>
          ? Šis veiksmas negrįžtamas.
        </p>
      </Modal>
    </div>
  );
}
